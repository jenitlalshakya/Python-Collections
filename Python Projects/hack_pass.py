import itertools
import string
import time
import figlet

charset = string.ascii_letters + string.digits + "!@#$"
target = "Aa"

start = time.time()
attempts = 0

for attempt in itertools.product(charset, repeat=len(target)):
    guess = ''.join(attempt)
    attempts += 1
    if guess == target:
        print(f"Password found: {guess} in {attempts} tries and {time.time() - start:.2f} seconds!")
        break

figlet.ascii_art_generator()