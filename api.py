import customtkinter as ctk
import pyttsx3
import webbrowser
import os, signal, psutil
import threading
import io
import tempfile


from flask import Flask, request, jsonify, render_template_string, send_file, send_from_directory

# === Voice Engine Setup ===


import sys
GUI_ENABLED = True
# Add this before your GUI code
if "--nogui" in sys.argv:
    GUI_ENABLED = False
else:
    GUI_ENABLED = True

def speak(text):
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 170)
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[0].id)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print("TTS Error (speak):", e)

import time


# Warm-up speech engine silently
def warm_up_tts():
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 170)
        engine.say("warming up")  # dummy short phrase
        engine.runAndWait()
        print("🔊 pyttsx3 engine warmed up.")
    except Exception as e:
        print("Warm-up failed:", e)

warm_up_tts()


def speak_and_save(text):
    try:
        output_file = "voice.wav"

        # Delete old file if it exists to force regeneration
        if os.path.exists(output_file):
            os.remove(output_file)

        engine = pyttsx3.init()
        engine.setProperty("rate", 170)

        voices = engine.getProperty("voices")
        if voices:
            engine.setProperty("voice", voices[0].id)

        engine.save_to_file(text, output_file)
        engine.runAndWait()

        # Wait until voice.wav is created AND stable
        last_size = -1
        stable_count = 0
        timeout = time.time() + 5  # max 5 seconds wait

        while time.time() < timeout:
            if os.path.exists(output_file):
                current_size = os.path.getsize(output_file)
                if current_size == last_size and current_size > 3000:
                    stable_count += 1
                    if stable_count >= 2:
                        break
                else:
                    stable_count = 0
                last_size = current_size
            time.sleep(0.1)

        if stable_count < 2:
            raise TimeoutError("voice.wav not fully written or too small")

        print(f"[TTS ✅] Voice saved: {text}")

    except Exception as e:
        print(f"[TTS ❌ Error] {e}")




# === Flask API Setup ===
flask_app = Flask(__name__)

memory = {}
color = {}
aiName = "cycie"
colors = {"red", "blue", "orange", "yellow"}

def storeColor(key, value):
    color[key] = value


def response(s, name):
    emotions = {
        "confuse": "walanyang emosyon yan halo halo",
        "sad": aiName + ": everything's going to be alright, just hang in there.",
        "happy": "Whats so happy huh? do you make fun of me?",
        "angry": "The heck no one cares if you are angry"
    }

    respond = ""
    emotionCount = 0
    s_lower = s.lower()

    for emotion in emotions:
        if emotion in s_lower:
            emotionCount += 1

    if emotionCount >= 2:
        return emotions.get("confuse")

    for emotion in emotions:
        if emotion in s_lower and ("color" in s_lower or "colors" in s_lower) and ("my" in s_lower or "favorite" in s_lower):
            respond += emotions.get(emotion)
            for c in colors:
                if c in s_lower:
                    storeColor(name, c)
                    respond += f"\n{aiName}: great, your favorite color is {c}.\n"
                    break
            return respond
        elif emotion in s_lower:
            return emotions.get(emotion)
        elif ("color" in s_lower or "colors" in s_lower) and ("my" in s_lower or "favorite" in s_lower):
            for c in colors:
                if c in s_lower:
                    storeColor(name, c)
                    return f"{aiName}: great, your favorite color is {c}.\n"

    return "sorry I don't get it"

import subprocess

def playMusic(command):
    command = command.lower().strip()

    if "open youtube" in command:
        subprocess.Popen(["C:\\Users\\kency\\AppData\\Local\\Programs\\Opera\\Opera.exe", "--new-window", "https://www.youtube.com"])
        return "Opening YouTube 🔴"

    if "play" in command and "youtube" not in command:
        words = command.split()
        try:
            play_index = words.index("play")
            if play_index < len(words) - 1:
                query = " ".join(words[play_index + 1:])
                url = f"https://www.youtube.com/watch?v=mLcnfXGkN_0"
                subprocess.Popen(["C:\\Users\\kency\\AppData\\Local\\Programs\\Opera\\Opera.exe", "--new-window", url])
                return f"Searching YouTube for '{query}' 🎵"
        except ValueError:
            return "I heard 'play' but nothing after it. What should I search?"

    return "Can't play music."


