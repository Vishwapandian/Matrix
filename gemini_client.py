import os
import requests
from typing import Any, Dict, List, Optional

#GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_KEY = "AIzaSyDZPtUp1UMlJu2qzpDm0fO2NPDeB1d9s9w"
if not GEMINI_API_KEY:
    raise EnvironmentError("GEMINI_API_KEY environment variable not set.")

GEMINI_ENDPOINT_TEMPLATE = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
)

# Default model to use
DEFAULT_MODEL = "gemini-2.0-flash"


def generate_content(
    *,
    user_content: str,
    system_instruction: Optional[str] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    model: str = DEFAULT_MODEL,
    generation_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Call the Gemini REST API and return the JSON response.

    Args:
        user_content: Text content representing the prompt or conversation context.
        system_instruction: Optional system-level instruction for the model.
        tools: Optional list of tool/function declarations (for function calling).
        model: Name of the Gemini model to use.
        generation_config: Optional generation configuration dict.

    Returns:
        Parsed JSON response from the API.
    """

    url = GEMINI_ENDPOINT_TEMPLATE.format(model=model, key=GEMINI_API_KEY)
    headers = {"Content-Type": "application/json"}

    payload: Dict[str, Any] = {
        "contents": [{"parts": [{"text": user_content}]}]
    }

    if system_instruction is not None:
        payload["system_instruction"] = {"parts": [{"text": system_instruction}]}

    if tools is not None:
        payload["tools"] = tools

    if generation_config is not None:
        payload["generationConfig"] = generation_config

    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


__all__ = ["generate_content", "DEFAULT_MODEL"] 