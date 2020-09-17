import json

def company_list():

    # Load data from file
    with open('actions/companies.json') as file:
        data = json.load(file)

    # Create list and add company names
    company_list = []
    for company in data:
        company_list.append (company)

    # Return the list
    return company_list


def company_details(company_name):

    # Load data from file
    with open('actions/companies.json') as file:
        data = json.load(file)

    # Check if company_name exists, otherwise return an error
    if company_name not in data:
        return None

    # Return the data for that specific company as a dictionary
    company_data = data[company_name]
    return company_data

#print (company_list())
#company_data = company_details("DPD")
#print (company_data['email_address'])