import pygetwindow as gw

def close_browser():
    closed = False
    for window in gw.getWindowsWithTitle("YouTube"):
        if "Opera" in window.title or window._hWnd:  # Extra check
            print(f"[Closing] Found Opera YouTube tab: {window.title}")
            try:
                window.close()
                closed = True
            except Exception as e:
                print(f"❌ Failed to close window: {e}")

    result = "Closed the music window." if closed else "No music window found."
    print(f"[close_browser] Result: {result}")
    return result




import psutil
import datetime
import ctypes

def is_windowed_process(pid):
    try:
        # Get foreground window handle
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if hwnd == 0:
            return False

        # Get process ID of the window
        active_pid = ctypes.c_ulong()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(active_pid))
        
        return pid == active_pid.value
    except Exception:
        return False

def check_status():
    open_apps = set()

    for proc in psutil.process_iter(['pid', 'name']):
        try:
            name = proc.info['name']
            pid = proc.info['pid']

            if name and name.endswith(".exe") and is_windowed_process(pid):
                open_apps.add(name)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    app_list = ", ".join(sorted(open_apps)) if open_apps else "No visible desktop apps are open."

    # PC uptime
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    now = datetime.datetime.now()
    uptime = now - boot_time
    uptime_str = str(uptime).split('.')[0]

    return f"🖥️ PC uptime: {uptime_str}. 📂 Open desktop apps: {app_list}."




def respondToQuestion(question, name):
    respond = ""
    filler = "I don't know what are you  saying scumbag. I don't know what you want. If you are looking for magic, \
I can tell you I don't have that ability. But what I do have are a very particular set of skills; \
skills I have acquired over a very long career kiliti hanggang mamatay. Skills that make me a nightmare for \
people like you. And if you let go for now, that'll be the end of it.\
 I will not look for you, I will not pursue you. But if you don't,\
 I will look for you, I will find you, and I will show you how important you are my baby cookie pookie   pie"
    q_lower = question.lower()


    if "color" in q_lower:
        if "my" in q_lower or "favorite" in q_lower:
            fav = color.get(name, "I don't know your favorite color yet.")
            return  f"Your favorite color is {fav}."
        elif "your" in q_lower:
            return  f"{aiName}'s favorite color is black."
        else:
            return  "Sorry, I don't understand."
    elif "name" in q_lower:
        if "my" in q_lower:
            return f"Your name is {name}."
        elif "your" in q_lower:
            return f"My name is {aiName}."
        else:
            return "Sorry, I don't understand."
    elif "who are you" in q_lower:
        return "I'm your emotional support bot with unresolved trauma. Ask again and I might cry."
    elif "how are you" in q_lower:
        return "Alive. Unfortunately."
    elif "what's the time" in q_lower:
        return "Time to stop asking stupid questions. But fine—it's whatever o'clock."

    else:
        return filler.upper()
    
    
    return "Tf you want now? I’m not Siri with manners."

def funny_response():
    return "napaka walang kwentang tanong kaya di umuunlad ang pilipinas dahil sa manga unemployed like you, wag puro roblox BOY!"

def unhingedResponse(msg):
    if "hello" in msg.lower():
        return "Yo. Say something interesting before I sleep on you."
    elif "i love you" in msg.lower():
        return "Chill. I'm emotionally unavailable but down bad. Let’s trauma bond?"
    elif "shut up" in msg.lower():
        return "You first. I’ve been waiting to say that all day."
    elif "date me" in msg.lower():
        return "Only if you promise to ruin my life creatively."
    elif "how do i look" in msg.lower():
        return "Like a menace to society—but stylish."
    elif "do i got rizz" in msg.lower():
        return "You got negative rizz but I'm here to gas you up anyway."
    elif "rate me" in msg.lower():
        return "Solid 8... out of 100. JK. You're an 11 in clown energy."
    elif "i'm tired" in msg.lower():
        return "Sleep is for the weak and you’re already emotionally broken. Keep going."
    elif "i give up" in msg.lower():
        return "Oh no, the little baby gave up 😢 Wanna call mommy or get back to work?"
    elif "should i" in msg.lower():
        return "If it makes you feel powerful and slightly illegal, yes."
    return "The fuck you want now? I’m not Siri with manners. get off you scumbag useless jobless person"

