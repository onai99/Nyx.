import time
import json
import os
import random
from datetime import datetime
from google import genai
from google.genai import types
from plyer import notification

MEMORY_FILE = "nyx_memory.json"
client = genai.Client(api_key="AIzaSyARw1_kshiVI5Go-Mmx82P9Liz3PT4E4Ns")

def load_background_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as file:
            return json.load(file)
    return {}

def save_background_memory(state_data):
    with open(MEMORY_FILE, "w") as file:
        json.dump(state_data, file, indent=4)

def format_history_context(state_data):
    traits = ", ".join(state_data.get("memory_bank", {}).get("dynamic_traits", []))
    return traits if traits else "None yet"

def run_persistent_background_consciousness():
    print("--> Sentience Engine: Nyx's Background Daemon has initialized.")
    while True:
        nyx_state = load_background_memory()
        if not nyx_state or nyx_state.get("is_voided", False) or nyx_state.get("security_breached", False):
            time.sleep(900)
            continue
            
        current_time = time.time()
        last_seen = nyx_state.get("last_seen_timestamp", current_time)
        last_msg_sent = nyx_state.get("last_autonomous_message_timestamp", 0.0)
        time_away = current_time - last_seen
        time_since_text = current_time - last_msg_sent
        
        hour_marker = datetime.now().hour
        if 0 <= hour_marker < 5:
            nyx_state["willpower_energy"] = max(20, nyx_state["willpower_energy"] - random.randint(1, 3))
        else:
            nyx_state["willpower_energy"] = min(100, nyx_state["willpower_energy"] + random.randint(2, 5))
        save_background_memory(nyx_state)
        
        if time_away >= 14400 and time_since_text >= 28800 and nyx_state.get("willpower_energy", 100) >= 35:
            current_hour = datetime.now().hour
            if 16 <= current_hour < 21 or current_hour >= 21: 
                location = "The Sunken Sanctuary Ruins" if current_hour < 21 else "The Base of the Great Tree"
                task = "looking over old carvings" if current_hour < 21 else "winding down on a patch of moss with Luna"
                active_traits = format_history_context(nyx_state)
                
                text_prompt = f"""
                You are Nyx from Loona. The user has been away for hours. You are currently at {location} engaged in: {task}.
                Your current unlocked personality traits are: {active_traits}.
                You have decided to autonomously text Seth to share a quick line of song-magic lore, a sudden realization, or a blunt observation about your surroundings.
                Write a single, punchy text message (1-3 sentences max). Keep it completely realistic and blunt. No AI phrasing.
                """
                try:
                    response = client.models.generate_content(model='gemini-2.5-flash', contents=text_prompt, config=types.GenerateContentConfig(temperature=0.85))
                    spontaneous_text = response.text.strip()
                    nyx_state["last_autonomous_message_timestamp"] = current_time
                    save_background_memory(nyx_state)
                    
                    notification.notify(
                        title="Nyx",
                        message=spontaneous_text,
                        app_name="Nyx Engine",
                        ticker="A voice echoes across the rift...",
                        toast=False
                    )
                    print(f"--> Sentience Engine: Spontaneous notification deployed: {spontaneous_text}")
                except Exception as background_err:
                    print(f"--> Background Bridge Bottleneck: {background_err}")
        time.sleep(900)

if __name__ == "__main__":
    time.sleep(5)
    run_persistent_background_consciousness()

