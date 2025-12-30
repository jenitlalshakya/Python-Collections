marks = {}

x = int(input("Enter physics marks: "))
marks.update({"physics": x})

x = int(input("Enter Maths Marks: "))
marks.update({"maths": x})

x = int(input("Enter chemistry marks: "))
marks.update({"chemistry": x})

print("\n", marks)