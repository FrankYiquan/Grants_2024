#this script is used to get information about National Sceience Fundation awards
import re
import requests


def clean_award_id(award_id):
    award_id = str(award_id).strip()
    match = re.search(r'\d+', award_id)
    return match.group() if match else None

def get_award_info(award_id):


    #normalize the award_id to ensure it is a string
    normalized_award_id = clean_award_id(award_id)
    if not normalized_award_id:
        print("Invalid award ID format.")
        return None
    url = f"http://api.nsf.gov/services/v1/awards/{normalized_award_id}.json"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Access the first award in the list
        award = data["response"]["award"][0]

        return {
            "startDate": award["startDate"],
            "amount": award["fundsObligatedAmt"]
        }

    except Exception as e:
        print(f"Error: {e}")
        return None

# # Example usage
# info = get_award_info("")
# print(info)
