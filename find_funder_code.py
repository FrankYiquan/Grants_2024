from fuzzywuzzy import process, fuzz
import pandas as pd
import json

def get_funder_codes(df_funders, funder_display_name, df_secondary):
    filtered_funders = df_funders[df_funders['Name'].str.contains('United States', case=False, na=False)]
    if filtered_funders.empty:
        filtered_funders = df_funders[df_funders['Name'].str.contains('Canada', case=False, na=False)]

    matches = process.extract(funder_display_name, filtered_funders['Name'], scorer=fuzz.partial_ratio, limit=None)

    enhanced_matches = []
    for match, score, idx in matches:
        if score >= 70:
            if funder_display_name in match:
                exact_match_score = fuzz.ratio(funder_display_name, match)
                combined_score = (score + exact_match_score) / 2 
                enhanced_matches.append((match, combined_score, idx))
            else:
                enhanced_matches.append((match, score * 0.8, idx))

    if enhanced_matches:
        best_match = max(enhanced_matches, key=lambda x: x[1])
        best_match_name = best_match[0]
        best_match_code = df_funders.loc[df_funders['Name'] == best_match_name, 'Code'].values[0]
        print(f"Best match name: {best_match_name}")
        print(f"Best match funder code: {best_match_code}")
    else:
        best_match_code = None
    
    if best_match_code is None:
        secondary_matches = process.extract(funder_display_name, df_secondary['Name'], scorer=fuzz.partial_ratio, limit=None)
        secondary_matches = [(match, score) for match, score, _ in secondary_matches if score >= 70 and funder_display_name in match]
        if secondary_matches:
            best_secondary_match = max(secondary_matches, key=lambda x: x[1])
            best_secondary_name = best_secondary_match[0]
            best_match_code = df_secondary.loc[df_secondary['Name'] == best_secondary_name, 'Code'].values[0]
            print(f"Secondary best match name: {best_secondary_name}")
            print(f"Secondary best match funder code: {best_match_code}")
        else: 
            best_match_code = None
            print("No matches found with a score of 70 or higher.")
    return best_match_code

def extract_from_json(data, df_funders, df_secondary):
    extracted_data = []
    df_funders['Name'] = df_funders['Name'].astype(str)
    for result in data.get('results', []):
        for grant in result.get('grants', []):
            funder_display_name = grant.get('funder_display_name', '')
            funder_code = get_funder_codes(df_funders, funder_display_name,df_secondary)
            grant_info = {
                'funder_display_name': funder_display_name,
                'funder_code': funder_code
            }
            extracted_data.append(grant_info)
    
    return extracted_data

file_path1 = 'data/centralExternalOrganizationList.xlsx'
file_path2 = 'data/localExternalOrganizationList.xlsx'

try:
    df_funders = pd.read_excel(file_path1, engine='openpyxl')
    df_secondary = pd.read_excel(file_path2,engine='openpyxl' )
    print(f"Column names: {df_funders.columns.tolist()}")  
    print(f"Column names: {df_funders.columns.tolist()}")
except FileNotFoundError:
    print(f"Excel file {file_path1} not found.")
    exit()
except UnicodeDecodeError:
    print(f"Error decoding Excel file {file_path1}.")
    exit()

json_file_path = 'data/2024_data.json'
with open(json_file_path, 'r') as json_file:
    data = json.load(json_file)

extracted_data = extract_from_json(data, df_funders, df_secondary)
df_code = pd.DataFrame(extracted_data)

df_code = df_code.drop_duplicates(subset=['funder_display_name'])

df_code.to_csv('file1.csv', index=False)
