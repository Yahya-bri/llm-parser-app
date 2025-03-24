import os
from typing import Dict, Any

# Default configuration settings
DEFAULT_CONFIG = {
    "model": "gemini-2.0-flash",
    "temperature": 0,
    "default_schema": "resume",
    "api_base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
}

# Default prompts for different document types
DEFAULT_PROMPTS = {
    "resume": "You are an AI document extraction specialist. Extract all resume information from this image including personal details, education, work experience, skills, and other relevant sections.",
    "invoice": "You are an AI document extraction specialist. Extract all invoice information from this image including invoice number, date, vendor, line items, amounts, and totals.",
    "receipt": "You are an AI document extraction specialist. Extract all receipt information from this image including merchant, date, items purchased, prices, and total amount.",
    "id_card": "You are an AI document extraction specialist. Extract all information from this ID card including name, ID number, date of birth, and other visible fields.",
}

def get_api_key() -> str:
    """Get the API key from environment variables."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")
    return api_key

def get_schemas_dir() -> str:
    """Get the schemas directory path."""
    # Default to a 'schemas' directory in the same folder as this file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.environ.get("VISION_PARSER_SCHEMAS_DIR", os.path.join(base_dir, "..", "schemas"))
