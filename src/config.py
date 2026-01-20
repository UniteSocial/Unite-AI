from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )

    ANTHROPIC_API_KEY: str = Field(
        default="",
        description="Anthropic API key for Claude access"
    )
    CLAUDE_MODEL: str = Field(
        default="claude-sonnet-4-5-20250929",
        description="Claude Sonnet 4.5 - latest model optimized for structured JSON output"
    )
    
    MISTRAL_API_KEY: str = Field(
        default="",
        description="Mistral API key for Mistral AI access"
    )
    MISTRAL_MODEL: str = Field(
        default="mistral-large-latest",
        description="Mistral AI model - mistral-large-latest is the most capable model"
    )
    AI_PROVIDER: str = Field(
        default="claude",
        description="AI provider to use: 'claude' or 'mistral'"
    )
    
    BRAVE_API_KEY: str = Field(
        default="",
        description="Brave Search API key for web search"
    )
    ENABLE_WEB_SEARCH: bool = Field(
        default=True,
        description="Enable web search for fact-checking"
    )

    ENABLE_ADVANCED_ANALYSIS: bool = True
    ENABLE_VERACITY_CHECK: bool = True
    ENABLE_NUANCE_ANALYSIS: bool = True

    EN_POST_TYPES: List[str] = [
        "Factual Claim", "Opinion", "Question",
        "Personal Update", "Promotion"
    ]
    DE_POST_TYPES: List[str] = [
        "Faktische Behauptung", "Meinungsäußerung", "Frage",
        "Persönliche Mitteilung", "Werbung / Spam"
    ]

    EN_POLITICAL_LABELS: List[str] = [
        "Left", "Center-Left", "Center",
        "Center-Right", "Right", "Neutral"
    ]
    DE_POLITICAL_LABELS: List[str] = [
        "Politisch Links", "Politisch Mitte-Links", "Politisch Mitte",
        "Politisch Mitte-Rechts", "Politisch Rechts", "Politisch Neutral"
    ]

    EN_INTENT_LABELS: List[str] = [
        "Informative", "Persuasive", "Satirical",
        "Provocative", "Commercial", "Entertaining"
    ]
    DE_INTENT_LABELS: List[str] = [
        "Informativ", "Überzeugend", "Satirisch",
        "Provozierend", "Kommerziell", "Unterhaltend"
    ]

    INTENT_CONFIDENCE_THRESHOLD: float = 0.3
    SPAM_CONFIDENCE_THRESHOLD: float = 0.7

    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000

    USE_LOCAL_LLM: bool = False
    LOCAL_LLM_URL: str = ""
    LOCAL_LLM_MODEL: str = "llama3.2"
    LOCAL_LLM_TIMEOUT: int = 30

    # CORS Configuration - restrict to specific origins in production
    CORS_ALLOWED_ORIGINS: str = Field(
        default="*",
        description="Comma-separated list of allowed CORS origins. Use '*' for development only."
    )
    
    # Logging Configuration
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    LOG_FILE: str = Field(
        default="",
        description="Optional log file path. If empty, logs only to stdout."
    )


settings = Settings()
