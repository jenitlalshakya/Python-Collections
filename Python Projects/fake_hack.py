import time
import random
import os
import sys

messages = [
    "Bypassing firewall...",
    "Establishing secure connection...",
    "Brute forcing password hash...",
    "Uploading payload...",
    "Injecting exploit...",
    "Accessing mainframe...",
    "Decrypting files...",
    "Collecting user credentials...",
    "Elevating privileges...",
    "Tracking IP address..."   
]

def typewriter(text, delay=0.02):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def progress_bar(task, length=30):
    typewriter(task)
    for i in range(length + 1):
        bar = "#" * i + "-" * (length - i)
        sys.stdout.write(f"\r[{bar}] {int((i/length)*100)}%")
        sys.stdout.flush()
        time.sleep(random.uniform(0.05, 0.2))
    print("\n")

def fake_hack():
    os.system("cls" if os.name == "nt" else "clear")
    typewriter("Initializing hacking sequence...\n", 0.05)
    time.sleep(1)

    for msg in random.sample(messages, k=10):
        progress_bar(msg)
        time.sleep(0.5)

    typewriter("\nACCESS GRANTED ✅\n", 0.1)
    typewriter("Welcome, Agent 47...\n", 0.05)

if __name__ == "__main__":
    fake_hack()