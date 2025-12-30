str = input("Enter String: ")
str_1 = str[::-1]

if(str == str_1):
    print(f"{str} is a Palindrome.")
else:
    print(f"{str} is not a Palindrome.")