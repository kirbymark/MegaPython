def divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return "You are trying to divide by zero"


print(divide(2, 0))
