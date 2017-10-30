file=open("example.txt",'w')
lines = ["Line 1","Line 2","Line 3","Line 4","Line 5"]
for i in lines:
    file.write(i+"\n")
file.close
