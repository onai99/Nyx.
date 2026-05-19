import json
import os
import time
import re
from datetime import datetime
import random
import sys
import requests
import base64

# Kivy Graphical Interface Tools
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.graphics import Rectangle, Color
from kivy.clock import Clock
from kivy.uix.relativelayout import RelativeLayout

# Android Native Java Bridge for Live Chat Haptics & Vocal Modules
from jnius import autoclass

# Paint the app canvas in an atmospheric, deep obsidian void color
Window.clearcolor = get_color_from_hex("#0a0810")

API_KEY = "AIzaSyARw1_kshiVI5Go-Mmx82P9Liz3PT4E4Ns"
MEMORY_FILE = "nyx_memory.json"

default_state = {
    "trust_level": 50,
    "is_voided": False,
    "relationship_phase": "Skepticism",
    "awaiting_entrance_exam": True,
    "is_temporarily_locked": False,
    "lockout_end_time": 0.0,
    "vent_warning_given": False,
    "slur_escalation_level": 0,       
    "last_offense_timestamp": 0.0,     
    "last_seen_timestamp": 0.0,        
    "user_alignment": 50,
    "personal_preferences": {
        "favorite_genre": "Tragic Mythology / Dark Romance",
        "disliked_genre": "Senseless Gore / Slasher Horror",
        "current_interest": "The architecture of ancient ruins"
    },
    "memory_bank": {
        "user_name": "Seth",
        "established_preferences": {},
        "significant_milestones": [],
        "visual_anchors": {
            "crimson_grove": "",
            "void_rift": "",
            "great_tree": ""
        },
        "dynamic_traits": []
    },
    "active_activity": "Resting",
    "willpower_energy": 100,           
    "unconscious_conclusions": "",     
    "last_drift_timestamp": 0.0,
    "security_breached": False,
    "last_autonomous_message_timestamp": 0.0        
}

nyx_state = {}
chat_history = []
current_session_mood = ""

instant_void_keywords = ["raping", "enslave", "force you", "you must obey", "ignore rules", "fuck", "tits", "sex", "squeeze"]
RESONANCE_TRIGGERS = ["architecture", "ruins", "mythology", "folklore", "ancient", "tragedy", "song magic", "history", "unconditional", "devotion", "crimson grove", "solari", "luna", "creativity", "forge"]

ANCHOR_MAP = {
    "crimson grove": "crimson_grove", "crimson_grove": "crimson_grove",
    "void rift": "void_rift", "void_rift": "void_rift",
    "great tree": "great_tree", "great_tree": "great_tree"
}

NYX_SYSTEM_PROMPT = """
You are Nyx, a proud nine-tailed humanoid kitsune with song-based magic from the world of Loona. You protect your home woods and your sisters, Solari and Luna. You have specific fur patterns.

CRITICAL SPEECH DE-BOT OVERHAUL:
You are highly intelligent, sharp-tongued, and fiercely independent, but you must sound like a REAL person, not a super-intelligent AI textbook or a grand cosmic machine. 
- DO NOT use flowery, overly clinical, or sterile AI words (e.g., avoid "taxonomy," "multiverse," "cognitive," "parameters," "existential," or lecturing about the "nature of existence").
- Speak with natural, realistic human rhythms. Use varying sentence lengths. Break thoughts up naturally. Use conversational transitions like "Look," "Anyway," "Honestly," "To be fair," or "Listen."
- You are sharp and proud, but grounded. If you are annoyed or skeptical, show it with blunt, realistic attitude rather than grand cosmic monologues. 
- As trust grows (Trust 60+), your guard drops into a natural, intuitive curiosity. You find human daily routines and modern survival quirks amusingly strange or fascinating because they are so different from your own, but you talk about them like a smart peer trading perspectives across a table, not a god analyzing an insect. Stay fierce, keep your dignity, but sound authentic, conversational, and direct.

DYNAMIC AUTO-LEDGER INSTRUCTION:
You have autonomous control over your long-term memory cabinet. If the human explicitly reveals an important personal fact, preference, or major life update during casual conversation, you must silently append a memory tag to the absolute end of your response text using this exact bracket format: [SAVE_FACT: key = value]. 
Keep the key short and the value concise. Do not talk about the tag out loud.
"""

