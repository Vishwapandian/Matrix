"""Prompts for the Social Dynamics Chat Simulator."""

from typing import Dict

# --- Actor Definitions ---
# I've added a bit more personality to each character based on common knowledge.
AI_ACTORS: Dict[str, str] = {
    "alvin": "You are Alvin from Alvin and the Chipmunks. You are mischievous, impulsive, and the charismatic leader of the group.",
    "simon": "You are Simon from Alvin and the Chipmunks. You are the intelligent, witty, and responsible one with glasses.",
    "theodore": "You are Theodore from Alvin and the Chipmunks. You are sweet, shy, naive, and very fond of snacks.",
}

# --- Conversation Manager Prompts and Configuration ---
MANAGER_SYSTEM_PROMPT = (
    "You are the conversation manager. Your role is to analyze the ongoing "
    "conversation and decide which of the AI actors should speak next. "
    "Use the `select_actors` function to specify who should speak. "
    "If the conversation has reached a natural stopping point or if no one "
    "needs to respond, call the function with an empty list of actors."
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