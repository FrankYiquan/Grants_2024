#this script is to get data from OpenAlex API for Brandeis University grants

import requests
import json

class get_data_openAlex:
#Brandeis institution id: i6902469

#this url is for Brandeis 2024
#api for get only 2024 grants: https://api.openalex.org/works?filter=institutions.id:https://openalex.org/I6902469,publication_year:2024&sort=publication_date:desc

    def __init__(self, base_url, file_name):
        self.base_url = base_url
        self.file_name = file_name


#base_url = 'https://api.openalex.org/works?filter=institutions.id:https://openalex.org/I6902469,publication_year:2023&sort=publication_date:desc'
    def get_data_openAlex(self):
        all_results = []
        api_url = self.base_url
        response = requests.get(api_url)
    
        if response.status_code == 200:
            data = response.json()
            all_results.extend(data.get('results', []))
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")

        with open(self.file_name, 'w') as json_file:
            json.dump(all_results, json_file, indent=4)

# if __name__ == "__main__":
#     base_url = 'https://api.openalex.org/works?filter=institutions.id:https://openalex.org/I6902469,publication_year:2024&sort=publication_date:desc'
#     file_name = 'brandeis_2024.json'

#     fetcher = get_data_openAlex(base_url, file_name)
#     fetcher.get_data_openAlex()