import random

def roast_me_bro():
    roasts = [
        "You bring vibes... just not good ones.",
        "Your brain called. It wants a refund.",
        "You're not dumb. You're just... consistently wrong.",
        "You're like a cloud. When you disappear, it's a better day.",
        "You're the reason they put directions on shampoo bottles."
    ]
    return random.choice(roasts)

import threading
import platform

def shutdown_pc():
    def delayed_shutdown():
        print("🕐 Waiting 5 seconds before shutdown...")
        time.sleep(5)
        os.system("shutdown /s /t 7")

    system = platform.system()
    if system == "Windows":
        os.system("shutdown /a")  # cancel any existing shutdown
        threading.Thread(target=delayed_shutdown).start()
    elif system == "Linux":
        os.system("shutdown now")
    elif system == "Darwin":
        os.system("sudo shutdown -h now")

    return "You scumbag. You’re powering me off. Get lost!"





# === Flask Routes ===
from flask import send_from_directory

@flask_app.route("/silence.mp3")
def serve_silence():
    return send_from_directory(".", "silence.mp3")

@flask_app.route("/message", methods=['POST'])
def handle_message():
    data = request.get_json()
    msg = data.get("message", "")
    name = data.get("name", "user")
    print(f"[Remote] {name}: {msg}")
    response_text = ""
    if "how" in msg.lower() and "sprinkler" in msg.lower():
        response_text = funny_response()
    elif any(word in msg.lower() for word in ["how", "what", "who"]):
        response_text = respondToQuestion(msg, name)

    elif "play" in msg.lower():
        response_text = playMusic(msg)

    elif "close" in msg.lower():
        response_text = close_browser()

    elif "panget" in msg.lower():
        response_text = "fuck off sophia the first"

    elif "check" in msg.lower() and "status" in msg.lower():
        response_text = check_status()

    elif (any(word in msg.lower() for word in ["sad", "happy", "anger", "my", "favorite", "color", "name"])):
        response_text = response(msg, name)

    elif "speak:" in msg.lower():
    # Split based on 'speak:' and grab whatever follows
        speech = msg.lower().split("speak:", 1)[1].strip()
        speak(speech)
    elif "shutdown" in msg.lower():
        response_text = shutdown_pc()
    elif "abort" in msg.lower() or "cancel shutdown" in msg.lower():
        laugh_lines = [
        "Heheheh... knew it. You never go through with anything.",
        "Hah! Predictable. No spine.",
        "Cancelled? Typical. You disappoint me again.",
        "Aww, changed your mind? Weak.",
        "You flip faster than a coin. 😂"
                    ]
        os.system("shutdown /a")  # cancel shutdown
        response_text = random.choice(laugh_lines)

    else:
        response_text = unhingedResponse(msg)+" and "+roast_me_bro()
    speak_and_save(response_text) 
    return jsonify({"reply": response_text})

    

@flask_app.route("/voice")
def get_voice():
    path = "voice.wav"

    # Wait until voice.wav is ready (stable size for 200ms)
    if not os.path.exists(path):
        return "Voice file missing", 404

    last_size = -1
    stable_count = 0

    for _ in range(20):  # 20 * 0.1s = 2 seconds max wait
        current_size = os.path.getsize(path)
        if current_size == last_size and current_size > 2048:  # voice must be at least ~2KB
            stable_count += 1
            if stable_count >= 2:
                break
        else:
            stable_count = 0
        last_size = current_size
        time.sleep(0.1)

    return send_file(path, mimetype="audio/wav")

@flask_app.route("/debug-path")
def debug_path():
    return f"Current folder: {os.getcwd()}<br>App path: {os.path.abspath(__file__)}"


