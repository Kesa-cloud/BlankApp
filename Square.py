def calculate_perimeter(side_lenth):
    return side_lenth * 4 #side by 4
def calculate_area(side_length):
    return side_length ** 2 #Side squared
side = float(input("Enter side length os square:"))
print(f"Perimeter = {calculate_perimeter(side)}")
print(f"Area = {calculate_area(side)}")