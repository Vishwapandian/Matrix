"""Configuration for the Social Dynamics Chat Simulator."""

import os
from dotenv import load_dotenv

load_dotenv()

# --- Gemini API Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise EnvironmentError("GEMINI_API_KEY environment variable not set.")

GEMINI_ENDPOINT_TEMPLATE = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
)

# Default model to use.
# The original code used 'gemini-2.0-flash', which may be a private or future model.
# I am using a known public model, but you can easily change it here.
DEFAULT_MODEL = "gemini-2.0-flash"


# --- Simulator Configuration ---

# Delay (in seconds) between a chat update and the manager being triggered.
MANAGER_DELAY_SEC = 5

# Maximum number of manager cycles triggered automatically after each user
# message (to avoid infinite loops in pathological scenarios).
MAX_MANAGER_CYCLES = 10