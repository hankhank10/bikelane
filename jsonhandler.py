import json

def company_list():
    with open('actions/companies.json') as file:
        data = json.load(file)

    company_list = []
    for company in data:
        company_list.append (company)

    return company_list

