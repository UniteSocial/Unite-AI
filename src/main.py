"""
Unite-I - Open Source Fact-Checking Service

A multi-stage analysis service for evaluating social media content
using LLM-powered analysis with web search verification.

https://github.com/UniteSocial/Unite-I
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .config import settings
from .models.api_models import (
    SocialMediaPostRequest,
    AdvancedEvaluationResponse,
    HealthResponse
)
from .services.evaluation_service import AdvancedEvaluationService

# Configure logging
log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

handlers = [logging.StreamHandler()]

# Only create file handler if LOG_FILE is explicitly set
log_file = os.environ.get('LOG_FILE')
if log_file:
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    handlers.append(logging.FileHandler(log_file, mode='a'))

logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format=log_format,
    handlers=handlers
)
logger = logging.getLogger(__name__)

VERSION = "2.0.0"

app_state = {}

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app_state["evaluation_service"] = AdvancedEvaluationService()
    logger.info("Unite-I service started")
    yield
    app_state.clear()
    logger.info("Unite-I service stopped")


def get_evaluation_service() -> AdvancedEvaluationService:
    return app_state["evaluation_service"]


def create_app() -> FastAPI:
    app = FastAPI(
        title="Unite-I",
        description="Open-source AI-powered fact-checking and content analysis service",
        version=VERSION,
        lifespan=lifespan
    )
    
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    cors_origins = settings.CORS_ALLOWED_ORIGINS.split(",") if settings.CORS_ALLOWED_ORIGINS != "*" else ["*"]
    cors_origins = [origin.strip() for origin in cors_origins]
    
    if cors_origins == ["*"]:
        logger.warning("CORS allows all origins. Restrict in production!")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )
    
    return app


app = create_app()


@app.get("/", response_model=HealthResponse, tags=["Health"])
@limiter.limit("30/minute")
async def root(request: Request) -> HealthResponse:
    service = get_evaluation_service()
    test_result = await service.perform_full_analysis("health", "test", "en")

    return HealthResponse(
        status="operational",
        timestamp=test_result["analysis_timestamp"],
        version=VERSION
    )


@app.post("/evaluate", response_model=AdvancedEvaluationResponse, tags=["Analysis"])
@limiter.limit("10/minute")
async def evaluate_content(request: Request, body: SocialMediaPostRequest) -> AdvancedEvaluationResponse:
    try:
        service = get_evaluation_service()
        result = await service.perform_full_analysis(
            post_id=body.post_id,
            post_text=body.post_text,
            language=body.language
        )
        return AdvancedEvaluationResponse(**result)
    except Exception as e:
        logger.error(f"Error processing evaluation request: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Analysis failed. Please try again later."
        )


@app.get("/config", tags=["Configuration"])
@limiter.limit("30/minute")
def get_config(request: Request) -> dict:
    """Get service configuration (non-sensitive only)."""
    service = get_evaluation_service()
    claude_service = service.claude_service
    mistral_service = service.mistral_service
    
    return {
        "version": VERSION,
        "enable_advanced_analysis": settings.ENABLE_ADVANCED_ANALYSIS,
        "enable_veracity_check": settings.ENABLE_VERACITY_CHECK,
        "enable_nuance_analysis": settings.ENABLE_NUANCE_ANALYSIS,
        "enable_web_search": settings.ENABLE_WEB_SEARCH,
        "ai_provider": settings.AI_PROVIDER,
        "claude_model": settings.CLAUDE_MODEL,
        "claude_enabled": claude_service.enabled,
        "mistral_model": settings.MISTRAL_MODEL,
        "mistral_enabled": mistral_service.enabled,
        "web_search_enabled": claude_service.web_search_enabled,
    }
