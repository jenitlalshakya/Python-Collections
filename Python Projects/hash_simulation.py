def simple_hash(text):
    hash_value = 0

    for char in text:
        hash_value += ord(char)
        hash_value = hash_value * 7
        hash_value = hash_value % 99999999

    return hex(hash_value)

if __name__ == "__main__":
    password = input("Enter password: ")
    hashed = simple_hash(password)

    print(f"Hashed Password: {hashed}")