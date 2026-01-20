"""
Mistral AI LLM service implementation.

This service extends BaseLLMService with Mistral-specific API integration.
"""

import logging
import time
from mistralai import Mistral

from ..config import settings
from .base_llm_service import BaseLLMService

logger = logging.getLogger(__name__)


class MistralService(BaseLLMService):
    """Mistral API service for content analysis."""

    def __init__(self) -> None:
        super().__init__()
        
        if not settings.MISTRAL_API_KEY:
            logger.warning("No Mistral API key provided. Mistral analysis will be disabled.")
            self.client = None
            self.enabled = False
        else:
            self.client = Mistral(api_key=settings.MISTRAL_API_KEY)
            self.enabled = True
        
        self._log_init_status()

    @property
    def service_name(self) -> str:
        return "Mistral"

    def _make_api_call(self, prompt: str, max_retries: int = 3, is_veracity: bool = False) -> str:
        for attempt in range(max_retries):
            try:
                max_tokens = 4096 if is_veracity else 1000
                temperature = 0.1
                
                logger.debug(f"[API] Calling Mistral model: {settings.MISTRAL_MODEL}, max_tokens: {max_tokens}")
                
                response = self.client.chat.complete(
                    model=settings.MISTRAL_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                if not response.choices or len(response.choices) == 0:
                    logger.error("[API] Mistral returned empty response choices")
                    raise ValueError("Empty response from Mistral API")
                
                response_text = response.choices[0].message.content
                if not response_text:
                    logger.error("[API] Mistral returned empty text in response")
                    raise ValueError("Empty text in Mistral API response")
                
                logger.debug(f"[API] Response length: {len(response_text)} chars")
                return response_text

            except Exception as e:
                logger.warning(f"API call attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise e
