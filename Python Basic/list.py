marks = [75, 48, 32, 90, 100, 12]
copy = marks[:]

print(copy)
copy[2] = 50
print(copy)

# append
copy.append(47)
print(copy)

# sort
copy.sort()
print(copy)

# reverse sort
copy.sort(reverse = True)
print(copy)

# reverse
marks.reverse()
print(marks)

# insert
copy.insert(2, 80)
print(copy)

# remove
copy.remove(75)
print(copy)

# remove by index
copy.pop(4)
print(copy)