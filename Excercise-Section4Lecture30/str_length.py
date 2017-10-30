def string_len(string):
    if type(string) == int:
        return "Sorry, integers dont have length"
    else:
        return len(string)


print(string_len("Hello Mark"))
print(string_len(10))
