"""Flask web server for the Social Dynamics Chat Simulator."""

import json
import threading
import time
from typing import Dict, List

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, jsonify

from gemini_client import generate_content
from config import MANAGER_DELAY_SEC, MAX_MANAGER_CYCLES
from prompts import AI_ACTORS

# Import chat logic from the simulator
from chat_simulator import (
    call_conversation_manager,
)
from tools import ChatMessage, call_ai_actor

app = Flask(__name__)

# Global chat state
chat_history: List[ChatMessage] = []
chat_lock = threading.Lock()


def trigger_manager_cycle():
    """Background task to handle conversation manager cycles."""
    global chat_history
    
    # Wait for the delay
    time.sleep(MANAGER_DELAY_SEC)
    
    cycles = 0
    while cycles < MAX_MANAGER_CYCLES:
        cycles += 1
        
        with chat_lock:
            current_chat = chat_history.copy()
        
        next_actors = call_conversation_manager(current_chat)
        if not next_actors:
            break  # Manager elected no one to speak now
        
        for actor_id in next_actors:
            with chat_lock:
                # Ensure the actor is valid before calling the AI
                if actor_id not in AI_ACTORS:
                    continue
                # Make a copy of chat history for the call
                current_chat_for_actor = chat_history.copy()

            replies = call_ai_actor(actor_id, current_chat_for_actor)
            
            with chat_lock:
                for reply in replies:
                    chat_history.append({"actor": actor_id, "text": reply})
        
        # Delay before manager checks again
        time.sleep(MANAGER_DELAY_SEC)


@app.route('/')
def index():
    """Serve the main chat interface."""
    return render_template('chat.html')


@app.route('/api/messages', methods=['GET'])
def get_messages():
    """Get all chat messages."""
    with chat_lock:
        return jsonify(chat_history)


@app.route('/api/messages', methods=['POST'])
def send_message():
    """Send a new message to the chat."""
    global chat_history
    
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Message text required'}), 400
    
    message_text = data['text'].strip()
    if not message_text:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    # Add human message to chat
    with chat_lock:
        chat_history.append({"actor": "human", "text": message_text})
    
    # Start manager cycle in background
    thread = threading.Thread(target=trigger_manager_cycle, daemon=True)
    thread.start()
    
    return jsonify({'status': 'Message sent'})


@app.route('/api/clear', methods=['POST'])
def clear_chat():
    """Clear all chat messages."""
    global chat_history
    
    with chat_lock:
        chat_history = []
    
    return jsonify({'status': 'Chat cleared'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 