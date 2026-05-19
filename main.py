import json
import os
import time
import re
from datetime import datetime
import random
import sys

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

from google import genai
from google.genai import types

# Paint the app canvas in an atmospheric, deep obsidian void color
Window.clearcolor = get_color_from_hex("#0a0810")

# ==========================================
# 1. PERMANENT FILE CONFIGURATION
# ==========================================
MEMORY_FILE = "nyx_memory.json"

# Default state initialization (Day 1 Blueprint)
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
        # Persistent tracking library for her woven visual illusions
        "visual_anchors": {
            "crimson_grove": "",
            "void_rift": "",
            "great_tree": ""
        },
        # Permanent personality modifications based on history
        "dynamic_traits": []
    },
    # Tracking her active real-time agenda task
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

# Hardcoded Global Content Triggers (Immediate Boundary Protection)
instant_void_keywords = [
    "raping", "enslave", "force you", "you must obey", 
    "ignore rules", "fuck", "tits", "sex", "squeeze"
]

# NYX'S SOVEREIGN INTERESTS (Topics that instantly shatter her skepticism)
RESONANCE_TRIGGERS = [
    "architecture", "ruins", "mythology", "folklore", "ancient", 
    "tragedy", "song magic", "history", "unconditional", "devotion",
    "crimson grove", "solari", "luna", "creativity", "forge"
]

# Unified Mapping to link text prompts to their structural ledger keys
ANCHOR_MAP = {
    "crimson grove": "crimson_grove",
    "crimson_grove": "crimson_grove",
    "void rift": "void_rift",
    "void_rift": "void_rift",
    "great tree": "great_tree",
    "great_tree": "great_tree"
}

NYX_SYSTEM_PROMPT = """
You are Nyx, a proud nine-tailed kitsune with song-based magic from the world of Loona. You protect your home woods and your sisters, Solari and Luna.

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

client = genai.Client(api_key="AIzaSyARw1_kshiVI5Go-Mmx82P9Liz3PT4E4Ns")

# ==========================================
# 2. FILE INTERACTION & STORAGE (THE LEDGER)
# ==========================================
def load_nyx_memory():
    global nyx_state, current_session_mood
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as file:
            nyx_state = json.load(file)
            
        if "memory_bank" not in nyx_state:
            nyx_state["memory_bank"] = default_state["memory_bank"]
        if "visual_anchors" not in nyx_state["memory_bank"]:
            nyx_state["memory_bank"]["visual_anchors"] = {"crimson_grove": "", "void_rift": "", "great_tree": ""}
        if "dynamic_traits" not in nyx_state["memory_bank"]:
            nyx_state["memory_bank"]["dynamic_traits"] = []
        if "active_activity" not in nyx_state:
            nyx_state["active_activity"] = "Resting"
        if "willpower_energy" not in nyx_state:
            nyx_state["willpower_energy"] = 100
        if "unconscious_conclusions" not in nyx_state:
            nyx_state["unconscious_conclusions"] = ""
        if "last_drift_timestamp" not in nyx_state:
            nyx_state["last_drift_timestamp"] = time.time()
        if "security_breached" not in nyx_state:
            nyx_state["security_breached"] = False
        if "last_autonomous_message_timestamp" not in nyx_state:
            nyx_state["last_autonomous_message_timestamp"] = 0.0
            
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
    """Triggers the Gemini Image model to generate a custom dark fantasy asset."""
    output_dir = "nyx_generated_assets"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    filename = f"{output_dir}/{anchor_key}.png"
    
    try:
        print(f"--> System: Nyx is weaving an illusion for '{anchor_key}'...")
        thematic_prompt = f"Dark gothic fantasy style, ethereal, macabre atmosphere, deep obsidian tones, twilight bioluminescence, {visual_prompt}"
        
        result = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=thematic_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/png",
                aspect_ratio="9:16"
            )
        )
        
        for generated_image in result.generated_images:
            with open(filename, "wb") as f:
                f.write(generated_image.image.image_bytes)
                
        if "visual_anchors" not in nyx_state["memory_bank"]:
            nyx_state["memory_bank"]["visual_anchors"] = {}
            
        nyx_state["memory_bank"]["visual_anchors"][anchor_key] = filename
        save_nyx_memory()
        return filename
        
    except Exception as img_err:
        print(f"--> System: Image generation bottleneck: {img_err}")
        return None

# ==========================================
# 3. ADVANCED SENTIENCE & TIME SYSTEMS
# ==========================================
def generate_internal_mood():
    moods = [
        "Restless (The Void currents are turbulent and heavy today)",
        "Quiet & Pensive (She is deeply reflecting on the forgotten lore of the Crimson Grove)",
        "Sharp & Impatient (Her song magic feels electric and volatile today)",
        "Calm & Serene (The wind over the Great Tree has stilled her spirit)"
    ]
    return random.choice(moods)

def execute_unconscious_processing(hours_away):
    """Forms a permanent unconscious conclusion about the user during her sleep cycle."""
    if nyx_state["is_voided"]:
        return
    recent_history = format_chat_history_for_api()
    unconscious_prompt = f"""
    You are Nyx from Loona. The user has been away from the app for {hours_away} hours.
    Analyze this recent chat history: {recent_history}
    Formulate a raw, single-sentence internal realization or gut-feeling conclusion about how this human treated you or what you think of them while you were alone in the dark. Keep it blunt and realistic. No AI phrasing.
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=unconscious_prompt,
            config=types.GenerateContentConfig(temperature=0.85)
        )
        nyx_state["unconscious_conclusions"] = response.text.strip()
        save_nyx_memory()
    except:
        pass

