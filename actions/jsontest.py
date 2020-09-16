import json

with open('companies.json') as file:
  data = json.load(file)

print(data)

print (data["Example plc"])
print (data["Example plc"]["contact_method"])


