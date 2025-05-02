import requests
import json
import argparse
import uuid
import sys
from config import config

def send_chat_request(message, session_id=None, user_id=None, base_url=None):
    """
    Send a chat request to the API and return the response
    """
    if base_url is None:
        base_url = f"http://{config.app.host}:{config.app.port}/api/{config.app.version}"
    
    if session_id is None:
        session_id = str(uuid.uuid4())
    
    if user_id is None:
        user_id = str(uuid.uuid4())
    
    url = f"{base_url}/chat"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": config.app.api_key
    }
    
    payload = {
        "user_message": message,
        "session_identifier": session_id,
        "user_identifier": user_id
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json(), session_id, user_id
    except requests.exceptions.RequestException as e:
        print(f"Error sending request: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return None, session_id, user_id

def interactive_chat(base_url=None):
    """
    Start an interactive chat session with the API
    """
    session_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    print(f"Starting new chat session with ID: {session_id}")
    print(f"User ID: {user_id}")
    print("Type 'exit' to quit the chat")
    
    while True:
        message = input("You: ")
        if message.lower() == 'exit':
            break
        
        response_data, _, _ = send_chat_request(message, session_id, user_id, base_url)
        if response_data:
            print(f"Agent: {response_data.get('bot_message')}")

def main():
    parser = argparse.ArgumentParser(description="Test the Multi-Domain Chatbot API")
    parser.add_argument("--url", help="Base URL of the API (default: from config)")
    parser.add_argument("--message", help="Single message to send (enters interactive mode if not provided)")
    parser.add_argument("--session", help="Session ID to use (generated if not provided)")
    parser.add_argument("--user", help="User ID to use (generated if not provided)")
    
    args = parser.parse_args()
    
    base_url = args.url
    
    if args.message:
        # Single message mode
        response_data, session_id, user_id = send_chat_request(args.message, args.session, args.user, base_url)
        if response_data:
            print(f"Session ID: {session_id}")
            print(f"User ID: {user_id}")
            print(f"Agent: {response_data.get('bot_message')}")
    else:
        # Interactive mode
        interactive_chat(base_url)

if __name__ == "__main__":
    main()
