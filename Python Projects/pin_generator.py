import secrets
import string


DIGITS = string.digits


def generate_pin(length: int, count: int = 1, allow_repeats: bool = True):
    if length < 4:
        raise ValueError("PIN length must be at least 4 digits.")
    if count < 1:
        raise ValueError("Count must be at least 1.")
    if not allow_repeats and length > len(DIGITS):
        raise ValueError("Cannot generate a non-repeating PIN longer than 10 digits.")

    pins = []
    for _ in range(count):
        if allow_repeats:
            pin = ''.join(secrets.choice(DIGITS) for _ in range(length))
        else:
            pool = list(DIGITS)
            pin = ''.join(secrets.choice(pool.pop(secrets.randbelow(len(pool)))) for _ in range(length))
        pins.append(pin)
    
    return pins


def main():
    try:
        length = int(input("Enter PIN length (default 4): ").strip() or 4)
        count = int(input("How many PINs to generate (default 1): ").strip() or 1)
        allow_repeats_input = input("Allow repeated digits? [y/n]: ").strip().lower() or "y"
        allow_repeats = allow_repeats_input in ("y", "yes")
    except ValueError:
        print("❌ Please enter a valid number.")
        return

    try:
        pins = generate_pin(length=length, count=count, allow_repeats=allow_repeats)
    except ValueError as e:
        print(f"Error: {e}")
        return

    print("\nGenerated PIN(s):")
    for i, p in enumerate(pins, start=1):
        print(f"{i}: {p}")


if __name__ == "__main__":
    main()