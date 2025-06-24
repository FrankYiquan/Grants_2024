import pandas as pd
import json

def funder_with_401code(unique_funder_path, funder_401_path, output_path="funder_with_401code.csv"):
    # Load funder names from JSON list
    with open(unique_funder_path, 'r', encoding='utf-8') as f:
        unique_funders = json.load(f)

    funder_401 = pd.read_csv(funder_401_path)

    results = []
    not_found_count = 0
    total_funders = len(unique_funders)

    for name in unique_funders:
        # Match using exact string (case sensitive)
        matched = funder_401[funder_401["Name"].str.contains(name, na=False, case=False)]

        if not matched.empty:
            # Take the first matching row
            first_match = matched.iloc[0]
            results.append({
                "Name": name,
                "Code": first_match["Code"]
            })
        else:
            # If no match, return "not_found"
            not_found_count += 1
            results.append({
                "Name": name,
                "Code": "not_found"
            })

    # Convert to DataFrame and save
    pd.DataFrame(results).to_csv(output_path, index=False)
    print(f"Processed {total_funders} funders. Not found: {not_found_count}. Results saved to {output_path}.")


unique_funder_path = "unique_funders.json"
funder_401_path = "funder_401.csv"
funder_with_401code(unique_funder_path, funder_401_path)