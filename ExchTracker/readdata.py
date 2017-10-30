import csv
with open('export-EtherPrice.csv', 'r') as f:
    reader = csv.reader(f)
    ethdata = list(reader)

print(type(ethdata))
for i in ethdata:
    print(i[0] + " " + i[2])

print(len(ethdata))
#    print(i[3])
