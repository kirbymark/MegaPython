lines=["Line 11","Line 12","Line 13"]
with open("example.txt",'a+') as file:
    file.seek(0)
    content = file.readlines()
    content=[i.rstrip("\n") for i in content]
    for i in content:
        print(i)
    for i in lines:
        file.write(i+"\n")
