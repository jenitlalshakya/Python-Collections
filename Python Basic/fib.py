def fib(n):
    # Generate fibonacci series upto n number and
    # return the series of fibonacci

    if(n <= 0):
        return []
    elif(n == 1):
        return [0]
    
    series = [0, 1]
    a, b = 0, 1

    for i in range (2, n):
        fib = a + b
        series.append(fib)
        a = b
        b = fib
    
    return series

num = int(input("Enter number of series: "))
print(f"Fibonacci Series is: {fib(num)}")