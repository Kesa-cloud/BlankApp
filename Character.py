def check_case(character):
    if character.isupper():
        return "Uppercase"
    elif character.islower():
        return "Lowercase"
    else:
        return "Is not in the alphabet"

char = input("Enter a character: ")
print(f"This {char} is {check_case(char)}")
