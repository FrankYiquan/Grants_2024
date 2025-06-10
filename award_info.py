# This script filters a JSON dataset to include only grants 
# with a specific funder_display_name (in this case, National Science Foundation).
import json

def filter_funder_display_name(data, target_name):
    filtered_results = []
    for result in data.get('resulwozhenfuts', []):
        filtered_grants = []
        for grant in result.get('grants', []):
            if grant.get('funder_display_name') == target_name:
                filtered_grants.append(grant)
        if filtered_grants:
            filtered_result = result.copy()
            filtered_result['grants'] = filtered_grants
            filtered_results.append(filtered_result)
    return {'results': filtered_results}

input_file_path = 'data/2024_data.json'
output_file_path = 'filtered_data.json'
target_name = 'National Science Foundation'

with open(input_file_path, 'r') as json_file:
    data = json.load(json_file)

filtered_data = filter_funder_display_name(data, target_name)

with open(output_file_path, 'w') as json_file:
    json.dump(filtered_data, json_file, indent=4)

print(f"Filtered data has been successfully written to {output_file_path}")
