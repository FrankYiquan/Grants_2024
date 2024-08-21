import json
import pandas as pd
from difflib import SequenceMatcher
from get_data import get_data_openAlex

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Input file names
input_file_name = input("Please enter the input JSON file name (with .json extension and relative path): ")
base_url = input("Please enter the base URL: ")

get_data_openAlex(base_url, input_file_name).get_data_openAlex()

csv_file_name = 'data/funder-info.csv'
# Load JSON data
with open(input_file_name, 'r') as json_file:
    data = json.load(json_file)

# Load CSV file
existing_funders_df = pd.read_csv(csv_file_name)
existing_funders = existing_funders_df['Funder_display_name'].tolist()

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

unmatched_funders_df = pd.DataFrame(unmatched_funders, columns=['Funder_display_name'])

if not unmatched_funders_df.empty:
    updated_funders_df = pd.concat([existing_funders_df, unmatched_funders_df], ignore_index=True)
    updated_funders_df.to_csv(csv_file_name, index=False)
    print(f"Unmatched funder names have been successfully appended to {csv_file_name}")
else:
    print("No unmatched funder names found to append.")

print("Unmatched funders:")
print(unmatched_funders)
