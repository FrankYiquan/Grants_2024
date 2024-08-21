import json
import pandas as pd

try:
    input_file_name = input("Please enter the input JSON file name (with .json extension and relative path): ")

    with open(input_file_name, 'r') as json_file:
        data = json.load(json_file)

    # Check if the data list is empty
    if not data:
        raise ValueError("The JSON data is empty. Please check the input file.")

    funder_data = []

    for item in data.get('results', []):
        # Check if item is a dictionary
        if isinstance(item, dict):
            for grant in item.get('grants', []):
                funder_info = {
                    'funder_display_name': grant.get('funder_display_name', '')
                }
                funder_data.append(funder_info)
        else:
            print(f"Skipping item, not a dictionary: {item}")

    if funder_data:  # Check if funder_data is not empty
        df = pd.DataFrame(funder_data)
        print("Shape of DataFrame:", df.shape)

        column_name = 'funder_display_name'
        frequency_count = df[column_name].value_counts().reset_index()
        frequency_count.columns = ['Funder_display_name', 'Frequency']

        output_file_name = 'funder_info.csv'
        frequency_count.to_csv(output_file_name, index=False)
        print(f"Funder information has been successfully written to {output_file_name}")

        print("\nTop 10 most frequent funders:")
        print(frequency_count.head(10))
    else:
        print("No valid 'funder_display_name' entries found.")

except FileNotFoundError:
    print(f"Error: The file '{input_file_name}' was not found.")
except json.JSONDecodeError:
    print(f"Error: Failed to parse JSON from '{input_file_name}'. Please check if the file contains valid JSON.")
except ValueError as ve:
    print(f"Error: {ve}")
except IndexError:
    print("Error: The JSON data is empty or improperly formatted.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
