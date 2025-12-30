i = 1
while i <= 100:
    print(i)
    i += 1

# reverse
print()
j = 100
while j >= 1:
    print(j)
    j -= 1

# multiplication table
print()
num = int(input("Enter any number:"))
k = 1
while k <= 10:
    print(f"{num} X {k} = {num * k}")
    k += 1

# print(1,4,9,16,.....)
print()
nums = [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]

l = 0
while l < len(nums):
    print(nums[l])
    l += 1

# search number in tuple using while
print
tuple = (1, 4, 9, 16, 25, 36, 49, 64, 81, 100)

x = int(input("Enter number you want to search: "))
a = 0
while a < len(tuple):
    if (tuple[a] == x):
        print(f"Number found in {a} index: {tuple[a]}")
        break

    a += 1