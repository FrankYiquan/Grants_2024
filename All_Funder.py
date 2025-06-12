from collections import Counter
import json
from get_data import get_data_openAlex


def get_all_funder(start_year:int, end_year:int):
    funder_counts = Counter()
    funder_set = set()

    for year in range(start_year, end_year + 1):
        input_file_name = 'brandeis_2024.json' #this can use to store any year (other than 2024), 2024 is just kepet for previous code.
        base_url = f'https://api.openalex.org/works?filter=institutions.id:https://openalex.org/I6902469,publication_year:{year}&sort=publication_date:desc'
        # get article from OpenAlex API
        get_data_openAlex(base_url, input_file_name).get_data_openAlex()

        # Load JSON data
        with open(input_file_name, 'r') as json_file:
            data = json.load(json_file)

        # Extract funder names from brandeis_2024.json
        for item in data:
            for grant in item.get('grants', []):
                funder_name = grant.get('funder_display_name', '')
                award_id = grant.get('award_id', '')
                # new funder only added if funder_name and awawrd_id not empty and funder_name is not "CERN"
                if funder_name and funder_name != "CERN" and award_id:
                    funder_set.add(funder_name)
                    funder_counts[funder_name] += 1
        print(f"Processed year {year}: found {len(funder_set)} unique funders so far.")
        
    # Save unique funder names
    with open("unique_funders.json", "w") as f:
        json.dump(sorted(list(funder_set)), f, indent=2)

    
    # Save funder counts
    sorted_counts = dict(funder_counts.most_common())

    with open("funder_counts.json", "w") as f:
        json.dump(sorted_counts, f, indent=2)

    print("Saved unique_funders.json and funder_counts.json.")




