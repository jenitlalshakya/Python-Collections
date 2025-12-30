import speech_recognition as sr
import pyttsx3
import re
import math


def speak(text):
    engine = pyttsx3.init("sapi5")
    engine.setProperty("rate", 190)
    engine.setProperty("volume", 1)
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[0].id)

    """Speak text naturally without cutting off words."""
    print(f"🗣️ {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)  # quick calibration
        print("🎙️ Speak your math expression...")
        audio = r.listen(source, timeout=3, phrase_time_limit=5)
    try:
        query = r.recognize_google(audio)
        print("👉 You said:", query)
        return query.lower()
    except sr.UnknownValueError:
        speak("Sorry, I could not understand that.")
        return None
    except sr.RequestError:
        speak("Network error. Please check your internet.")
        return None

def convert_to_expression(text):
    # Remove filler words
    fillers = ["calculate", "what is", "the", "of"]
    for f in fillers:
        text = text.replace(f, "")

    # Handle powers
    text = text.replace("to the power of", "**")
    text = text.replace("power of", "**")
    text = text.replace("power", "**")
    text = text.replace("raised to", "**")
    text = text.replace("powed", "**")

    # Basic arithmetic
    text = text.replace("plus", "+")
    text = text.replace("minus", "-")
    text = text.replace("times", "*")
    text = text.replace("multiplied by", "*")
    text = text.replace("divided by", "/")
    text = text.replace("over", "/")
    text = text.replace("into", "*")
    text = text.replace("x", "*")

    # Square, cube, roots
    if "square root" in text:
        text = text.replace("square root of", "")
        text = f"math.sqrt({text.strip()})"

    elif "cube root" in text:
        text = text.replace("cube root of", "")
        text = f"round(({text.strip()}) ** (1/3), 5)"

    elif "square" in text:
        text = text.replace("square of", "")
        text = f"({text.strip()} ** 2)"

    elif "cube" in text:
        text = text.replace("cube of", "")
        text = f"({text.strip()} ** 3)"

    # Factorial
    elif "factorial" in text:
        text = text.replace("factorial of", "")
        text = f"math.factorial(int({text.strip()}))"

    # Trigonometry
    elif "sine" in text or "sin" in text:
        text = text.replace("sine", "").replace("sin", "")
        text = f"math.sin(math.radians({text.strip()}))"

    elif "cosine" in text or "cos" in text:
        text = text.replace("cosine", "").replace("cos", "")
        text = f"math.cos(math.radians({text.strip()}))"

    elif "tangent" in text or "tan" in text:
        text = text.replace("tangent", "").replace("tan", "")
        text = f"math.tan(math.radians({text.strip()}))"

    # Logarithms
    elif "log base 10" in text or "log10" in text:
        text = text.replace("log base 10", "").replace("log10", "")
        text = f"math.log10({text.strip()})"

    elif "natural log" in text or "ln" in text:
        text = text.replace("natural log", "").replace("ln", "")
        text = f"math.log({text.strip()})"

    # Percentage
    elif "percent of" in text:
        text = text.replace("percent of", "%")
        parts = text.split("%")
        if len(parts) == 2:
            num, val = parts
            text = f"({num.strip()} / 100) * {val.strip()}"

    # Absolute value
    elif "absolute" in text or "modulus" in text:
        text = text.replace("absolute", "").replace("modulus", "")
        text = f"abs({text.strip()})"

    # Keep only safe characters unless it's math functions
    if not text.startswith(("math.", "abs(")):
        text = re.sub(r'[^0-9+\-*/(). **]', '', text)

    return text

def main():
    speak("Welcome to Voice Calculator. Please say your calculation.")
    while True:
        text = listen()
        if text is None:
            continue
        if "exit" in text or "quit" in text:
            speak("Goodbye!")
            break

        expr = convert_to_expression(text)
        print("Expression:", expr)
        try:
            result = eval(expr, {"math": math})
            print("✅ Result:", result)
            speak(f"The answer is {result}")
        except Exception as e:
            speak("Sorry, I couldn't calculate that.")
            print("Error:", e)

if __name__ == "__main__":
    main()