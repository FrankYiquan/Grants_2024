import requests
import json

def fetch_openalex_work(work_id: str):
    url = f"https://api.openalex.org/works/{work_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# Reconstruct the abstract
def reconstruct_abstract(index):
    word_count = max(i for positions in index.values() for i in positions) + 1
    words = [None] * word_count
    for word, positions in index.items():
        for pos in positions:
            words[pos] = word
    return " ".join(words)


if __name__ == "__main__":
    # work_id = "W4405963434"
    # data = fetch_openalex_work(work_id)

    # # Export data to a JSON file
    # output_file = "openalex_work_data.json"
    # with open(output_file, "w") as f:
    #     json.dump(data, f, indent=2)

    # print(f"Data saved to {output_file}")

    # work_id = "W4405963434"
    # url = f"https://api.openalex.org/works/{work_id}"

    # response = requests.get(url)
    # data = response.json()

    # # Access the abstract_inverted_index if it exists
    # abstract_index = data.get("abstract_inverted_index")

    # abstract_text = reconstruct_abstract(abstract_index)
    # print(abstract_text)

    with open("data/reseracherIDs (1).csv", "r") as f:
        faculties = f.readlines()

    for faculty in faculties:
        orcid = faculty.strip()
