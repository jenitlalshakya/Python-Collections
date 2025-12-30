import random
import string
from password_crack_time import estimate_crack_time


SAFE_SYMBOLS = "!@#$%^&*_-+="
MIN_LENGTH = 8
DEFAULT_LENGTH = 16


def generate_password(length=MIN_LENGTH, use_digits=True, use_symbols=True):
    characters = string.ascii_letters

    if use_digits:
        characters += string.digits
    if use_symbols:
        characters += SAFE_SYMBOLS

    if not characters:
        raise ValueError("No character set selected!")

    password = []
    if use_digits:
        password.append(random.choice(string.digits))
    if use_symbols:
        password.append(random.choice(SAFE_SYMBOLS))
    password.append(random.choice(string.ascii_lowercase))
    password.append(random.choice(string.ascii_uppercase))

    password += random.choices(characters, k=length - len(password))

    random.shuffle(password)

    return "".join(password)


if __name__ == "__main__":
    print("🔐 Password Generator")

    while True:
        try:
            length = int(input("Enter password length (default 16): ") or DEFAULT_LENGTH)
            if length < MIN_LENGTH:
                print(f"❌ Password length must be at least {MIN_LENGTH} characters. Please try again.")
                continue
            break
        except ValueError:
            print("❌ Please enter a valid number.")

    use_digits = input("Include digits? (y/n): ").lower().startswith("y")
    use_symbols = input("Include symbols? (y/n): ").lower().startswith("y")

    password = generate_password(length, use_digits, use_symbols)
    crack_time = estimate_crack_time(password)

    print(f"\n✅ Your secure password is:\n{password}")
    print(f"\n⏳ Estimated crack time: {crack_time}")
