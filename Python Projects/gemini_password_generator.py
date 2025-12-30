import random
import string

SAFE_SYMBOLS = "!@#$%^&*_-+="

def generate_password(length=12,  include_uppercase=True, include_lowercase=True, include_digits=True, include_symbols=True):
    """Generates a strong password."""

    characters = ""
    if include_uppercase:
        characters += string.ascii_uppercase
    if include_lowercase:
        characters += string.ascii_lowercase
    if include_digits:
        characters += string.digits
    if include_symbols:
        characters += SAFE_SYMBOLS

    if not characters:  # If no character sets are selected, return an empty string or raise an error
        return ""  # Or raise ValueError("At least one character set must be selected.")
    password = ''.join(random.choice(characters) for i in range(length))
    return password

if __name__ == "__main__":
    password = generate_password()
    print(f"Generated password:\n{password}")
