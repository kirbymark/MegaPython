ctemps=[10,-20,-289,32,123,100]

def temp_c_to_f(celsius):
    if float(celsius) < -273.15:
        print("The lowest possible temperature that physical matter can reach is -273.15 °C")
    else:
        fahrenheit = celsius * 9 / 5 + 32
        return fahrenheit

def writer(temps):
    with open("output.txt",'w') as file:
        for t in ctemps:
            if t > -273.15:
                file.write(str(temp_c_to_f(t))+"\n")

writer(ctemps)
