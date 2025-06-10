# this script retrieves funder names from a JSON file obtained via the OpenAlex API and appends any new funder names to an existing CSV file.
# 1) get all funding provider from OpenALex API
# 2) compare funder names from JSON with existing funder names in CSV ('data/funder-info.csv')
# 3) if unmatched, append to CSV

import json
import pandas as pd
from difflib import SequenceMatcher
from get_data import get_data_openAlex
import requests
import uuid
import xml.etree.ElementTree as ET
import os
import xml.dom.minidom
import csv






def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def remove_extra_blank_lines(xml_str):
    # keep only lines that are not empty or just whitespace
    lines = [line for line in xml_str.splitlines() if line.strip() != '']
    return "\n".join(lines)



# Input file names (this is only for Brandeis 2024)

year = 2018
input_file_name = 'brandeis_2024.json' #this can use to store any year (other than 2024), 2024 is just kepet for previous code.
base_url = f'https://api.openalex.org/works?filter=institutions.id:https://openalex.org/I6902469,publication_year:{year}&sort=publication_date:desc'

#check if xml file exits
xml_file = "New_Funder.xml"

# Load or create XML
if os.path.exists(xml_file):
    tree = ET.parse(xml_file)
    xml_root = tree.getroot()
else:
    xml_root = ET.Element("organization_units")
    tree = ET.ElementTree(xml_root)

#create a dictionary to store funder names and their codes
country_name_to_alpha3 = {}
with open("CountryCode.csv", newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # Assuming the CSV has columns: 'name' and 'alpha-3'
        country_name_to_alpha3[row['name'].strip().lower()] = row['alpha-3'].strip()


# get article from OpenAlex API
get_data_openAlex(base_url, input_file_name).get_data_openAlex()

csv_file_name = 'data/funder_info.csv'
# Load JSON data
with open(input_file_name, 'r') as json_file:
    data = json.load(json_file)

# Load CSV file
existing_funders_df = pd.read_csv(csv_file_name)
existing_funders = existing_funders_df['Funder_display_name'].tolist() #give a list of exiting funder names pulled from ScholarWork records

# Extract funder names from JSON
funder_data = []
for item in data:
    for grant in item.get('grants', []):
        funder_name = grant.get('funder_display_name', '')
        if funder_name:
            funder_data.append(funder_name)

# Create DataFrame of unique funder names from JSON
df = pd.DataFrame(funder_data, columns=['Funder_display_name']).drop_duplicates()

# Check for matches between JSON funders and existing CSV funders
unmatched_funders = []
similarity_threshold = 0.9

for funder in df['Funder_display_name']:
    match_found = False
    for existing_funder in existing_funders:
        if similar(funder, existing_funder) >= similarity_threshold:
            match_found = True
            break
    if not match_found:
        unmatched_funders.append(funder)

unmatched_funders_df = pd.DataFrame({
    'Funder_display_name': unmatched_funders,
    'funder_code': [None] * len(unmatched_funders)
})

# If there are unmatched funders, append them to the existing CSV
if not unmatched_funders_df.empty:

    #for each new(unmatched) funder, add id either from ROG or UUID
    for index, row in unmatched_funders_df.iterrows():
        funder_name = row['Funder_display_name']
        #search up rog first 
        url = "https://api.ror.org/organizations"
        params = {"query": funder_name}

        response = requests.get(url, params=params)
        # if funder can be found in ROG, get the id
        if response.status_code == 200:
            ror_data = response.json()
            if ror_data['items']:
                funder_id = ror_data['items'][0]['id'].split("org/")[1] # ROG id
                unmatched_funders_df.at[index, 'funder_code'] = funder_id
        #use uuid if not found in ROG
        else:
            unmatched_funders_df.at[index, 'funder_code'] = str(uuid.uuid4())


        #create xml for each funder
        sub_root = ET.SubElement(xml_root, "unit")
        element = ET.SubElement(sub_root, "unitData")
        ET.SubElement(element, "organizationCode").text = funder_id
        ET.SubElement(element, "organizationName").text = funder_name
        ET.SubElement(element, "organizationType").text = "Funder"
        data = ET.SubElement(element, "data")
        location = ET.SubElement(data, "addressDataList")
        ET.SubElement(location, "city").text = ror_data['items'][0]['addresses'][0]['geonames_city']['city']

        country_name = ror_data['items'][0]['country']['country_name'].strip().lower()
        alpha3_code = country_name_to_alpha3.get(country_name, "UNK") 
        ET.SubElement(location, "country").text =  alpha3_code

    #append unmatched funders to data/funder_info.csv
    updated_funders_df = pd.concat([existing_funders_df, unmatched_funders_df], ignore_index=True)
    updated_funders_df.to_csv(csv_file_name, index=False)
    print(f"Unmatched funder names have been successfully appended to {csv_file_name}")

    #append unmatched funders to New_Funder.xml
    rough_string = ET.tostring(xml_root, encoding='utf-8')
    pretty_xml = xml.dom.minidom.parseString(rough_string).toprettyxml(indent="  ")

    pretty_xml = remove_extra_blank_lines(pretty_xml)

    with open(xml_file, "w", encoding="utf-8") as f:
        f.write(pretty_xml)
        print(f"XML file 'New_Funder.xml' has been created with unmatched funders.")
else:
    print("No unmatched funder names found to append.")

print("Unmatched funders:")
print(unmatched_funders)
