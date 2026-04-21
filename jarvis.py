# ── IMPORTS ───────────────────────────────────────────────────
import speech_recognition as sr   # Converts your voice to text
import pyttsx3                     # Makes Jarvis speak out loud
import os                          # Runs system commands
import webbrowser                  # Opens websites in your browser
import sys                         # Used to exit the program
import time                        # Used for waiting/delays
from openai import OpenAI          # Connects to ChatGPT


# ── CHATGPT SETUP ─────────────────────────────────────────────
OPENAI_API_KEY = "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"  # Paste your key here

client = OpenAI(api_key=OPENAI_API_KEY)  # Create the ChatGPT connection

# Stores the full conversation so Jarvis remembers what was said
chat_history = [
    {
        "role": "system",  # This is Jarvis's personality/instructions
        "content": (
            "You are Jarvis, a smart and helpful AI assistant. "
            "You speak like the Jarvis from Iron Man — professional, concise, and call the user 'sir'. "
            "Keep answers short and spoken-friendly — no bullet points, no markdown, no long paragraphs. "
            "Just clear, natural speech that sounds good out loud."
        )
    }
]


# ── ASK CHATGPT ───────────────────────────────────────────────
def ask_chatgpt(question):

    try:
        chat_history.append({"role": "user", "content": question})  # Add question to history

        # Send full conversation to ChatGPT and get a reply
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",   # The AI model being used
            messages=chat_history,   # Send the whole conversation
            max_tokens=150,          # Max length of the reply
            temperature=0.7          # How creative the reply is (0=safe, 1=creative)
        )

        reply = response.choices[0].message.content.strip()  # Extract the reply text

        chat_history.append({"role": "assistant", "content": reply})  # Save reply to history

        return reply  # Send reply back to be spoken

    except Exception as e:
        print(f"[CHATGPT ERROR]: {e}")  # Print error if something goes wrong
        return "I'm having trouble connecting to my brain right now, sir."


# ── SPEAK ─────────────────────────────────────────────────────
def speak(text):

    print(f"[JARVIS]: {text}")  # Print what Jarvis is saying

    try:
        engine = pyttsx3.init()               # Create a fresh voice engine
        engine.setProperty("rate", 165)       # Set speaking speed

        voices = engine.getProperty("voices") # Get list of available voices
        for v in voices:
            if "david" in v.name.lower():     # Look for the David voice
                engine.setProperty("voice", v.id)  # Use it if found
                break

        engine.say(text)          # Queue the text to be spoken
        engine.runAndWait()       # Actually speak it out loud
        engine.stop()             # Clean up the engine after speaking

    except Exception as e:
        print("Voice error:", e)  # Print error if voice fails


# ── LISTEN ────────────────────────────────────────────────────
def listen(prompt="Listening..."):

    r = sr.Recognizer()  # Create a speech recognizer

    with sr.Microphone() as source:       # Open the microphone
        print(f"[MIC] {prompt}")          # Show listening status
        r.adjust_for_ambient_noise(source, duration=0.3)  # Filter background noise

        try:
            # Record audio — wait up to 6 seconds for speech
            audio = r.listen(source, timeout=6, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            return ""  # Return empty if no speech heard

    try:
        text = r.recognize_google(audio)  # Send audio to Google to convert to text
        print(f"[YOU]: {text}")           # Print what was heard
        return text.lower()               # Return text in lowercase
    except:
        return ""  # Return empty if speech wasn't understood


# ── GOOGLE SEARCH ─────────────────────────────────────────────
def google_top_result(query):

    speak("Working on it sir.")

    # btnI=1 is Google's "I'm Feeling Lucky"
    # It skips the search page and opens the #1 result directly
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}&btnI=1"
    webbrowser.open(url)  # Open the top result in browser


# ── OPEN APP ──────────────────────────────────────────────────
def open_app(app):

    speak("Working on it sir.")
    os.system(f"start {app}")  # Tell Windows to open the app by name


# ── EXECUTE COMMAND ───────────────────────────────────────────
def execute(command):

    # Check if user wants to quit
    if any(x in command for x in ["stop", "exit", "quit"]):
        speak("Goodbye sir.")
        sys.exit()  # Close the program

    # If command contains search words → open top Google result
    elif any(x in command for x in ["search", "google", "look up"]):
        # Strip all search-related words to get just the topic
        query = (command
                 .replace("search google for", "")
                 .replace("search google", "")
                 .replace("search for", "")
                 .replace("search up", "")
                 .replace("look up", "")
                 .replace("search", "")
                 .replace("google", "")
                 .strip())

        if query:
            google_top_result(query)  # Search if we got a topic
        else:
            # Ask what to search if nothing was said after "search"
            speak("What would you like me to search for, sir?")
            q = listen("Waiting for search query...")
            if q:
                google_top_result(q)

    # If command contains "open" → launch an app
    elif "open" in command:
        app = command.replace("open", "").strip()  # Get the app name
        if app:
            open_app(app)
        else:
            speak("What should I open, sir?")

    # Anything else → send to ChatGPT for a smart answer
    else:
        speak("Let me think about that, sir.")
        answer = ask_chatgpt(command)  # Ask ChatGPT
        speak(answer)                  # Speak the answer out loud


# ── MULTI COMMAND SUPPORT ─────────────────────────────────────
def parse(command):
    # Split on "and" so "open chrome and search cats" works as two commands
    parts = [p.strip() for p in command.split(" and ")]
    for p in parts:
        execute(p)  # Run each part one by one


# ── MAIN LOOP ─────────────────────────────────────────────────
def main():

    speak("Jarvis is online.")  # Startup message

    while True:  # Keep running forever until "stop" is said

        wake = listen("Waiting for Jarvis...")  # Listen for wake word

        if not wake or "jarvis" not in wake:
            continue  # Ignore if "jarvis" wasn't said

        speak("Sir")  # Respond to wake word

        command = listen("Waiting for command...")  # Listen for the command

        if not command:
            speak("I didn't catch that, sir.")  # Nothing was heard
            continue

        parse(command)  # Process and run the command


# ── RUN ───────────────────────────────────────────────────────
if __name__ == "__main__":
    main()  # Start Jarvis