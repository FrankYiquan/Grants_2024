import json
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import csv
import requests
from datetime import datetime
import re 
import pandas as pd
from get_data import get_data_openAlex

# Function to get data from json  data file get from openAlex
#data: open alex data, which is stored in brandeis_2024.json
# funder_info: funder name + ID
def extract_information(data, funder_info):
    extracted_data = []
    
    # Loop through each result in the data
    for result in data:
        grants = []
        investigator_info = None

        # Loop through each investigator in the result
        # for each author(investigator) in author listst, get their info and 
        for investigator in result.get('authorships', []):
            position = investigator.get('author_position', '')
            author = investigator.get('author', '')
            # Check if the investigator is the first author and is affiliated with Brandeis University
            if position == 'first':
                for institution in investigator.get('institutions', []):
                    if institution.get('display_name', '') == 'Brandeis University':
                        author_name = author.get('display_name')
                        Id_1 = get_user_identifier(author_name, filename='data/20240805_reseracherIDs.csv')
                        investigator_info = {
                            'investigatorId': Id_1,
                            'investigatorIdType': 'primaryId'
                        }
                        # If the investigator is found, break out of the loop
                        break
                # Break out of the outer loop if we already have investigator info
                if investigator_info:
                    break
        # Loop through each grant in the result
        for grant in result.get('grants', []):
            funder_display_name = grant.get('funder_display_name', '')

             # Skip grants from CERN if CERN is one of the funders among the grants
            if funder_display_name == "CERN":
                grants = []  # Clear the grants list if CERN is found
                break 

            if funder_display_name in funder_info:
                award_id = grant.get('award_id', '')
                if isinstance(award_id, int):
                    award_id = str(award_id)
                # Reformat award ID for NSF
                if funder_display_name == 'National Science Foundation':
                    award_id = reformat_award_id(award_id)
                
                # Create a dictionary with grant information
                grant_info = {
                    'grantId': award_id,
                    'funderCode': funder_info[funder_display_name],
                    'funderAgency': funder_display_name
                }

                # Add start date and amount for NSF grants
                if funder_display_name == 'National Science Foundation':
                    nsf_data = get_nsf_award_data(award_id)
                    grant_info.update(nsf_data)

                if all(value not in ('', 'Unknown', None) for value in grant_info.values()):
                    # Attach investigator info to each grant if available
                    if investigator_info and all(value not in ('', 'Unknown', None) for value in investigator_info.values()):
                        grant_info.update(investigator_info)

                    grants.append(grant_info)

        # Append the grants to the extracted data
        if grants:
            extracted_data.append({'grants': grants})

    return extracted_data

# Function to reformat award ID for NSF
def reformat_award_id(award_id):
    if not isinstance(award_id, str):
        return None
    match = re.search(r'\d+', award_id)
    if match:
        return match.group(0) 
    else:
        return None  

# Function to format date
def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%m/%d/%Y')
        return date_obj.strftime('%Y%m%d')
    except ValueError:
        return 'Unknown'

# Function to load funder info from a CSV file
def load_funder_info(filename):
    funder_info = {}
    with open(filename, 'r', encoding='ISO-8859-1') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            funder_display_name = row['Funder_display_name']
            funder_code = row['funder_code']
            funder_info[funder_display_name] = funder_code
    return funder_info

# Function to get NSF award data by using NSF API
def get_nsf_award_data(award_id):
    api_url = f'http://api.nsf.gov/services/v1/awards/{award_id}.json'
    try:
        response = requests.get(api_url)
        response.raise_for_status() 
        json_data = response.json()

        awards = json_data.get('response', {}).get('award', [])

        if awards:
            award_info = awards[0]
            start_date = award_info.get('startDate', '')
            amount = award_info.get('fundsObligatedAmt', '')
            title= award_info.get('title', '')

            return {
                'startDate': format_date(start_date), 
                'amount': str(amount),
                'title': title
            }
        else:
            return {
                'startDate': 'Unknown',
                'amount': '0',
                'title': 'Unknown'
            }

    except Exception as e:
        print(f"Error: {e}")
        return {
            'startDate': 'Unknown',
            'amount': '0'
        }

