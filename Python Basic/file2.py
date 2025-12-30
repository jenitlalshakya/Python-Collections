with open("practice.txt", "w") as f:
    f.write("Hi everyone\nWe are learning File I/O\nusing Java.\nI like programming in Java.")

with open("practice.txt", "r") as f:
    data = f.read()

new_data = data.replace("Java", "Python")
print(new_data)

with open("practice.txt", "w") as f:
    f.write(new_data)

print("File created")