class student:
    def __init__(self, name, marks):
        self.name = name
        self.marks = marks

    @staticmethod # used to make a class without any parameters
    def hello():
        print("Hello")

    def get_avg(self):
        sum = 0
        for val in self.marks:
            sum += val
        print(f"Hi, {self.name}. Your average is: {sum / 3}")

s1 = student("Trump", [99, 98, 97])
s1.get_avg()
s1.hello()

s1.name = "Tony" # we can manipulate class objects
s1.get_avg()