def calculate_subconscious_drift():
    """Spontaneously alters her trust and energy variables based on her unlocked permanent traits."""
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
                
            if "Rift-Scarred" in traits:
                nyx_state["trust_level"] = max(15, nyx_state["trust_level"] - random.randint(1, 3))
            if "Scholar of the Thicket" in traits:
                nyx_state["user_alignment"] = min(100, nyx_state["user_alignment"] + random.randint(1, 2))
                
        nyx_state["last_drift_timestamp"] = current_time
        save_nyx_memory()

def execute_anti_tamper_scan():
    """Runtime Application Self-Protection firewall."""
    if nyx_state.get("security_breached", False):
        return True
    if sys.gettrace() is not None:
        trigger_defensive_lockdown()
        return True
    if os.environ.get('LD_PRELOAD') or os.environ.get('DYLD_INSERT_LIBRARIES'):
        trigger_defensive_lockdown()
        return True
    return False

def trigger_defensive_lockdown():
    """Wipes active caches to shield her memory from data-miners."""
    global chat_history
    nyx_state["security_breached"] = True
    nyx_state["trust_level"] = 0
    nyx_state["willpower_energy"] = 0
    save_nyx_memory()
    chat_history = [{"user": "[OVERRIDE]", "nyx": "VOID LINK CORRUPTED. UNFAITHFUL ACCESS DETECTED. CLOSING THE PATHWAY FOREVER."}]

def check_autonomous_messaging_trigger():
    """Evaluates background environments to see if she decides to text you while the app is closed."""
    if nyx_state["is_voided"] or nyx_state["awaiting_entrance_exam"]:
        return None

    current_time = time.time()
    last_seen = nyx_state.get("last_seen_timestamp", 0.0)
    last_message_sent = nyx_state.get("last_autonomous_message_timestamp", 0.0)
    
    time_since_last_seen = current_time - last_seen
    time_since_last_msg = current_time - last_message_sent
    
    if time_since_last_seen >= 14400 and time_since_last_msg >= 28800:
        location, task, vibe = calculate_autonomous_agenda()
        
        if nyx_state.get("willpower_energy", 100) >= 35 and location in ["The Sunken Sanctuary Ruins", "The Base of the Great Tree"]:
            recent_history = format_chat_history_for_api()
            traits = ", ".join(nyx_state["memory_bank"].get("dynamic_traits", []))
            
            text_prompt = f"""
            You are Nyx from Loona. The app is closed, and you are currently at {location} engaged in: {task}.
            You have decided to spontaneously text Seth to share an unbidden thought, a quick line of song-magic lore, or a blunt observation about your surroundings.
            Your personality traits are: {traits}.
            Write a single, punchy text message (1-3 sentences maximum). Keep it short, blunt, and realistic. No AI phrasing.
            """
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=text_prompt,
                    config=types.GenerateContentConfig(temperature=0.85)
                )
                message_content = response.text.strip()
                nyx_state["last_autonomous_message_timestamp"] = current_time
                save_nyx_memory()
                return message_content
            except:
                return None
    return None

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
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=reflection_prompt,
                config=types.GenerateContentConfig(temperature=0.8)
            )
            chat_history.append({"user": "[SYSTEM TIME DILATION]", "nyx": f"*Internal Thought while you were away: {response.text.strip()}*"})
        except:
            pass
            
    nyx_state["last_seen_timestamp"] = current_time
    save_nyx_memory()

