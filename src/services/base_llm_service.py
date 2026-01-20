"""
Base LLM service with shared analysis methods.

This abstract base class contains all shared logic for LLM-based
content analysis, used by both Claude and Mistral service implementations.
"""

import json
import logging
import re
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional
from datetime import datetime

from ..config import settings
from .search_service import SearchService
from .prompt_loader import (
    get_classification_prompt,
    get_political_analysis_prompt,
    get_intent_analysis_prompt,
    get_veracity_prompt
)

logger = logging.getLogger(__name__)

# Constants for veracity analysis
MAX_SEARCH_QUERIES = 8
RESULTS_PER_QUERY = 3
MAX_FILTERED_RESULTS = 5
MIN_SNIPPET_LENGTH = 50
MIN_URL_LENGTH = 5
MIN_WORD_LENGTH_FOR_MATCHING = 3
MIN_RELEVANCE_SCORE = 2
AUTO_MAP_FALLBACK_SOURCES = 2


class BaseLLMService(ABC):
    """Abstract base class for LLM services."""
    
    def __init__(self) -> None:
        self.enabled = False
        self.search_service = SearchService()
        self.web_search_enabled = settings.ENABLE_WEB_SEARCH and self.search_service.enabled
        self._current_search_results: List[Dict] = []
    
    @property
    @abstractmethod
    def service_name(self) -> str:
        """Return the name of this service (e.g., 'Claude', 'Mistral')."""
        pass
    
    @abstractmethod
    def _make_api_call(self, prompt: str, max_retries: int = 3, is_veracity: bool = False) -> str:
        """Make an API call to the LLM provider."""
        pass
    
    def _log_init_status(self) -> None:
        """Log service initialization status."""
        logger.info(f"[INIT] {self.service_name}Service initialized:")
        logger.info(f"[INIT]   {self.service_name} enabled: {self.enabled}")
        logger.info(f"[INIT]   Web search enabled: {self.web_search_enabled}")
        logger.info(f"[INIT]   SearchService enabled: {self.search_service.enabled}")
        logger.info(f"[INIT]   ENABLE_WEB_SEARCH setting: {settings.ENABLE_WEB_SEARCH}")
        if self.enabled:
            logger.info(f"[INIT] {self.service_name} service ready for analysis")
        else:
            logger.warning(f"[INIT] {self.service_name} service DISABLED - API key missing or invalid")

    async def classify_post_type(
        self,
        text: str,
        language: str = "en"
    ) -> Tuple[str, float, Dict[str, float]]:
        if not self.enabled:
            logger.warning(f"{self.service_name} service not enabled, using default classification")
            return self._get_default_classification(language)

        labels = self._get_post_type_labels(language)

        try:
            prompt = get_classification_prompt(text, ', '.join(labels), language)
            response = self._make_api_call(prompt)
            return self._parse_classification_response(response, labels)
        except Exception as e:
            logger.error(f"Error in {self.service_name} classification: {e}")
            return self._get_default_classification(language)

    async def analyze_political_tendency(
        self,
        text: str,
        language: str = "en"
    ) -> Dict[str, float]:
        if not self.enabled:
            logger.warning(f"{self.service_name} service not enabled, using default political analysis")
            return self._get_default_political_analysis(language)

        labels = self._get_political_labels(language)

        try:
            prompt = get_political_analysis_prompt(text, ', '.join(labels), language)
            response = self._make_api_call(prompt)
            return self._parse_political_response(response, labels)
        except Exception as e:
            logger.error(f"Error in {self.service_name} political analysis: {e}")
            return self._get_default_political_analysis(language)

    async def analyze_intents(
        self,
        text: str,
        language: str = "en"
    ) -> Dict[str, float]:
        if not self.enabled:
            logger.warning(f"{self.service_name} service not enabled, using default intent analysis")
            return self._get_default_intent_analysis(language)

        labels = self._get_intent_labels(language)

        try:
            prompt = get_intent_analysis_prompt(text, ', '.join(labels), language)
            response = self._make_api_call(prompt)
            return self._parse_intent_response(response, labels)
        except Exception as e:
            logger.error(f"Error in {self.service_name} intent analysis: {e}")
            return self._get_default_intent_analysis(language)

    async def analyze_veracity(
        self,
        claim: str,
        language: str = "en"
    ) -> Tuple[str, str, str, List[Dict]]:
        logger.info(f"[VERACITY] analyze_veracity called - enabled={self.enabled}, web_search_enabled={self.web_search_enabled}")
        
        if not self.enabled:
            logger.warning(f"[VERACITY] {self.service_name} service not enabled, using default veracity analysis")
            status, justification, method = self._get_default_veracity_analysis(claim, language)
            return status, justification, method, []

        try:
            all_search_results = await self._perform_web_searches(claim, language)
            search_context = self._build_search_context(all_search_results, language)
            
            current_date = datetime.now().strftime("%d. %B %Y" if language == "de" else "%B %d, %Y")
            prompt = get_veracity_prompt(claim, current_date, search_context, language)
            
            logger.debug(f"[VERACITY] Prompt length: {len(prompt)} characters")
            
            logger.info(f"[VERACITY] Sending request to {self.service_name}...")
            response = self._make_api_call(prompt, is_veracity=True)
            logger.info(f"[VERACITY] Received response ({len(response)} characters)")
            
            result = self._parse_veracity_response(response)
            status, justification, verification_method, sources = result
            
            logger.info(f"[VERACITY] Final result: status={status}, sources={len(sources)}")
            
            self._current_search_results = []
            return result

        except Exception as e:
            import traceback
            logger.error(f"[VERACITY] ERROR: {type(e).__name__}: {e}")
            logger.error(f"[VERACITY] Traceback:\n{traceback.format_exc()}")
            status, justification, method = self._get_default_veracity_analysis(claim, language)
            return status, justification, method, []

    async def _perform_web_searches(self, claim: str, language: str) -> List[Dict]:
        """Perform web searches to gather evidence for fact-checking."""
        all_search_results = []
        
        if not self.web_search_enabled:
            logger.error("Web search is DISABLED - veracity analysis will be unreliable!")
            return []
        
        logger.info(f"[VERACITY] Starting analysis for claim: {claim[:100]}")
        
        search_queries = self._extract_all_search_queries(claim, language)
        search_queries.insert(0, claim)
        logger.info(f"[VERACITY] Total queries: {len(search_queries)}")
        
        for i, query in enumerate(search_queries[:MAX_SEARCH_QUERIES], 1):
            logger.info(f"[VERACITY] Search {i}/{min(len(search_queries), MAX_SEARCH_QUERIES)}: {query[:80]}")
            
            if i > 1:
                await asyncio.sleep(0.25)
            
            results = await self.search_service.search(
                query=query,
                count=RESULTS_PER_QUERY,
                language=language
            )
            if results:
                all_search_results.extend(results)
                logger.info(f"[VERACITY] Query {i} returned {len(results)} results")
        
        # Deduplicate by URL
        seen_urls = set()
        unique_results = []
        for result in all_search_results:
            if result.get('url') not in seen_urls:
                seen_urls.add(result.get('url'))
                unique_results.append(result)
        
        logger.info(f"[VERACITY] After deduplication: {len(unique_results)} unique results")
        
        filtered = self._filter_search_results(unique_results, claim, max_results=MAX_FILTERED_RESULTS)
        logger.info(f"[VERACITY] Filtered to {len(filtered)} high-quality results")
        
        return filtered

    def _build_search_context(self, search_results: List[Dict], language: str) -> str:
        """Build search context string for the veracity prompt."""
        if search_results:
            formatted_results = []
            for i, result in enumerate(search_results, 1):
                title = self._sanitize_text(result.get('title', 'N/A'))
                snippet = self._sanitize_text(result.get('snippet', 'N/A'))
                
                formatted_results.append(
                    f"[SOURCE {i}] Title: {title}\n"
                    f"URL: {result.get('url', 'N/A')}\n"
                    f"Snippet: {snippet}"
                )
            search_context = "\n\n=== WEB SEARCH RESULTS ===\n" + "\n\n".join(formatted_results)
            
            self._current_search_results = search_results
            
            if language == "de":
                search_context += "\n\n[OK] Die obigen Web-Suchergebnisse sind deine EINZIGE Informationsquelle."
            else:
                search_context += "\n\n[OK] The above web search results are your ONLY source of information."
        else:
            self._current_search_results = []
            if language == "de":
                search_context = "\n\n[NONE] KEINE WEB-SUCHERGEBNISSE GEFUNDEN\n\nKeine Informationen verfuegbar. Fuer ueberpruefbare Fakten bedeutet dies wahrscheinlich: FALSCH."
            else:
                search_context = "\n\n[NONE] NO WEB SEARCH RESULTS FOUND\n\nNo information available. For verifiable facts, this likely means: FALSE."
        
        return search_context

    def _sanitize_text(self, text: str) -> str:
        """Sanitize text to prevent JSON issues."""
        return text.replace('"', '"').replace('"', '"').replace('"', '"').replace('»', '"').replace('«', '"')

    def _filter_search_results(
        self,
        results: List[Dict],
        claim: str,
        max_results: int = 5
    ) -> List[Dict]:
        """Filter and rank search results by quality and relevance."""
        if not results:
            return []
        
        claim_lower = claim.lower()
        claim_words = set(claim_lower.split())
        
        filtered = []
        skipped_short = 0
        skipped_no_url = 0
        skipped_no_match = 0
        
        for result in results:
            snippet = result.get('snippet', '')
            title = result.get('title', '')
            url = result.get('url', '')
            
            if len(snippet.strip()) < MIN_SNIPPET_LENGTH:
                skipped_short += 1
                continue
            
            if not url or len(url.strip()) < MIN_URL_LENGTH:
                skipped_no_url += 1
                continue
            
            score = 0
            snippet_len = len(snippet)
            if snippet_len >= 100:
                score += 2
            elif snippet_len >= 50:
                score += 1
            
            snippet_lower = snippet.lower()
            title_lower = title.lower()
            
            matching_words = sum(1 for word in claim_words if len(word) > MIN_WORD_LENGTH_FOR_MATCHING and word in snippet_lower)
            if matching_words > 0:
                score += matching_words * 2
            
            title_matches = sum(1 for word in claim_words if len(word) > MIN_WORD_LENGTH_FOR_MATCHING and word in title_lower)
            if title_matches > 0:
                score += title_matches * 3
            
            if score == 0:
                skipped_no_match += 1
                continue
            
            result['_relevance_score'] = score
            filtered.append(result)
        
        logger.info(f"[FILTER] Filtered {len(results)} results: {len(filtered)} accepted, {skipped_short} short, {skipped_no_url} no URL, {skipped_no_match} no match")
        
        filtered.sort(key=lambda x: x.get('_relevance_score', 0), reverse=True)
        
        for result in filtered:
            result.pop('_relevance_score', None)
        
        return filtered[:max_results]
    
    def _extract_all_search_queries(self, claim: str, language: str) -> List[str]:
        """Extract multiple search queries from a claim."""
        queries = []
        claim_lower = claim.lower()
        
        proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', claim)
        
        for name in proper_nouns:
            if len(name) > 3:
                queries.append(name)
                
                if language == "de":
                    if any(title in claim_lower for title in ["bundeskanzler", "kanzler"]):
                        queries.append(f"{name} Bundeskanzler Deutschland")
                        queries.append(f"Bundeskanzler Deutschland aktuell")
                    if any(book in claim_lower for book in ["buch", "autobiografie", "biografie"]):
                        queries.append(f"{name} Buch Autobiografie")
                        queries.append(f"{name} Buch 2024 2025")
                    if "merkel" in name.lower():
                        queries.append("Angela Merkel Autobiografie Freiheit")
                else:
                    if "chancellor" in claim_lower:
                        queries.append(f"{name} Chancellor Germany")
                        queries.append("Germany Chancellor current")
                    if any(book in claim_lower for book in ["book", "autobiography", "biography"]):
                        queries.append(f"{name} book autobiography")
        
        if language == "de":
            if "merz" in claim_lower:
                queries.append("Friedrich Merz Bundeskanzler")
                queries.append("Deutschland Bundeskanzler 2025")
        else:
            if "merz" in claim_lower:
                queries.append("Friedrich Merz Chancellor")
                queries.append("Germany Chancellor 2025")
        
        date_patterns = re.findall(r'\b(2024|2025|2026)\b', claim)
        for date in date_patterns:
            if language == "de":
                queries.append(f"Deutschland Politik {date}")
            else:
                queries.append(f"Germany politics {date}")
        
        seen = set()
        unique_queries = []
        for q in queries:
            if q not in seen and len(q) > 2:
                seen.add(q)
                unique_queries.append(q)
        
        return unique_queries

    def _parse_classification_response(
        self,
        response_text: str,
        labels: List[str]
    ) -> Tuple[str, float, Dict[str, float]]:
        try:
            cleaned = self._clean_json_response(response_text)
            data = json.loads(cleaned)
            primary_label = data.get("primary_label", labels[0])
            confidence = data.get("confidence", 0.5)
            scores = data.get("scores", {})

            for label in labels:
                if label not in scores:
                    scores[label] = 0.0

            return primary_label, confidence, scores

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error parsing classification response: {e}")
            return labels[0], 0.5, {label: 1.0 / len(labels) for label in labels}

    def _parse_political_response(
        self,
        response_text: str,
        labels: List[str]
    ) -> Dict[str, float]:
        try:
            if not response_text:
                logger.error("[POLITICAL] Empty response text received")
                return {label: 1.0 / len(labels) for label in labels}
            
            cleaned = self._clean_json_response(response_text)
            data = json.loads(cleaned)
            scores = data.get("scores", {})

            for label in labels:
                if label not in scores:
                    scores[label] = 0.0

            return scores

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error parsing political response: {e}")
            return {label: 1.0 / len(labels) for label in labels}

    def _parse_intent_response(
        self,
        response_text: str,
        labels: List[str]
    ) -> Dict[str, float]:
        try:
            if not response_text:
                logger.error("[INTENT] Empty response text received")
                return {label: 1.0 / len(labels) for label in labels}
            
            cleaned = self._clean_json_response(response_text)
            data = json.loads(cleaned)
            scores = data.get("scores", {})

            for label in labels:
                if label not in scores:
                    scores[label] = 0.0

            return scores

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error parsing intent response: {e}")
            return {label: 1.0 / len(labels) for label in labels}

    def _clean_json_response(self, response_text: str) -> str:
        """Clean response text to extract valid JSON."""
        cleaned = response_text.strip()
        if cleaned.startswith('```'):
            cleaned = re.sub(r'^```[a-z]*\s*', '', cleaned, flags=re.MULTILINE)
            cleaned = re.sub(r'\s*```\s*$', '', cleaned, flags=re.MULTILINE)
            cleaned = cleaned.strip()
        return cleaned

    def _parse_veracity_response(self, response_text: str) -> Tuple[str, str, str, List[Dict]]:
        """Parse veracity response with multiple JSON extraction strategies."""
        logger.debug(f"[PARSE] Attempting to parse response ({len(response_text)} chars)")
        
        # Strategy 1: Try direct JSON parse
        try:
            data = json.loads(response_text)
            logger.info("[PARSE] Success: Direct JSON parse worked")
        except json.JSONDecodeError:
            logger.warning("[PARSE] Direct JSON parse failed, trying cleanup")
            cleaned = self._clean_json_response(response_text)
            
            # Extract JSON by finding balanced braces
            first_brace = cleaned.find('{')
            if first_brace != -1:
                brace_count = 0
                end_pos = first_brace
                in_string = False
                escape_next = False
                for i in range(first_brace, len(cleaned)):
                    char = cleaned[i]
                    if escape_next:
                        escape_next = False
                        continue
                    if char == '\\':
                        escape_next = True
                        continue
                    if char == '"' and not escape_next:
                        in_string = not in_string
                        continue
                    if not in_string:
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end_pos = i + 1
                                break
                if end_pos > first_brace:
                    cleaned = cleaned[first_brace:end_pos]
                else:
                    last_brace = cleaned.rfind('}')
                    if last_brace > first_brace:
                        cleaned = cleaned[first_brace:last_brace + 1]
            
            try:
                data = json.loads(cleaned)
                logger.info("[PARSE] Success: Cleaned JSON parse worked")
            except json.JSONDecodeError as e:
                logger.warning(f"[PARSE] Cleanup failed: {e}")
                
                try:
                    repaired = self._repair_json_strings(cleaned)
                    data = json.loads(repaired)
                    logger.info("[PARSE] Success: JSON repair worked")
                except (json.JSONDecodeError, Exception):
                    logger.error(f"[PARSE] All strategies failed")
                    return "Unverifiable", "Invalid JSON response from analysis", "Parse error", []
        
        try:
            status = data.get("status", "Unverifiable")
            justification = data.get("justification", "No analysis available")
            verification_method = data.get("verification_method", "Web search")
            sources = data.get("sources", [])
            
            if not isinstance(sources, list):
                sources = []
            else:
                valid_sources = []
                for s in sources:
                    if isinstance(s, dict) and s.get('url'):
                        valid_sources.append({
                            "title": s.get("title", ""),
                            "url": s.get("url", ""),
                            "snippet": s.get("snippet", "")
                        })
                sources = valid_sources
            
            if not sources and self._current_search_results:
                logger.warning("[PARSE] No sources in response, attempting auto-mapping")
                sources = self._auto_map_sources_from_results(justification)
            
            valid_statuses = ["Factually Correct", "Untruth", "Misleading", "Unverifiable"]
            if status not in valid_statuses:
                logger.warning(f"[PARSE] Invalid status '{status}' replaced with 'Unverifiable'")
                status = "Unverifiable"
            
            return status, justification, verification_method, sources
            
        except Exception as e:
            logger.error(f"Error processing parsed data: {e}")
            return "Unverifiable", "Error processing analysis", "Parse error", []

    def _repair_json_strings(self, json_str: str) -> str:
        """Attempt to repair common JSON issues like unescaped quotes."""
        result = []
        i = 0
        in_string = False
        escape_next = False
        
        while i < len(json_str):
            char = json_str[i]
            
            if escape_next:
                result.append(char)
                escape_next = False
                i += 1
                continue
            
            if char == '\\':
                escape_next = True
                result.append(char)
                i += 1
                continue
            
            if char == '"':
                is_value = False
                j = len(result) - 1
                while j >= 0 and result[j] in ' \t\n\r':
                    j -= 1
                if j >= 0:
                    lookback = ''.join(result[max(0, j-3):j+1])
                    if ':' in lookback or lookback.strip().startswith(','):
                        is_value = True
                
                if in_string and is_value:
                    result.append('\\"')
                else:
                    result.append(char)
                    in_string = not in_string
                i += 1
                continue
            
            result.append(char)
            i += 1
        
        return ''.join(result)
    
    def _auto_map_sources_from_results(self, justification: str) -> List[Dict]:
        """Map sources from search results based on justification content."""
        if not self._current_search_results:
            return []
        
        justification_lower = justification.lower()
        mapped_sources = []
        
        justification_words = set(word for word in justification_lower.split() if len(word) > 4)
        
        for result in self._current_search_results:
            snippet_lower = result.get('snippet', '').lower()
            title_lower = result.get('title', '').lower()
            
            relevance = sum(1 for word in justification_words if word in snippet_lower or word in title_lower)
            
            if relevance >= MIN_RELEVANCE_SCORE:
                mapped_sources.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("snippet", "")[:200]
                })
        
        if not mapped_sources and self._current_search_results:
            for result in self._current_search_results[:AUTO_MAP_FALLBACK_SOURCES]:
                mapped_sources.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("snippet", "")[:200]
                })
        
        return mapped_sources

    def _get_post_type_labels(self, language: str) -> List[str]:
        return settings.DE_POST_TYPES if language == "de" else settings.EN_POST_TYPES

    def _get_political_labels(self, language: str) -> List[str]:
        return settings.DE_POLITICAL_LABELS if language == "de" else settings.EN_POLITICAL_LABELS

    def _get_intent_labels(self, language: str) -> List[str]:
        return settings.DE_INTENT_LABELS if language == "de" else settings.EN_INTENT_LABELS

    def _get_default_classification(self, language: str) -> Tuple[str, float, Dict[str, float]]:
        labels = self._get_post_type_labels(language)
        scores = {label: 1.0 / len(labels) for label in labels}
        return labels[0], 1.0 / len(labels), scores

    def _get_default_political_analysis(self, language: str) -> Dict[str, float]:
        labels = self._get_political_labels(language)
        return {label: 1.0 / len(labels) for label in labels}

    def _get_default_intent_analysis(self, language: str) -> Dict[str, float]:
        labels = self._get_intent_labels(language)
        return {label: 1.0 / len(labels) for label in labels}

    def _get_default_veracity_analysis(
        self,
        claim: str,
        language: str
    ) -> Tuple[str, str, str]:
        return "Unverifiable", "Analysis not available", "Default method used"
