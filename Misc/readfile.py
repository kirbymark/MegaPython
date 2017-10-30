file=open("example.txt",'r')
content = file.read()
print(content)
file.seek(0)
content = file.readlines()
print(content)
content1=[i.rstrip("\n") for i in content]
print(content1)
file.close()
