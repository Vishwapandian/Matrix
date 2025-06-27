"""Tools for the Social Dynamics Chat Simulator."""

from typing import Any, Dict, List, TypedDict

from gemini_client import generate_content
from prompts import AI_ACTORS

# --- Tool Definitions ---

SEND_MESSAGE_TOOL_NAME = "send_message"

SEND_MESSAGE_DECLARATION = {
    "name": SEND_MESSAGE_TOOL_NAME,
    "description": "Sends a message to the group chat.",
    "parameters": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "The content of the message to send.",
            },
        },
        "required": ["message"],
    },
}

ACTOR_TOOLS: List[Dict[str, Any]] = [
    {"function_declarations": [SEND_MESSAGE_DECLARATION]}
]

# --- Chat-related Types and Helpers ---

class ChatMessage(TypedDict):
    actor: str
    text: str


def render_chat(chat: List[ChatMessage]) -> str:
    """Render chat history as plain text lines for model context."""
    return "\n".join(f"{m['actor']}: {m['text']}" for m in chat)

# --- AI Actor Logic ---

def call_ai_actor(actor_id: str, chat_history: List[ChatMessage]) -> List[str]:
    """Call the Gemini API for a given AI actor and get message(s) from tool calls."""
    system_prompt = AI_ACTORS[actor_id]
    user_prompt = render_chat(chat_history)

    tool_config = {
        "function_calling_config": {
            "mode": "ANY",
            "allowed_function_names": [SEND_MESSAGE_TOOL_NAME],
        }
    }

    response_json = generate_content(
        system_instruction=system_prompt,
        user_content=user_prompt,
        tools=ACTOR_TOOLS,
        tool_config=tool_config,
    )

    messages = []
    try:
        parts = response_json["candidates"][0]["content"]["parts"]
        for part in parts:
            if "functionCall" in part:
                function_call = part["functionCall"]
                if function_call["name"] == SEND_MESSAGE_TOOL_NAME:
                    message = function_call["args"].get("message", "")
                    if message:
                        messages.append(message.strip())
    except (KeyError, IndexError, TypeError) as e:
        print(f"Error parsing response for {actor_id}: {e}")
        # Consider logging the full response_json here for debugging
        return []

    return messages 