# Function to split name into first and last name
def split_name(name):
    parts = name.split()
    return parts

# Function to get last name
def get_last(name):
    name = split_name(name)
    return name[-1]

# Function to get first name
def get_first(name):
    name = split_name(name)
    return name[0]

# Function to get user identifier  
def get_user_identifier(researcher_name, filename='data/20240805_reseracherIDs.csv'):
    try:
        # Load the CSV file
        df = pd.read_csv(filename, dtype={'User Primary Identifier': str})
        matching_rows = df[df['Researcher Last Name'] == get_last(researcher_name)]
        # If there are multiple matching rows, filter by first name
        if not matching_rows.empty:
            if len(matching_rows) > 1:
                first_name = get_first(researcher_name)
                matching_rows = matching_rows[matching_rows['Researcher First Name'] == first_name]

            if len(matching_rows) == 1:
                user_id = matching_rows.iloc[0]['User Primary Identifier']
                return user_id
            else:
                print("Multiple or no matches found after additional filtering by first name.")
                return None
        else:
            return None
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return None
    except Exception as e:
        print(f"Error reading the file {filename}: {e}")
        return None


# Function to format user ID
def format_user_id(user_id):
    try:
        numeric_id = int(float(user_id))
        return str(numeric_id)
    except ValueError:
        print(f"Error converting user ID: {user_id}")
        return None
# Function to convert dictionary to XML    
def dict_to_xml(data):
    root = ET.Element('grants')
    root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    root.set('xsi:noNamespaceSchemaLocation', 'schema1.xsd')
    for item in data:
        for grant in item['grants']:
            grant_elem = ET.SubElement(root, "grant")

            award_id_elem = ET.SubElement(grant_elem, "grantId")
            award_id_elem.text = grant.get('grantId', 'N/A')
            
            funder_code_elem = ET.SubElement(grant_elem, "funderCode")
            funder_code_elem.text = grant.get('funderCode', 'N/A')

            funder_display_name_elem = ET.SubElement(grant_elem, "funderAgency")
            funder_display_name_elem.text = grant.get('funderAgency', 'N/A')
        
            if 'startDate' in grant:
                start_date_elem = ET.SubElement(grant_elem, "startDate")
                start_date_elem.text = grant.get('startDate', 'N/A')

            if 'amount' in grant:
                amount_elem = ET.SubElement(grant_elem, "amount")
                amount_elem.text = grant.get('amount', 'N/A')

            if 'title' in grant:
                titel_elem = ET.SubElement(grant_elem, 'grantName')
                titel_elem.text = grant.get('title', 'N/A')

            if 'investigatorId' in grant:
                investigator_elem = ET.SubElement(grant_elem, 'investigator')

                investigatorId_elem = ET.SubElement(investigator_elem, 'investigatorId')
                investigatorId_elem.text = grant.get('investigatorId', 'N/A')
                
                investigatorIdType_elem = ET.SubElement(investigator_elem, 'investigatorIdType')
                investigatorIdType_elem.text = grant.get('investigatorIdType', 'N/A')
                
    return ET.ElementTree(root)

# Function to pretty print XML
def pretty_print_xml(tree):
    rough_string = ET.tostring(tree.getroot(), 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

# Input file names and the base url to used to get data from opealex
base_url = input("Please enter the base URL: ")
openAlex_file_name = input("Please enter the output JSON file name (with .json extension and relative path): ")

# Get data from openAlex
get_data_openAlex(base_url, openAlex_file_name).get_data_openAlex()

funder_info = load_funder_info('data/funder_info.csv')

with open(openAlex_file_name, 'r') as json_file:
    data = json.load(json_file)

# Extract information from the JSON data
extracted_data = extract_information(data, funder_info)

# Convert extracted data to XML
xml_tree = dict_to_xml(extracted_data)

# Pretty print the XML
pretty_xml = pretty_print_xml(xml_tree)

output_file_name = "output.xml"

with open(output_file_name, 'w', encoding='utf-8') as output_file:
    output_file.write(pretty_xml)

print(f"XML data successfully written to {output_file_name}")


# 1) get data from openAlex API
