f = open("text.txt", "r+")

f.write("I am Learning Python!!!")

f.seek(0)
print(f.read())

f.close()