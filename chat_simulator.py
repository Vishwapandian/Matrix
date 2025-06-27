"""Social Dynamics Simulator via Group Chat.

Usage:
    $ export GEMINI_API_KEY=<your_key>
    $ python chat_simulator.py

The script will prompt the human user to send messages into the chat. Each user
message triggers the conversation manager (after a 5-second delay). The manager
selects which AI actors (Evie, Auri, Puck) should respond. The simulator
calls the Gemini model separately for each selected actor, rotating the system
prompt to match the actor being simulated. Responses are appended to chat and
printed to the console. The cycle repeats automatically.
"""

import json
import time
from typing import Any, Dict, List, TypedDict

from dotenv import load_dotenv
load_dotenv()

from gemini_client import generate_content
from config import MANAGER_DELAY_SEC, MAX_MANAGER_CYCLES
from prompts import (
    AI_ACTORS,
    MANAGER_SYSTEM_PROMPT,
    MANAGER_FUNCTION_NAME,
    MANAGER_FUNCTION_DECLARATION,
)
from tools import ChatMessage, render_chat, call_ai_actor

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Conversation Manager Logic
# ---------------------------------------------------------------------------

def call_conversation_manager(chat_history: List[ChatMessage]) -> List[str]:
    """Invoke Gemini as the conversation manager to select next AI actors.

    Returns a list of actor IDs (subset of AI_ACTORS keys) that should reply
    next. The list can be empty if no actor should speak.
    """
    chat_context = render_chat(chat_history)

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
    function_call = candidate.get("functionCall")
    if not function_call:
        print("[Manager] No function call detected; defaulting to no actors.")
        return []

    if function_call.get("name") != MANAGER_FUNCTION_NAME:
        print(f"[Manager] Unexpected function call: {function_call.get('name')}")
        return []

    args = function_call.get("args", {})
    actors = args.get("actors", [])
    
    # Filter to known actor IDs and deduplicate.
    return [a for a in dict.fromkeys(actors) if a in AI_ACTORS]


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
                replies = call_ai_actor(actor_id, chat_history)
                for reply in replies:
                    chat_history.append({"actor": actor_id, "text": reply})
                    print(f"{actor_id.capitalize()}: {reply}\n")

            # Delay before manager checks again.
            time.sleep(MANAGER_DELAY_SEC)


if __name__ == "__main__":
    main() 