def string_len(string):
    if type(string) == int:
        return "Sorry, integers don't have length"
    elif type(string) == float:
        return "Sorry, floats don't have length"
    else:
        return len(string)


print(string_len("Hello Mark"))
print(string_len(10))
print(string_len(1.5))
