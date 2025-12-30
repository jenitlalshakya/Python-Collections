import math
import string

SAFE_SYMBOLS = "!@#$%^&*_-+="

def get_charset_size(password: str) -> int:
    charset = 0
    if any(c.islower() for c in password):
        charset += 26
    if any(c.isupper() for c in password):
        charset += 26
    if any(c.isdigit() for c in password):
        charset += 10
    if any(c in SAFE_SYMBOLS for c in password):
        charset += len(SAFE_SYMBOLS)

    return charset

def estimate_crack_time(password: str, guesses_per_second: float = 1e11) -> str:
    length = len(password)
    charset_size = get_charset_size(password)

    if charset_size == 0:
        return "Invalid password (no recognized characters)."

    total_combinations = charset_size ** length
    avg_guesses_needed = total_combinations / 2
    seconds = avg_guesses_needed / guesses_per_second

    units = [("years", 60 * 60 * 24 * 365),
             ("days", 60 * 60 * 24),
             ("hours", 60 * 60),
             ("minutes", 60),
             ("seconds", 1)]
    
    result = []
    for unit, unit_seconds in units:
        if seconds >= unit_seconds:
            value, seconds = divmod(seconds, unit_seconds)
            result.append(f"{int(value):,} {unit}")
    return ", ".join(result) if result else "less than 1 second"


if __name__ == "__main__":
    print("🔐 Password Crack Time Estimator")
    pwd = input("Enter a password to analyze: ").strip()
    guesses_per_sec = input("Enter guesses per second (default 1e11): ").strip()
    guesses_per_sec = float(guesses_per_sec) if guesses_per_sec else 1e11

    time_estimate = estimate_crack_time(pwd, guesses_per_sec)
    print(f"\nEstimated brute-force crack time: {time_estimate}")