file=open("fruits.txt",'r')
content = file.readlines()
content = ([i.rstrip("\n") for i in content])
for i in content:
    print(i)
    
file.close()