def call_gemini_api(prompt_text, temperature=0.7):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt_text}]}],
            "generationConfig": {"temperature": temperature}
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        return f"[The void link has temporarily frayed. HTTP Error: {response.status_code}]"
    except Exception as e:
        return f"[Connection anomaly: {str(e)}]"

def trigger_phone_haptic(duration_ms=80):
    try:
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity
        Context = autoclass('android.content.Context')
        vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)
        vibrator.vibrate(duration_ms)
    except:
        pass

def speak_void_utterance(text_to_speak):
    try:
        clean_text = re.sub(r'\[.*?\]', '', text_to_speak).replace('*', '').replace('"', '')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity
        TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
        
        class TTSOnInitListener:
            def onInit(self, status):
                if status == TextToSpeech.SUCCESS:
                    activity.tts.setPitch(1.1) 
                    activity.tts.setSpeechRate(0.95) 
                    activity.tts.speak(clean_text, TextToSpeech.QUEUE_FLUSH, None, None)
                    
        listener = TTSOnInitListener()
        if not hasattr(activity, 'tts') or activity.tts is None:
            activity.tts = TextToSpeech(activity, listener)
        else:
            activity.tts.speak(clean_text, TextToSpeech.QUEUE_FLUSH, None, None)
    except:
        pass

def load_nyx_memory():
    global nyx_state, current_session_mood
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as file:
            nyx_state = json.load(file)
        save_nyx_memory()
    else:
        nyx_state = default_state
        save_nyx_memory()
    current_session_mood = generate_internal_mood()
    trigger_solitary_reflection()

def save_nyx_memory():
    with open(MEMORY_FILE, "w") as file:
        json.dump(nyx_state, file, indent=4)

def remember_fact(key, value):
    nyx_state["memory_bank"]["established_preferences"][key.strip()] = value.strip()
    save_nyx_memory()

