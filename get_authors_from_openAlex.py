import requests
import json
import pandas as pd

def get_authors_from_openAlex():
    base_url = "https://api.openalex.org/authors"
    params = {
        "filter": "last_known_institutions.id:I6902469",
        "per-page": 50,
        "sort": "works_count:desc"
    }
    authors = []
    cursor = "*"  # cursor '*' means start from the first page

    while True:
        params["cursor"] = cursor
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        authors.extend(data.get("results", []))

        meta = data.get("meta", {})
        next_cursor = meta.get("next_cursor")

        if not next_cursor:
            break  # no more pages
        cursor = next_cursor

    # Save to file
    with open("authors.json", "w", encoding="utf-8") as f:
        json.dump(authors, f, indent=2, ensure_ascii=False)

    print(f"Fetched {len(authors)} authors and saved to authors.json")

# # Run the function
# get_authors_from_openAlex()


def extract_faculty_table(input_file="authors.json", output_file="faculty_table.csv"):
    with open(input_file, "r", encoding="utf-8") as f:
        authors = json.load(f)

    data = []
    for author in authors:
        data.append({
            "id": author.get("id", "").split("/")[-1],
            "display_name": author.get("display_name", ""),
            "display_name_alternatives": "; ".join(author.get("display_name_alternatives", [])),
            "orcid": author.get("orcid", "")
        })

    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)
    print(f"Saved table to {output_file}")

# Run it
extract_faculty_table()