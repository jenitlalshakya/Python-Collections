def factorial(n):
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n-1)

def main():
    num = int(input("Enter any number: "))
    print(f"Factorial of {num} is: {factorial(num)}")


if __name__ == "__main__":
    main()