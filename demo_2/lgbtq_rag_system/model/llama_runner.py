import requests
from google.auth import default
from google.auth.transport.requests import Request
import json
from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

# Set your endpoint details
DEDICATED_DNS = os.getenv("DEDICATED_DNS")

# Function to get access token
def get_access_token():
    creds, _ = default()
    creds.refresh(Request())
    return creds.token


def run_llm(prompt):
    headers = {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json"
    }

    payload = {
        "instances": [
            {
                "@requestFormat": "chatCompletions",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 1000
            }
        ]
    }

    response = requests.post(DEDICATED_DNS, headers=headers, json=payload)
    
    if response.status_code == 200:
        try:
            data = response.json()
            # Safely access the response message content
            message = data.get("predictions", {}).get("choices", [])[0].get("message", {}).get("content", "")
            return message
        except (json.JSONDecodeError, IndexError, KeyError) as e:
            print(f"⚠️ Error parsing response: {e}")
            return "⚠️ Error: Unable to parse LLM response."
    else:
        print(f"⚠️ Error in LLM request: {response.status_code} - {response.text}")
        return f"⚠️ Error: LLM request failed with status {response.status_code}."