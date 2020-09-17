import json

with open('companies.json') as file:
  data = json.load(file)

print(data)

#print (data["Example plc"])
#print (data["Example plc"]["contact_method"])

#if "Example pld" in data:
#    print ("Exists")
#else:
#    print ("Does not exist")

for company in data:
    print (company)


