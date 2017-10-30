file=open("output.txt",'w')
numbers = [1,2,3]
for i in numbers:
    file.write(str(i)+"\n")
file.close
