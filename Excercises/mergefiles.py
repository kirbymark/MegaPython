import datetime
import glob2

filename = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".txt"
print(filename)

print(glob2.glob("file*.txt"))

with open(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".txt","w") as file:
    for read_file in glob2.glob("file*.txt"):
        with open(read_file,"r") as f:
            file.write(f.read() + "\n")
