file=open("example.txt",'a')
lines = ["Line 6","Line 7","Line 8","Line 9","Line 10"]
for i in lines:
    file.write(i+"\n")
file.close
