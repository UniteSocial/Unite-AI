import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timezone
from ..config import settings
from ..models.api_models import (
    PostType, VeracityStatus, PoliticalTendency, Intent,
    PostAnalysis, VeracityAnalysis, PoliticalTendencyAnalysis, NuanceAnalysis
)
from .claude_service import ClaudeService
from .mistral_service import MistralService

logger = logging.getLogger(__name__)
SPAM_LABELS = ["Werbung / Spam", "Promotion"]


class AdvancedEvaluationService:

    def __init__(self) -> None:
        self.claude_service = ClaudeService()
        self.mistral_service = MistralService()
        logger.info("AdvancedEvaluationService initialized")
    
    def _get_ai_service(self):
        """
        Returns the appropriate AI service based on AI_PROVIDER setting.
        Defaults to Claude if provider not set or invalid.
        """
        provider = settings.AI_PROVIDER.lower()
        if provider == "mistral":
            if self.mistral_service.enabled:
                return self.mistral_service
            else:
                logger.warning("Mistral requested but not enabled, falling back to Claude")
                return self.claude_service
        else:
            # Default to Claude
            return self.claude_service

    async def perform_full_analysis(
        self,
        post_id: str,
        post_text: str,
        language: str = "en"
    ) -> Dict:

        processing_error = None

        try:
            post_type, is_spam = await self._run_triage(post_text, language)

            veracity_analysis = await self._get_veracity_analysis(
                post_type, is_spam, post_text, language
            )

            nuance_analysis = await self._get_nuance_analysis(
                is_spam, post_text, language
            )

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Analysis failed for post {post_id}: {e}")
            logger.error(f"Traceback: {error_details}")
            processing_error = f"Analysis failed: {type(e).__name__}: {str(e) if str(e) else repr(e)}"
            return {
                "post_id": post_id,
                "analysis_timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                "language": language,
                "post_analysis": PostAnalysis(
                    post_type=PostType.OPINION,
                    is_spam=False
                ),
                "veracity_analysis": None,
                "nuance_analysis": None,
                "processing_error": processing_error
            }

        return self._build_analysis_response(
            post_id, language, post_type, is_spam,
            veracity_analysis,
            nuance_analysis,
            processing_error
        )

    async def _run_triage(self, text: str, language: str) -> Tuple[PostType, bool]:
        ai_service = self._get_ai_service()
        primary_label, confidence, scores = await ai_service.classify_post_type(
            text, language
        )

        is_spam = self._detect_spam(primary_label, confidence)
        post_type = self._map_to_post_type(primary_label, language)

        logger.info(f"AI triage: {post_type}, spam: {is_spam}, confidence: {confidence:.2f}")
        return post_type, is_spam

    async def _get_veracity_analysis(
        self,
        post_type: PostType,
        is_spam: bool,
        post_text: str,
        language: str
    ) -> Optional[VeracityAnalysis]:

        if not self._should_perform_veracity_check(post_type, is_spam):
            logger.info("Skipping veracity check - not a factual claim or is spam")
            return None

        try:
            ai_service = self._get_ai_service()
            logger.info(f"[EVAL] Starting veracity analysis for post: {post_text[:100]}")
            logger.info(f"[EVAL] Post type: {post_type}, is_spam: {is_spam}")
            status, justification, verification_method, sources = await ai_service.analyze_veracity(
                post_text, language
            )
            logger.info(f"[EVAL] Veracity analysis returned: status={status}, method={verification_method}")
            
            # Validate sources is a list
            if not isinstance(sources, list):
                logger.warning(f"Sources is not a list: {type(sources)}")
                sources = []
            
            # Convert sources to proper format matching Source model
            formatted_sources = []
            for source in sources:
                # Ensure source is a dictionary before accessing with .get()
                if isinstance(source, dict):
                    formatted_sources.append({
                        "title": source.get("title", "Unknown Source"),
                        "url": source.get("url", ""),
                        "snippet": source.get("snippet", "")
                    })
                else:
                    logger.warning(f"Invalid source format (not a dict): {source}")

            return VeracityAnalysis(
                status=self._map_veracity_status(status),
                justification=justification,
                verification_method=verification_method,
                sources=formatted_sources
            )
        except Exception as e:
            logger.error(f"Error in _get_veracity_analysis: {type(e).__name__}: {e}")
            logger.exception("Full traceback:")
            raise  # Re-raise to be caught by outer exception handler

    async def _get_nuance_analysis(
        self,
        is_spam: bool,
        post_text: str,
        language: str
    ) -> Optional[NuanceAnalysis]:

        if is_spam or not settings.ENABLE_NUANCE_ANALYSIS:
            return None

        ai_service = self._get_ai_service()
        political_scores = await ai_service.analyze_political_tendency(
            post_text, language
        )
        intent_scores = await ai_service.analyze_intents(
            post_text, language
        )

        political_analysis = self._build_political_analysis(political_scores, language)
        detected_intents = self._build_intent_list(intent_scores, language)

        return NuanceAnalysis(
            political_tendency=political_analysis,
            detected_intents=detected_intents
        )

    def _should_perform_veracity_check(
        self,
        post_type: PostType,
        is_spam: bool
    ) -> bool:
        return (
            post_type == PostType.FACTUAL_CLAIM
            and not is_spam
            and settings.ENABLE_VERACITY_CHECK
        )

    def _detect_spam(self, primary_label: str, confidence: float) -> bool:
        is_promotion_label = primary_label in SPAM_LABELS
        high_promotion_score = confidence > settings.SPAM_CONFIDENCE_THRESHOLD
        return is_promotion_label and high_promotion_score

    def _build_political_analysis(
        self,
        scores: Dict[str, float],
        language: str
    ) -> PoliticalTendencyAnalysis:
        # Normalize scores to sum to 1.0 for consistency
        total = sum(scores.values())
        normalized_scores = {k: round(v / total, 4) for k, v in scores.items()} if total > 0 else scores
        
        # Simple approach: primary label is the highest scoring category
        primary_label = max(normalized_scores, key=normalized_scores.get)

        return PoliticalTendencyAnalysis(
            primary=self._map_to_political_tendency(primary_label, language),
            scores=normalized_scores
        )

    def _build_intent_list(
        self,
        scores: Dict[str, float],
        language: str
    ) -> List[Intent]:
        detected_intents = [
            intent for intent, score in scores.items()
            if score > settings.INTENT_CONFIDENCE_THRESHOLD
        ]

        return [
            self._map_to_intent(intent, language)
            for intent in detected_intents
        ]

    def _build_analysis_response(
        self,
        post_id: str,
        language: str,
        post_type: PostType,
        is_spam: bool,
        veracity_analysis: Optional[VeracityAnalysis],
        nuance_analysis: Optional[NuanceAnalysis],
        processing_error: Optional[str] = None
    ) -> Dict:

        return {
            "post_id": post_id,
            "analysis_timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "language": language,
            "post_analysis": PostAnalysis(
                post_type=post_type,
                is_spam=is_spam
            ),
            "veracity_analysis": veracity_analysis,
            "nuance_analysis": nuance_analysis,
            "processing_error": processing_error
        }

    def _map_veracity_status(self, status: str) -> VeracityStatus:
        mapping = {
            "Factually Correct": VeracityStatus.FACTUALLY_CORRECT,
            "Untruth": VeracityStatus.UNTRUTH,
            "Misleading": VeracityStatus.MISLEADING,
            "Unverifiable": VeracityStatus.UNVERIFIABLE
        }
        return mapping.get(status, VeracityStatus.UNVERIFIABLE)

    def _map_to_post_type(self, label: str, language: str) -> PostType:
        mapping = {
            "Factual Claim": PostType.FACTUAL_CLAIM,
            "Faktische Behauptung": PostType.FACTUAL_CLAIM,
            "Opinion": PostType.OPINION,
            "Meinungsäußerung": PostType.OPINION,
            "Question": PostType.QUESTION,
            "Frage": PostType.QUESTION,
            "Personal Update": PostType.PERSONAL_UPDATE,
            "Persönliche Mitteilung": PostType.PERSONAL_UPDATE,
            "Promotion": PostType.PROMOTION,
            "Werbung / Spam": PostType.PROMOTION
        }
        return mapping.get(label, PostType.OPINION)

    def _map_to_political_tendency(
        self,
        label: str,
        language: str
    ) -> PoliticalTendency:
        mapping = {
            "Left": PoliticalTendency.LEFT,
            "Politisch Links": PoliticalTendency.LEFT,
            "Center-Left": PoliticalTendency.CENTER_LEFT,
            "Politisch Mitte-Links": PoliticalTendency.CENTER_LEFT,
            "Center": PoliticalTendency.CENTER,
            "Politisch Mitte": PoliticalTendency.CENTER,
            "Center-Right": PoliticalTendency.CENTER_RIGHT,
            "Politisch Mitte-Rechts": PoliticalTendency.CENTER_RIGHT,
            "Right": PoliticalTendency.RIGHT,
            "Politisch Rechts": PoliticalTendency.RIGHT,
            "Neutral": PoliticalTendency.NEUTRAL,
            "Politisch Neutral": PoliticalTendency.NEUTRAL
        }
        return mapping.get(label, PoliticalTendency.NEUTRAL)

    def _map_to_intent(self, label: str, language: str) -> Intent:
        mapping = {
            "Informative": Intent.INFORMATIVE,
            "Informativ": Intent.INFORMATIVE,
            "Persuasive": Intent.PERSUASIVE,
            "Überzeugend": Intent.PERSUASIVE,
            "Satirical": Intent.SATIRICAL,
            "Satirisch": Intent.SATIRICAL,
            "Provocative": Intent.PROVOCATIVE,
            "Provozierend": Intent.PROVOCATIVE,
            "Commercial": Intent.COMMERCIAL,
            "Kommerziell": Intent.COMMERCIAL,
            "Entertaining": Intent.ENTERTAINING,
            "Unterhaltend": Intent.ENTERTAINING
        }
        return mapping.get(label, Intent.INFORMATIVE)