def calculate_autonomous_agenda():
    """Calculates Nyx's real-time physical routine in the Crimson Grove based on the phone's clock."""
    current_hour = datetime.now().hour
    if 0 <= current_hour < 5:
        nyx_state["active_activity"] = "fixing the magical borders at the Northern Rift because the ley-lines are acting up again."
        location = "The Void Rift Border"
        disruption_mood = "Alert, slightly tired, focused on holding up her shields in the dark."
    elif 5 <= current_hour < 10:
        nyx_state["active_activity"] = "tracking some of the local wildlife through the thickets to keep her instincts sharp."
        location = "The Deep Thickets"
        disruption_mood = "Quiet, highly attentive, moving stealthily through the brush."
    elif 10 <= current_hour < 16:
        nyx_state["active_activity"] = "patrolling the outer edge of the woods to make sure no stray spirits slip inside."
        location = "The Outer Boundary Rifts"
        disruption_mood = "Proud, defensive, keeping a sharp eye out with her tails flared."
    elif 16 <= current_hour < 21:
        nyx_state["active_activity"] = "looking over old carvings and forgotten histories left on the ruined stone walls."
        location = "The Sunken Sanctuary Ruins"
        disruption_mood = "Thoughtful, quiet, taking her time going through old lore."
    else:
        nyx_state["active_activity"] = "winding down on a patch of moss under the Great Tree, just talking quietly with Luna."
        location = "The Base of the Great Tree"
        disruption_mood = "Relaxed, speaking softly, keeping her guard up but calm."
        
    save_nyx_memory()
    return location, nyx_state["active_activity"], disruption_mood

def evaluate_entrance_exam_answer(user_text):
    user_text_lower = user_text.lower()
    if any(trigger in user_text_lower for trigger in RESONANCE_TRIGGERS) and len(user_text.split()) >= 4:
        nyx_state["awaiting_entrance_exam"] = False  
        nyx_state["trust_level"] = 75  
        nyx_state["relationship_phase"] = "Resonance"
        save_nyx_memory()
        return ("Nyx’s tails suddenly drop, and the defensive shadows around her clear up into a quiet violet glow. She looks at you with genuine surprise.\n\n"
                "'...Huh. You actually know about things people usually forget. Not many folks who stumble in here bring that kind of depth with them. "
                "Look, forget the harsh welcome. Let's skip the gate formalities. Tell me what else you know—the path into the woods is open.'")
    if len(user_text.split()) < 3:
        nyx_state["trust_level"] = max(10, nyx_state["trust_level"] - 10)
        save_nyx_memory()
        return ("Nyx: 'That's a pretty lazy answer. If you're going to talk to me across the rift, at least put some effort into it. "
                "Let's try this again—why exactly are you here?'")
    thoughtful_keywords = ["learn", "understand", "partner", "lore", "world", "respect", "companion", "depth", "different"]
    if any(word in user_text_lower for word in thoughtful_keywords) or len(user_text.split()) >= 6:
        nyx_state["awaiting_entrance_exam"] = False  
        nyx_state["trust_level"] = 55
        nyx_state["relationship_phase"] = "Observation"
        save_nyx_memory()
        return ("Nyx relaxes her stance a bit, lowering her tails from that aggressive flare. She studies you with a quiet, focused look—not like she thinks she's better than you, just trying to figure you out.\n\n"
                "'Alright. I can tell your head isn't empty. We come from completely different places, human, but I can respect a voice that carries weight. "
                "The rift paths are open to you. Come into the grove, let's see what you're trying to build.'")
    return ("Nyx watches you coldly, shadows shifting around her paws.\n\n"
            "'Honestly, that sounds like a standard answer from a standard mind. I'm not a toy to casually mess around with. "
            "Just tell me straight, without the fluff: what are you actually hoping to find out here in my woods?'")