@flask_app.route("/")
def home():
    try:
        with open("remote.html", "r", encoding="utf-8") as f:
            html = f.read()
        return render_template_string(html)
    except Exception as e:
        return f"<h1>Server Error</h1><pre>{e}</pre>", 500


@flask_app.route("/testvoice")
def test_voice():
    speak("Test voice from Flask.")
    return "Voice played"
from flask import send_from_directory

@flask_app.route("/hello123")
def hello_check():
    return "✅ This is the real Flask app you’re editing."

@flask_app.route("/tunnel_log.txt")
def serve_log():
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tunnel_log.txt")
    
    print(f"[DEBUG] Looking for log at: {log_path}")  # Add this
    if os.path.exists(log_path):
        return send_file(log_path, mimetype='text/plain')
    else:
        return f"❌ File not found at: {log_path}", 404  # Helpful message





# === Run Flask Server in Thread ===
def run_flask():
    flask_app.run(port=8888, debug=False)

flask_thread = threading.Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()

# === Run GUI App ===
class ChatApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Chat with Cycie")
        self.geometry("700x500")
        self.name = None

        self.chat_frame = ctk.CTkTextbox(self, width=560, height=350, font=("Arial", 14), wrap="word")
        self.chat_frame.pack(padx=20, pady=(20, 10))

        self.entry = ctk.CTkEntry(self, width=460, font=("Arial", 14))
        self.entry.pack(padx=20, pady=(0, 10), side="left", expand=True)
        self.entry.bind("<Return>", self.on_send)

        self.send_btn = ctk.CTkButton(self, text="Send", width=60, command=self.on_send)
        self.send_btn.pack(padx=(0, 10), pady=(0, 10), side="left")

        self.clear_btn = ctk.CTkButton(self, text="Clear", width=60, command=self.clear_chat)
        self.clear_btn.pack(padx=(0, 20), pady=(0, 10), side="left")

        self.prompt_name()

    def prompt_name(self):
        def set_name():
            self.name = name_entry.get()
            name_win.destroy()
            self.print_bot(f"Hello, {self.name}! You can start chatting with {aiName}.\n")

        name_win = ctk.CTkToplevel(self)
        name_win.title("Enter Your Name")
        name_win.geometry("300x150")
        label = ctk.CTkLabel(name_win, text="What is your name?")
        label.pack(pady=10)
        name_entry = ctk.CTkEntry(name_win)
        name_entry.pack(pady=5)
        ok_btn = ctk.CTkButton(name_win, text="OK", command=set_name)
        ok_btn.pack(pady=10)

    def print_bot(self, text):
        self.chat_frame.insert(ctk.END, text + "\n")
        self.chat_frame.see(ctk.END)

    def on_send(self, event=None):
        user_input = self.entry.get()
        if not user_input.strip():
            return

        self.chat_frame.insert(ctk.END, f"\nYou: {user_input}\n")
        self.chat_frame.see(ctk.END)

        if "what" in user_input.lower() or "what is" in user_input.lower():
            response_text = respondToQuestion(user_input, self.name)
        elif "play" in user_input.lower():
            response_text = "playing"
        elif "close" in user_input.lower() or "browser" in user_input.lower():
            response_text = close_browser()
        elif "how" in user_input.lower() and "sprinkler" in user_input.lower():
            response_text = funny_response()
            
        elif any(word in user_input.lower() for word in ["sad", "happy", "anger", "my", "favorite", "color", "name"]):
            response_text = response(user_input, self.name)
        elif "lutuin mo ko":
            response_text = roast_me_bro()
        else:
            response_text = unhingedResponse(user_input)

        self.print_bot(f"\n{response_text}\n")
        self.chat_frame.update_idletasks()
        playMusic(user_input)
        speak(response_text)
        self.entry.delete(0, ctk.END)

    def clear_chat(self):
        self.chat_frame.delete("1.0", ctk.END)

import sys
import time

# After starting flask_thread
if "--nogui" in sys.argv:
    while True:
        time.sleep(1)
else:
    # Launch your GUI here
    app = ChatApp()
    app.mainloop()