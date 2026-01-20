"""
Claude (Anthropic) LLM service implementation.

This service extends BaseLLMService with Claude-specific API integration.
"""

import logging
import time
from anthropic import Anthropic

from ..config import settings
from .base_llm_service import BaseLLMService

logger = logging.getLogger(__name__)


class ClaudeService(BaseLLMService):
    """Claude API service for content analysis."""

    def __init__(self) -> None:
        super().__init__()
        
        if not settings.ANTHROPIC_API_KEY:
            logger.warning("No Anthropic API key provided. Claude analysis will be disabled.")
            self.client = None
            self.enabled = False
        else:
            self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            self.enabled = True
        
        self._log_init_status()

    @property
    def service_name(self) -> str:
        return "Claude"

    def _make_api_call(self, prompt: str, max_retries: int = 3, is_veracity: bool = False) -> str:
        for attempt in range(max_retries):
            try:
                max_tokens = 4096 if is_veracity else 1000
                temperature = 0.1
                
                logger.debug(f"[API] Calling Claude model: {settings.CLAUDE_MODEL}, max_tokens: {max_tokens}")
                
                response = self.client.messages.create(
                    model=settings.CLAUDE_MODEL,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                if not response.content or len(response.content) == 0:
                    logger.error("[API] Claude returned empty response content")
                    raise ValueError("Empty response from Claude API")
                
                response_text = response.content[0].text
                if not response_text:
                    logger.error("[API] Claude returned empty text in response")
                    raise ValueError("Empty text in Claude API response")
                
                logger.debug(f"[API] Response length: {len(response_text)} chars")
                return response_text

            except Exception as e:
                logger.warning(f"API call attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise e
