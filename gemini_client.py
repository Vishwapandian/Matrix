import requests
from typing import Any, Dict, List, Optional

from config import GEMINI_API_KEY, GEMINI_ENDPOINT_TEMPLATE, DEFAULT_MODEL


def generate_content(
    *,
    user_content: str,
    system_instruction: Optional[str] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    tool_config: Optional[Dict[str, Any]] = None,
    model: str = DEFAULT_MODEL,
    generation_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Call the Gemini REST API and return the JSON response.

    Args:
        user_content: Text content representing the prompt or conversation context.
        system_instruction: Optional system-level instruction for the model.
        tools: Optional list of tool/function declarations (for function calling).
        tool_config: Optional tool configuration, e.g. to force a tool call.
        model: Name of the Gemini model to use.
        generation_config: Optional generation configuration dict.

    Returns:
        Parsed JSON response from the API.
    """
    if not GEMINI_API_KEY:
        raise EnvironmentError("GEMINI_API_KEY is not set in the configuration.")

    url = GEMINI_ENDPOINT_TEMPLATE.format(model=model, key=GEMINI_API_KEY)
    headers = {"Content-Type": "application/json"}

    payload: Dict[str, Any] = {
        "contents": [{"parts": [{"text": user_content}]}]
    }

    if system_instruction is not None:
        payload["system_instruction"] = {"parts": [{"text": system_instruction}]}

    if tools is not None:
        payload["tools"] = tools

    if tool_config is not None:
        payload["tool_config"] = tool_config

    if generation_config is not None:
        payload["generationConfig"] = generation_config

    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


__all__ = ["generate_content"] 