"""
Prompt loader for Unite-I system prompts.

Loads prompts from the prompts/ directory, enabling transparency
and auditability of AI instructions.
"""

import os
import logging
from typing import Dict
from functools import lru_cache

logger = logging.getLogger(__name__)

PROMPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'prompts')


@lru_cache(maxsize=16)
def load_prompt(name: str, language: str = "en") -> str:
    """
    Load a prompt template from file.
    
    Args:
        name: Prompt name (classification, political_analysis, intent_analysis, veracity)
        language: Language code (en, de)
        
    Returns:
        Prompt template string with placeholders
    """
    filename = f"{name}_{language}.txt"
    filepath = os.path.join(PROMPTS_DIR, filename)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"Prompt file not found: {filepath}")
        raise
    except Exception as e:
        logger.error(f"Error loading prompt {filename}: {e}")
        raise


def get_classification_prompt(text: str, labels: str, language: str = "en") -> str:
    """Build classification prompt with variables filled."""
    template = load_prompt("classification", language)
    return template.format(text=text, labels=labels)


def get_political_analysis_prompt(text: str, labels: str, language: str = "en") -> str:
    """Build political analysis prompt with variables filled."""
    template = load_prompt("political_analysis", language)
    return template.format(text=text, labels=labels)


def get_intent_analysis_prompt(text: str, labels: str, language: str = "en") -> str:
    """Build intent analysis prompt with variables filled."""
    template = load_prompt("intent_analysis", language)
    return template.format(text=text, labels=labels)


def get_veracity_prompt(claim: str, current_date: str, search_context: str, language: str = "en") -> str:
    """Build veracity prompt with variables filled."""
    template = load_prompt("veracity", language)
    return template.format(claim=claim, current_date=current_date, search_context=search_context)


def get_available_prompts() -> Dict[str, list]:
    """List all available prompts by category."""
    prompts = {}
    if os.path.exists(PROMPTS_DIR):
        for filename in os.listdir(PROMPTS_DIR):
            if filename.endswith('.txt'):
                name = filename.rsplit('_', 1)[0]
                if name not in prompts:
                    prompts[name] = []
                lang = filename.rsplit('_', 1)[1].replace('.txt', '')
                prompts[name].append(lang)
    return prompts
