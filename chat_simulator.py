"""Social Dynamics Simulator via Group Chat.

Usage:
    $ export GEMINI_API_KEY=<your_key>
    $ python chat_simulator.py

The script will prompt the human user to send messages into the chat. Each user
message triggers the conversation manager (after a 5-second delay). The manager
selects which AI actors (Alvin, Simon, Theodore) should respond. The simulator
calls the Gemini model separately for each selected actor, rotating the system
prompt to match the actor being simulated. Responses are appended to chat and
printed to the console. The cycle repeats automatically.
"""

import json
import time
from typing import Any, Dict, List

from dotenv import load_dotenv
load_dotenv()

from gemini_client import generate_content

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

AI_ACTORS: Dict[str, str] = {
    "alvin": "You are Alvin from Alvin and the Chipmunks",
    "simon": "You are Simon from Alvin and the Chipmunks",
    "theodore": "You are Theodore from Alvin and the Chipmunks",
}

MANAGER_SYSTEM_PROMPT = (
    "You are the conversation manager, you will call the appropriate person to "
    "talk based on the chat state. Return a function call selecting which AI "
    "actors should respond. If no one should respond, return an empty list."
)

# Name of the custom tool the manager should invoke via function calling.
MANAGER_FUNCTION_NAME = "select_actors"

# Function declaration passed to Gemini for the manager call.
MANAGER_FUNCTION_DECLARATION = {
    "name": MANAGER_FUNCTION_NAME,
    "description": "Select which AI actors should speak next based on the current chat state.",
    "parameters": {
        "type": "object",
        "properties": {
            "actors": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": list(AI_ACTORS.keys()),
                },
                "description": "List of actor IDs that should speak next."
            }
        },
        "required": ["actors"],
    },
}

# Delay (in seconds) between a chat update and the manager being triggered.
MANAGER_DELAY_SEC = 5

# Maximum number of manager cycles triggered automatically after each user
# message (to avoid infinite loops in pathological scenarios).
MAX_MANAGER_CYCLES = 10


# ---------------------------------------------------------------------------
# Chat State Helpers
# ---------------------------------------------------------------------------

ChatMessage = Dict[str, str]  # {"actor": str, "text": str}


def render_chat(chat: List[ChatMessage]) -> str:
    """Render chat history as plain text lines for model context."""
    return "\n".join(f"{m['actor']}: {m['text']}" for m in chat)


# ---------------------------------------------------------------------------
# Conversation Manager Logic
# ---------------------------------------------------------------------------

def call_conversation_manager(chat: List[ChatMessage]) -> List[str]:
    """Invoke Gemini as the conversation manager to select next AI actors.

    Returns a list of actor IDs (subset of AI_ACTORS keys) that should reply
    next. The list can be empty if no actor should speak.
    """
    chat_context = render_chat(chat)

    response = generate_content(
        user_content=chat_context,
        system_instruction=MANAGER_SYSTEM_PROMPT,
        tools=[{"functionDeclarations": [MANAGER_FUNCTION_DECLARATION]}],
    )

    try:
        candidate = response["candidates"][0]["content"]["parts"][0]
    except (KeyError, IndexError):
        print("[Manager] Unexpected response structure; defaulting to no actors.")
        return []

    # Expecting a function call.
    function_call = candidate.get("functionCall")  # type: ignore[arg-type]
    if not function_call:
        print("[Manager] No function call detected; defaulting to no actors.")
        return []

    if function_call.get("name") != MANAGER_FUNCTION_NAME:
        print(f"[Manager] Unexpected function call: {function_call.get('name')}")
        return []

    args_raw = function_call.get("args")
    try:
        args = json.loads(args_raw) if isinstance(args_raw, str) else args_raw
        actors = args.get("actors", []) if isinstance(args, dict) else []
    except json.JSONDecodeError:
        print("[Manager] Failed to parse function call args; defaulting to no actors.")
        return []

    # Filter to known actor IDs and deduplicate.
    return [a for a in dict.fromkeys(actors) if a in AI_ACTORS]


# ---------------------------------------------------------------------------
# AI Actor Logic
# ---------------------------------------------------------------------------

def call_ai_actor(actor_id: str, chat: List[ChatMessage]) -> str:
    """Invoke Gemini pretending to be a specific AI actor to generate a reply."""
    system_instruction = AI_ACTORS[actor_id]
    chat_context = render_chat(chat)

    response = generate_content(
        user_content=chat_context,
        system_instruction=system_instruction,
    )

    try:
        # Extract first candidate text.
        parts = response["candidates"][0]["content"]["parts"]
        # Concatenate all text parts.
        text = " ".join(p.get("text", "") for p in parts if "text" in p).strip()
        return text
    except (KeyError, IndexError):
        return "(Error: actor response unavailable)"


# ---------------------------------------------------------------------------
# Main Loop
# ---------------------------------------------------------------------------

def main() -> None:
    print("=== Social Dynamics Chat Simulator ===")
    print("Type a message and press Enter to send. Type 'quit' to exit.\n")

    chat_history: List[ChatMessage] = []

    while True:
        user_msg = input("You: ").strip()
        if user_msg.lower() in {"quit", "exit"}:
            print("Exiting.")
            break

        # Append human message.
        chat_history.append({"actor": "human", "text": user_msg})

        # Trigger conversation manager after delay.
        time.sleep(MANAGER_DELAY_SEC)
        cycles = 0
        while cycles < MAX_MANAGER_CYCLES:
            cycles += 1

            next_actors = call_conversation_manager(chat_history)
            if not next_actors:
                break  # Manager elected no one to speak now.

            for actor_id in next_actors:
                reply = call_ai_actor(actor_id, chat_history)
                chat_history.append({"actor": actor_id, "text": reply})
                print(f"{actor_id.capitalize()}: {reply}\n")

            # Delay before manager checks again.
            time.sleep(MANAGER_DELAY_SEC)


if __name__ == "__main__":
    main() 