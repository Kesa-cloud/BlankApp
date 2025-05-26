values = []

for i in range(5):
    value = float(input("Enter value {i + 1}:")) # looping part
    values.append(value)

average = sum(values) / len(values) # formula for avg
print(f"Average of values = {average:.2f}")