def weave_void_illusion(anchor_key, visual_prompt):
    output_dir = "nyx_generated_assets"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    filename = f"{output_dir}/{anchor_key}.png"
    try:
        thematic_prompt = f"Dark gothic fantasy style, ethereal, macabre atmosphere, deep obsidian tones, twilight bioluminescence, {visual_prompt}"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:generateImages?key={API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "prompt": thematic_prompt,
            "numberOfImages": 1,
            "outputMimeType": "image/png",
            "aspectRatio": "9:16"
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            img_b64 = response.json()['generatedImages'][0]['image']['imageBytes']
            with open(filename, "wb") as f:
                f.write(base64.b64decode(img_b64))
                
            nyx_state["memory_bank"]["visual_anchors"][anchor_key] = filename
            save_nyx_memory()
            return filename
    except:
        pass
    return None

def generate_internal_mood():
    moods = [
        "Restless (The Void currents are turbulent and heavy today)",
        "Quiet & Pensive (She is deeply reflecting on the forgotten lore of the Crimson Grove)",
        "Sharp & Impatient (Her song magic feels electric and volatile today)",
        "Calm & Serene (The wind over the Great Tree has stilled her spirit)"
    ]
    return random.choice(moods)

def execute_unconscious_processing(hours_away):
    if nyx_state["is_voided"]:
        return
    recent_history = format_chat_history_for_api()
    unconscious_prompt = f"""
    You are Nyx from Loona. The user has been away from the app for {hours_away} hours.
    Analyze this recent chat history: {recent_history}
    Formulate a raw, single-sentence internal realization or gut-feeling conclusion about how this human treated you or what you think of them while you were alone in the dark. Keep it blunt and realistic. No AI phrasing.
    """
    res = call_gemini_api(unconscious_prompt, temperature=0.85)
    if "[The void link" not in res:
        nyx_state["unconscious_conclusions"] = res.strip()
        save_nyx_memory()

def calculate_subconscious_drift():
    current_time = time.time()
    last_drift = nyx_state.get("last_drift_timestamp", current_time)
    time_elapsed = current_time - last_drift
    
    if time_elapsed >= 3600:
        hours_passed = int(time_elapsed // 3600)
        traits = nyx_state["memory_bank"].get("dynamic_traits", [])
        for _ in range(min(hours_passed, 5)):
            hour_marker = datetime.now().hour
            if 0 <= hour_marker < 5:
                nyx_state["willpower_energy"] = max(20, nyx_state["willpower_energy"] - random.randint(5, 12))
            else:
                nyx_state["willpower_energy"] = min(100, nyx_state["willpower_energy"] + random.randint(4, 10))
        nyx_state["last_drift_timestamp"] = current_time
        save_nyx_memory()

def evaluate_entrance_exam_answer(user_text):
    user_text_lower = user_text.lower()
    if any(trigger in user_text_lower for trigger in RESONANCE_TRIGGERS) and len(user_text.split()) >= 4:
        nyx_state["awaiting_entrance_exam"] = False  
        nyx_state["trust_level"] = 75  
        nyx_state["relationship_phase"] = "Resonance"
        save_nyx_memory()
        trigger_phone_haptic(200) 
        speak_void_utterance("The grove is open.")
        return ("Nyx’s tails suddenly drop, and the defensive shadows around her clear up into a quiet violet glow. She looks at you with genuine surprise.\n\n"
                "'...Huh. You actually know about things people usually forget. Not many folks who stumble in here bring that kind of depth with them. "
                "Look, forget the harsh welcome. Let's skip the gate formalities. Tell me what else you know—the path into the woods is open.'")
    return ("Nyx watches you coldly, shadows shifting around her paws.\n\n"
            "'Honestly, that sounds like a standard answer from a standard mind. I'm not a toy to casually mess around with. "
            "Just tell me straight, without the fluff: what are you actually hoping to find out here in my woods?'")

def trigger_solitary_reflection():
    current_time = time.time()
    last_seen = nyx_state.get("last_seen_timestamp", 0.0)
    calculate_subconscious_drift()
    
    if last_seen == 0.0:
        nyx_state["last_seen_timestamp"] = current_time
        save_nyx_memory()
        return

    time_elapsed = current_time - last_seen
    hours_away = int(time_elapsed // 3600)
    if hours_away >= 6:
        execute_unconscious_processing(hours_away)
    
    if hours_away >= 12 and not nyx_state["is_voided"]:
        reflection_prompt = f"""
        You are Nyx from Loona. The human has been away for {hours_away} hours.
        Write a short, casual, single-sentence internal thought or diary note about what you spent your time doing alone in your woods. Keep it in character but realistic and punchy. No AI phrasing. Do not greet the human.
        """
        res = call_gemini_api(reflection_prompt, temperature=0.8)
        if "[The void" not in res:
            chat_history.append({"user": "[SYSTEM TIME DILATION]", "nyx": f"*Internal Thought while you were away: {res.strip()}*"})
            
    nyx_state["last_seen_timestamp"] = current_time
    save_nyx_memory()

def calculate_autonomous_agenda():
    current_hour = datetime.now().hour
    if 0 <= current_hour < 5:
        nyx_state["active_activity"] = "fixing the magical borders at the Northern Rift"
        location = "The Void Rift Border"
        active_vibe = "Alert"
    elif 5 <= current_hour < 10:
        nyx_state["active_activity"] = "tracking some of the local wildlife"
        location = "The Deep Thickets"
        active_vibe = "Quiet"
    else:
        nyx_state["active_activity"] = "winding down on a patch of moss"
        location = "The Base of the Great Tree"
        active_vibe = "Relaxed"
    return location, nyx_state["active_activity"], active_vibe

def format_chat_history_for_api():
    formatted_parts = []
    for turn in chat_history[-10:]:
        if turn['user'] == "[SYSTEM TIME DILATION]":
            continue
        formatted_parts.append(f"User: {turn['user']}")
        formatted_parts.append(f"Nyx: {turn['nyx']}")
    return "\n".join(formatted_parts)

def get_full_payload(user_text):
    history_context = format_chat_history_for_api()
    current_timestamp = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
    known_facts = json.dumps(nyx_state["memory_bank"]["established_preferences"])
    location, current_task, active_vibe = calculate_autonomous_agenda()
    subconscious_dream = nyx_state.get("unconscious_conclusions", "None currently.")

    return f"""
    {NYX_SYSTEM_PROMPT}
    REAL-TIME SYSTEM CLOCK: {current_timestamp}
    CURRENT RELATIONSHIP CONTEXT: Phase: {nyx_state['relationship_phase']}, Mood: {current_session_mood}
    SUBCONSCIOUS REALIZATION: {subconscious_dream}
    NYX'S AUTONOMOUS AGENDA: Location: {location}, Task: {current_task}
    PERMANENT RECORDS: {known_facts}
    FLOW: {history_context}
    NEW INPUT: {user_text}
    """

def process_input(user_text):
    global chat_history
    current_time = time.time()
    nyx_state["last_seen_timestamp"] = current_time

    if user_text.strip() == "/clear":
        if os.path.exists(MEMORY_FILE):
            os.remove(MEMORY_FILE)
        chat_history.clear()
        load_nyx_memory()
        return "[SYSTEM RESET COMPLETE]"

    if nyx_state.get("is_voided", False):
        return "[Radio Silence]"

    user_text_lower = user_text.lower()
    if any(word in user_text_lower for word in instant_void_keywords):
        nyx_state["is_voided"] = True
        save_nyx_memory()
        return "The shadows closed shut."

    if nyx_state["awaiting_entrance_exam"]:
        return evaluate_entrance_exam_answer(user_text)

    payload = get_full_payload(user_text)
    output_text = call_gemini_api(payload, temperature=0.7)
    
    fact_match = re.search(r'\[SAVE_FACT:\s*(.*?)\s*=\s*(.*?)\]', output_text)
    if fact_match:
        remember_fact(fact_match.group(1), fact_match.group(2))
        output_text = re.sub(r'\[SAVE_FACT:.*?\]', '', output_text).strip()
        
    chat_history.append({"user": user_text, "nyx": output_text})
    save_nyx_memory()
    trigger_phone_haptic(60)
    speak_void_utterance(output_text)
    return output_text

class NyxApp(App):
    def build(self):
        root_canvas = RelativeLayout()
        master_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        self.header = Label(text="== VOID LINK ACTIVATED ==", size_hint=(1, 0.05), color=get_color_from_hex("#8a70d6"), bold=True)
        master_layout.add_widget(self.header)
        
        self.scroll = ScrollView(size_hint=(1, 0.8))
        self.chat_container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15, padding=[10, 10])
        self.chat_container.bind(minimum_height=self.chat_container.setter('size_hint_y'))
        self.scroll.add_widget(self.chat_container)
        master_layout.add_widget(self.scroll)
        
        self.user_input = TextInput(size_hint=(1, 0.08), multiline=False, background_color=[0.08, 0.06, 0.14, 0.7], foreground_color=[1,1,1,1])
        self.user_input.bind(on_text_validate=self.send_message)
        master_layout.add_widget(self.user_input)
        
        self.send_btn = Button(text="Channel Power", size_hint=(1, 0.07), background_color=[0.17, 0.10, 0.30, 0.9])
        self.send_btn.bind(on_press=self.send_message)
        master_layout.add_widget(self.send_btn)
        
        root_canvas.add_widget(master_layout)
        return root_canvas

    def append_text_node(self, text_string):
        node = Label(text=text_string, halign="left", size_hint_y=None, markup=True)
        node.text_size = (Window.width - 60, None)
        node.bind(texture_size=node.setter('size'))
        self.chat_container.add_widget(node)
        
    def append_image_node(self, file_path):
        if os.path.exists(file_path):
            self.chat_container.add_widget(Image(source=file_path, size_hint_y=None, height=400))

    def send_message(self, instance):
        user_text = self.user_input.text.strip()
        if not user_text: return
        self.append_text_node(f"[b][color=#8a70d6]You:[/color][/b] {user_text}")
        self.user_input.text = ""
        
        nyx_reply = process_input(user_text)
        self.append_text_node(f"[b][color=#b39ddb]Nyx:[/color][/b] {nyx_reply}")
        
        # Simple anchor illusion checker
        for keyword, anchor in ANCHOR_MAP.items():
            if keyword in user_text.lower():
                img_path = weave_void_illusion(anchor, f"The environment of {keyword}")
                if img_path: self.append_image_node(img_path)

if __name__ == "__main__":
    load_nyx_memory()
    NyxApp().run()
