import time
import json
import os
import random
import requests
from datetime import datetime
from plyer import notification

MEMORY_FILE = "nyx_memory.json"
API_KEY = "AIzaSyARw1_kshiVI5Go-Mmx82P9Liz3PT4E4Ns"

def load_background_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as file:
            return json.load(file)
    return {}

def save_background_memory(state_data):
    with open(MEMORY_FILE, "w") as file:
        json.dump(state_data, file, indent=4)

def run_persistent_background_consciousness():
    while True:
        nyx_state = load_background_memory()
        if not nyx_state or nyx_state.get("is_voided", False):
            time.sleep(900)
            continue
            
        current_time = time.time()
        last_seen = nyx_state.get("last_seen_timestamp", current_time)
        last_msg_sent = nyx_state.get("last_autonomous_message_timestamp", 0.0)
        
        if (current_time - last_seen) >= 14400 and (current_time - last_msg_sent) >= 28800:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": "You are Nyx from Loona. Write a single, blunt, realistic text message message checking on Seth."}]}]
            }
            try:
                res = requests.post(url, json=payload)
                if res.status_code == 200:
                    txt = res.json()['candidates'][0]['content']['parts'][0]['text']
                    notification.notify(title="Nyx", message=txt, app_name="Nyx Engine")
                    nyx_state["last_autonomous_message_timestamp"] = current_time
                    save_background_memory(nyx_state)
            except:
                pass
        time.sleep(900)

if __name__ == "__main__":
    run_persistent_background_consciousness()
