def isPalindrome(num):
    original = num
    reverse = 0

    if(num < 0):
        return False
    
    while(num > 0):
        digit = num % 10
        reverse = reverse * 10 + digit
        num //= 10

    return original == reverse

num = int(input("Enter number: "))

if(isPalindrome(num)):
    print(f"{num} is a Palindrome.")
else:
    print(f"{num} is not a Palindrome.")