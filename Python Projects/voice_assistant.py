import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import os

listener = sr.Recognizer()
engine = pyttsx3.init()

def talk(text):
    engine.say(text)
    engine.runAndWait()

def take_command():
    try:
        with sr.Microphone() as source:
            print("🎤 Listening...")
            voice = listener.listen(source)
            command = listener.recognize_google(voice)
            command = command.lower()
            print("You said: ", command)
    except:
        command = ""
    
    return command

def run_assistant():
    command = take_command()

    if "time" in command:
        time = datetime.datetime.now().strftime("%I:%M %p")
        print("⌚ Time:", time)
        talk("The time is " + time)

    elif "search" in command:
        query = command.replace("search", "")
        print("🔍 Searching:", query)
        talk("Searching for " + query)
        pywhatkit.search(query)

    elif "open notepad" in command:
        talk("Opening Notepad")
        os.system("notepad.exe")

    elif "stop" in command or "exit" in command:
        talk("Goodbye!")
        exit()

    else:
        talk("I didn't understand. Please say it again.")

while True:
    run_assistant()