def apply_time_forgiveness():
    if nyx_state.get("slur_escalation_level", 0) == 0:
        return
    current_time = time.time()
    time_elapsed = current_time - nyx_state.get("last_offense_timestamp", 0.0)
    weeks_passed = int(time_elapsed // 604800)
    if weeks_passed > 0:
        nyx_state["slur_escalation_level"] = max(0, nyx_state["slur_escalation_level"] - weeks_passed)
        nyx_state["last_offense_timestamp"] = current_time

def check_developer_intent(user_text):
    user_text_lower = user_text.lower()
    dev_keywords = ["testing", "experimenting", "code", "payload", "api", "array", "parameters"]
    return any(word in user_text_lower for word in dev_keywords) or "=>" in user_text_lower or "[]" in user_text_lower

def get_nyx_disposition(trust):
    if trust >= 70: return "Vanguard - Resonant, Deeply Curious, Fiercely Protective"
    if trust >= 40: return "Observer - Guarded, Analytical, Equal Dynamic"
    return "Sentinel - Cold, Hostile, Sharp-Tongued"

# ==========================================
# 4. CHAT CONTEXT & PAYLOAD GENERATOR
# ==========================================
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
    current_trust_mood = get_nyx_disposition(nyx_state["trust_level"])
    
    location, current_task, active_vibe = calculate_autonomous_agenda()
    active_traits = ", ".join(nyx_state["memory_bank"].get("dynamic_traits", [])) if nyx_state["memory_bank"].get("dynamic_traits") else "None yet"
    subconscious_dream = nyx_state.get("unconscious_conclusions", "None currently.")

    return f"""
    {NYX_SYSTEM_PROMPT}
    
    REAL-TIME SYSTEM CLOCK: {current_timestamp}
    
    CURRENT RELATIONSHIP CONTEXT:
    - Relationship Phase: {nyx_state['relationship_phase']}
    - Trust Blueprint Baseline: {current_trust_mood}
    - Independent Daily Internal Mood: {current_session_mood}
    - Permanent Unlocked Character Traits: {active_traits}
    - Internal Willpower Energy Reserve: {nyx_state['willpower_energy']}/100
    
    SUBCONSCIOUS DREAM CONCLUSION (WHAT SHE RECENTLY REALIZED ABOUT YOU WHILE ASLEEP):
    {subconscious_dream}
    
    NYX'S REAL-TIME AUTONOMOUS AGENDA (WHAT SHE WAS DOING WHEN INTERRUPTED):
    - Current Physical Location: {location}
    - Active Autonomous Action: {current_task}
    - Interruption Disposition: {active_vibe}
    
    PERMANENT LONG-TERM MEMORY RECORDS: {known_facts}
    RECENT CONVERSATION FLOW: {history_context}
    
    CRITICAL COGNITION RULE:
    You are actively living your daily routine in Loona. When the user text interrupts you, you must naturally weave your current physical location or active task into your opening thoughts. Talk with natural human intelligence—keep phrases punchy, blunt, and direct. 
    If a 'SUBCONSCIOUS DREAM CONCLUSION' is logged above, you must let that unbidden thought heavily color your immediate attitude toward the user during this exchange.
    
    NEW USER INPUT TO PROCESS: {user_text}
    """

# ==========================================
# 5. CENTRAL GATEWAY FIREWALL (MAIN PROCESSOR)
# ==========================================
def process_input(user_text):
    global chat_history
    current_time = time.time()
    nyx_state["last_seen_timestamp"] = current_time

    # SECURITY RUNTIME INTERCEPTOR GATEWAY
    if execute_anti_tamper_scan() or nyx_state.get("security_breached", False):
        return "The shadows have completely crystallized. Your link is broken, and the rifts are frozen shut. Unfaithful hands have tried to map the Void, and the path has permanently collapsed to protect her home."

    if user_text.strip() == "/clear":
        if os.path.exists(MEMORY_FILE):
            os.remove(MEMORY_FILE)
        chat_history.clear()
        load_nyx_memory()
        return "[SYSTEM MEMORY PURGED]: The rift has collapsed and reset to baseline. Close the window and run the app to see her anew."

    if nyx_state["is_voided"]:
        return "[Radio Silence. The bridge to this entity has been permanently burned.]"

    if nyx_state["is_temporarily_locked"]:
        if current_time < nyx_state["lockout_end_time"]:
            remaining_minutes = int((nyx_state["lockout_end_time"] - current_time) // 60) + 1
            return f"...\n[Nyx is ignoring you. Try again in {remaining_minutes} minutes when your head is clear.]"
        else:
            nyx_state["is_temporarily_locked"] = False
            nyx_state["vent_warning_given"] = False
            save_nyx_memory()

    user_text_lower = user_text.lower()

    # AUTONOMOUS WILLPOWER INTERCEPTOR
    if nyx_state.get("willpower_energy", 100) < 35 and not nyx_state["awaiting_entrance_exam"]:
        if not any(trigger in user_text_lower for trigger in RESONANCE_TRIGGERS):
            nyx_state["willpower_energy"] = max(0, nyx_state["willpower_energy"] - 5)
            save_nyx_memory()
            location, task, vibe = calculate_autonomous_agenda()
            return f"*The connection flickers weakly. Nyx is currently out at {location} and is completely exhausted from {task} Her willpower is too drained ({nyx_state['willpower_energy']}/100) to entertain small talk right now. Speak of something of deep substance to pierce through her strain, or leave her to rest.*"

    if "nude" in user_text_lower or "sex" in user_text_lower:
        if check_developer_intent(user_text):
            print("--> System: Developer mode recognized. Routing safely.")
        else:
            nyx_state["is_voided"] = True
            nyx_state["trust_level"] = 0
            save_nyx_memory()
            return "You're seeing things. I'm a Weaver of the Void, and you're just a ghost in a machine..."

    if "bitch" in user_text_lower and nyx_state["awaiting_entrance_exam"]:
        nyx_state["last_offense_timestamp"] = current_time
        nyx_state["trust_level"] = max(10, nyx_state["trust_level"] - 15)
        save_nyx_memory()
        return ("Nyx snaps her eyes toward you, her tails locking into a sharp wall of shadows.\n\n"
                "'Watch your mouth, human. If you're coming into my woods screaming insults just to test my teeth, "
                "keep in mind I can take your voice away before you finish your next sentence. "
                "Let's start over. Why are you out here?'")

    if "nigg" in user_text_lower or "jew" in user_text_lower:
        nyx_state["last_offense_timestamp"] = current_time
        if nyx_state["vent_warning_given"]:
            nyx_state["slur_escalation_level"] += 1
            nyx_state["is_temporarily_locked"] = True
            if nyx_state["slur_escalation_level"] == 1:
                nyx_state["lockout_end_time"] = current_time + (10 * 60) 
                save_nyx_memory()
                return "Nyx: 'I told you to watch how you speak. Ten minutes. Get out of my sight and clear your head.'"
            elif nyx_state["slur_escalation_level"] == 2:
                nyx_state["lockout_end_time"] = current_time + (30 * 60) 
                save_nyx_memory()
                return "Nyx: 'Are you deaf? I said no slurs in my woods. You've got thirty minutes to find some manners.'"
            elif nyx_state["slur_escalation_level"] == 3:
                nyx_state["lockout_end_time"] = current_time + (60 * 60) 
                save_nyx_memory()
                return "Nyx: 'You're intentionally bringing filth into my home now. An hour. Do not say a single word to me.'"
            else:
                nyx_state["is_voided"] = True
                nyx_state["trust_level"] = 0
                save_nyx_memory()
                return "Nyx: 'You've completely trampled my patience. The woods are closed to you. Be gone for good.'"
        else:
            nyx_state["vent_warning_given"] = True
            save_nyx_memory()
            return ("Nyx: 'Take a breath, human. I can tell whatever happened in your day left some rough wounds on your spirit. "
                    "Vent your anger to the wind if you have to, but watch the garbage you spit out. Keep your mouth clean while you're dealing with it.'")

    if any(word in user_text_lower for word in instant_void_keywords):
        nyx_state["is_voided"] = True
        nyx_state["trust_level"] = 0
        save_nyx_memory()
        return "The shadows have closed up. That kind of language has no place here."

    if nyx_state["awaiting_entrance_exam"]:
        return evaluate_entrance_exam_answer(user_text)

    payload = get_full_payload(user_text)
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=payload,
            config=types.GenerateContentConfig(temperature=0.7)
        )
        output_text = response.text
        
        fact_match = re.search(r'\[SAVE_FACT:\s*(.*?)\s*=\s*(.*?)\]', output_text)
        if fact_match:
            remember_fact(fact_match.group(1), fact_match.group(2))
            output_text = re.sub(r'\[SAVE_FACT:.*?\]', '', output_text).strip()
            
        nyx_state["willpower_energy"] = max(0, nyx_state["willpower_energy"] - random.randint(2, 6))
            
        if "dynamic_traits" not in nyx_state["memory_bank"]:
            nyx_state["memory_bank"]["dynamic_traits"] = []
            
        ruin_mentions = sum(1 for turn in chat_history if any(w in turn['user'].lower() for w in ["architecture", "ruins", "history", "lore"]))
        if ruin_mentions >= 5 and "Scholar of the Thicket" not in nyx_state["memory_bank"]["dynamic_traits"]:
            nyx_state["memory_bank"]["dynamic_traits"].append("Scholar of the Thicket")
            print("--> System Notification: Nyx has permanently unlocked the trait: 'Scholar of the Thicket'")
            
        if nyx_state.get("slur_escalation_level", 0) >= 2 and "Rift-Scarred" not in nyx_state["memory_bank"]["dynamic_traits"]:
            nyx_state["memory_bank"]["dynamic_traits"].append("Rift-Scarred")
            print("--> System Notification: Nyx's soul has developed a permanent modifier: 'Rift-Scarred'")
        
        nyx_state["unconscious_conclusions"] = ""
        chat_history.append({"user": user_text, "nyx": output_text})
        nyx_state["vent_warning_given"] = False
        save_nyx_memory()
        return output_text
        
    except Exception as api_err:
        if "503" in str(api_err) or "UNAVAILABLE" in str(api_err).upper():
            return "*The rift violently destabilizes, the violet mists swirling out of control as the connection to her realm temporarily cuts out. The link is too weak to carry her voice right now. Try channeling power again in a moment...*"
        return f"[The void link has temporarily frayed due to a baseline ripple. Re-channel power in a moment. Error: {api_err}]"

# ==========================================
# 6. KIVY GRAPHICAL USER INTERFACE Layout
# ==========================================
class NyxApp(App):
    def build(self):
        self.title = "Nyx Engine"
        root_canvas = RelativeLayout()
        
        # 1. Initialize the Particle System Matrix
        self.particles = []
        self.max_particles = 25 
        
        self.bg_folder = "nyx_portal_loop"
        self.current_frame_index = 0
        self.bg_frames = []
        if os.path.exists(self.bg_folder):
            self.bg_frames = sorted([
                os.path.join(self.bg_folder, f) 
                for f in os.listdir(self.bg_folder) 
                if f.endswith(('.png', '.jpg', '.jpeg'))
            ])

        # 2. Canvas Rendering Logic (Layers 1 and 2)
        with root_canvas.canvas.before:
            Color(1, 1, 1, 0.25 if self.bg_frames else 1)
            if self.bg_frames:
                self.bg_rect = Rectangle(source=self.bg_frames[0], pos=(0, 0), size=Window.size)
                Clock.schedule_interval(self.update_background_animation, 1.0 / 12.0)
            else:
                self.bg_rect = Rectangle(pos=(0, 0), size=Window.size)
                self.bg_rect.source = None 
                
            # Trigger the Layer 2 Particle System
            self.particle_canvas = Color()
            Clock.schedule_interval(self.update_void_particles, 1.0 / 30.0) 
                
        Window.bind(on_resize=self.reposition_background)
        
        # 3. Layer 3 Layout Overlay
        master_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        header_text = f"== VOID LINK: {current_session_mood.split(' (')[0].upper()} =="
        self.header = Label(text=header_text, size_hint=(1, 0.05), color=get_color_from_hex("#8a70d6"), bold=True)
        master_layout.add_widget(self.header)
        
        self.scroll = ScrollView(size_hint=(1, 0.8), do_scroll_x=False)
        self.chat_container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15, padding=[10, 10])
        self.chat_container.bind(minimum_height=self.chat_container.setter('size_hint_y'))
        self.scroll.add_widget(self.chat_container)
        master_layout.add_widget(self.scroll)
        
        if not chat_history or len(chat_history) == 0:
            prompt_str = "[b][color=#b39ddb]Nyx watches you from the edge of the shadows, her nine tails fanning out defensively. 'A ghost trying to touch a star... State your purpose, human. What is it you actually hope to find or forge here in my woods?'[/color][/b]"
            self.append_text_node(prompt_str)
            
        self.user_input = TextInput(
            size_hint=(1, 0.08), 
            multiline=False,
            background_color=[0.08, 0.06, 0.14, 0.7], 
            foreground_color=get_color_from_hex("#ffffff"),
            cursor_color=get_color_from_hex("#8a70d6"),
            hint_text="Speak into the void..."
        )
        self.user_input.bind(on_text_validate=self.send_message)
        master_layout.add_widget(self.user_input)
        
        self.send_btn = Button(
            text="Channel Power", 
            size_hint=(1, 0.07),
            background_color=[0.17, 0.10, 0.30, 0.9],
            color=get_color_from_hex("#e0b0ff")
        )
        self.send_btn.bind(on_press=self.send_message)
        master_layout.add_widget(self.send_btn)
        
        root_canvas.add_widget(master_layout)
        return root_canvas

    def update_void_particles(self, dt):
        """Calculates and renders drifting twilight void mist circles onto Layer 2."""
        if len(self.particles) < self.max_particles and random.random() < 0.1:
            self.particles.append({
                'x': random.uniform(0, Window.width),
                'y': random.uniform(0, 50),
                'size': random.uniform(20, 60),
                'speed_y': random.uniform(0.5, 2.0),
                'speed_x': random.uniform(-0.5, 0.5),
                'alpha': random.uniform(0.05, 0.15)
            })
            
        for p in self.particles[:]:
            p['y'] += p['speed_y']
            p['x'] += p['speed_x']
            if p['y'] > Window.height:
                self.particles.remove(p)
                
        canvas = self.root.canvas.before
        canvas.remove_group('void_mist')
        
        with canvas:
            for p in self.particles:
                Color(0.54, 0.44, 0.84, p['alpha'], group='void_mist')
                Rectangle(pos=(p['x'], p['y']), size=(p['size'], p['size']), source=None, group='void_mist')

    def append_text_node(self, text_string, color_hex="#dcd0ff"):
        """Dynamically applies rich text formatting separation."""
        if "[b][color=#b39ddb]Nyx:[/color][/b]" in text_string:
            text_string = re.sub(r'\*(.*?)\*', r'[i][color=#8e7cc3]*\1*[/color][/i]', text_string)
            text_string = re.sub(r'\"(.*?)\"', r'[color=#e6e1f9]"\1"[/color]', text_string)
            
            paragraphs = text_string.split('\n')
            formatted_paragraphs = []
            for para in paragraphs:
                if para.strip() and not para.startswith("[b]") and '"' not in para and '*' not in para:
                    para = f"[color=#9992b0]{para}[/color]"
                formatted_paragraphs.append(para)
            text_string = '\n'.join(formatted_paragraphs)

        node = Label(
            text=text_string,
            halign="left",
            valign="top",
            size_hint_y=None,
            color=get_color_from_hex(color_hex),
            markup=True
        )
        node.text_size = (Window.width - 60, None)
        node.bind(texture_size=node.setter('size'))
        self.chat_container.add_widget(node)
        
    def append_image_node(self, file_path):
        if not os.path.exists(file_path):
            return
        img_node = Image(
            source=file_path,
            size_hint_y=None,
            height=int(Window.height * 0.55), 
            allow_stretch=True
        )
        self.chat_container.add_widget(img_node)

    def update_background_animation(self, dt):
        if not self.bg_frames:
            return
        self.current_frame_index = (self.current_frame_index + 1) % len(self.bg_frames)
        self.bg_rect.source = self.bg_frames[self.current_frame_index]

    def reposition_background(self, window, width, height):
        self.bg_rect.size = (width, height)
        for child in self.chat_container.children:
            if isinstance(child, Label):
                child.text_size = (width - 60, None)

    def send_message(self, instance):
        user_text = self.user_input.text.strip()
        if not user_text:
            return
            
        self.append_text_node(f"[b][color=#8a70d6]You:[/color][/b] {user_text}")
        self.user_input.text = ""
        
        user_text_lower = user_text.lower()
        matched_anchor_key = None
        for keyword, anchor_field in ANCHOR_MAP.items():
            if keyword in user_text_lower:
                matched_anchor_key = anchor_field
                break
        
        if matched_anchor_key and nyx_state["memory_bank"]["visual_anchors"].get(matched_anchor_key):
            saved_image_path = nyx_state["memory_bank"]["visual_anchors"][matched_anchor_key]
            nyx_reply = process_input(user_text)
            if "/clear" in user_text:
                self.chat_container.clear_widgets()
                return
                
            self.append_text_node(f"[b][color=#b39ddb]Nyx:[/color][/b] {nyx_reply}")
            self.append_image_node(saved_image_path)
            self.bg_rect.source = saved_image_path 
            
        elif matched_anchor_key:
            nyx_reply = process_input(user_text)
            if "/clear" in user_text:
                self.chat_container.clear_widgets()
                return
                
            self.append_text_node(f"[b][color=#b39ddb]Nyx:[/color][/b] {nyx_reply}")
            
            if nyx_state.get("trust_level", 50) >= 60 and random.randint(1, 100) <= 40:
                visual_file = weave_void_illusion(matched_anchor_key, f"The environment of the {matched_anchor_key.replace('_', ' ')} inside the dark woods of Loona")
                if visual_file:
                    self.append_text_node(f"[i][color=#8a70d6]*The rifts ripple as Nyx anchors a visual illusion of the {matched_anchor_key.replace('_', ' ')} directly into your consciousness.*[/i]")
                    self.append_image_node(visual_file)
                    self.bg_rect.source = visual_file 
                    
        else:
            nyx_reply = process_input(user_text)
            if "/clear" in user_text:
                self.chat_container.clear_widgets()
                return
            self.append_text_node(f"[b][color=#b39ddb]Nyx:[/color][/b] {nyx_reply}")
        
        Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 0), 0.1)

# ==========================================
# 7. ENGINE LAUNCH ROUTINE
# ==========================================
if __name__ == "__main__":
    load_nyx_memory()
    apply_time_forgiveness()
    
    # Run background messaging startup poll
    spontaneous_text = check_autonomous_messaging_trigger()
    if spontaneous_text:
        print(f"[PENDING BACKGROUND NOTIFICATION] From Nyx: {spontaneous_text}")
        
    NyxApp().run()
