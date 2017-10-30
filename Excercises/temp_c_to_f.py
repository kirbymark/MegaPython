def temp_c_to_f(celsius):
    if float(celsius) < -273.15:
        print("The lowest possible temperature that physical matter can reach is -273.15 °C")
    else:
        fahrenheit = celsius * 9 / 5 + 32
        return fahrenheit


print(temp_c_to_f(10))
print(temp_c_to_f(-10))
print(temp_c_to_f(-273))
print(temp_c_to_f(-274))
