import pyfiglet

def ascii_art_generator():
    print("ASCII ART GENERATOR, Use CTRL+C to quit!")

    while True:
        try:
            text = input("Enter Text (CTRL+C to quit): ")
            ascii_art = pyfiglet.figlet_format(text)
            print(ascii_art)
            
        except KeyboardInterrupt:
            print("\nBye! Keep creating art😀")
            break

if __name__ == "__main__":
    ascii_art_generator()