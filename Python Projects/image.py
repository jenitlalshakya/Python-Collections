from PIL import Image

ASCII_CHARS = "@%#*+=-:. "
def resize_image(image, new_width=100):
    width, height = image.size
    aspect_ratio = height / width
    new_height = int(new_width * aspect_ratio * 0.55)
    return image.resize((new_width, new_height))

def grayify(image):
    return image.convert("L")

def pixels_to_ascii(image):
    pixels = image.getdata()
    ascii_str = "".join(ASCII_CHARS[pixel * len(ASCII_CHARS) // 256] for pixel in pixels)
    return ascii_str

def image_to_ascii(path, new_width=100):
    try:
        image = Image.open(path)
    except Exception as e:
        print("Unable to open image file,", e)
        return
    
    image = resize_image(image, new_width)
    image = grayify(image)

    ascii_str = pixels_to_ascii(image)
    img_width = image.width
    ascii_img = "\n".join(ascii_str[i:i+img_width]
    for i in range(0, len(ascii_str), img_width))
    print(ascii_img)

path = input("Enter the path to your image file: ")
image_to_ascii(path)