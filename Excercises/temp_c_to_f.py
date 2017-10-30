def temp_c_to_f(celsius):
    if float(celsius) < -273.15:
        print("The lowest possible temperature that physical matter can reach is -273.15 °C")
    else:
        fahrenheit = celsius * 9 / 5 + 32
        return fahrenheit


ctemps=[10,-20,-289,100]
for t in ctemps:
    print(temp_c_to_f(t))
