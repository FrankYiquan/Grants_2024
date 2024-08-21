# Overview
This script processes grant-related data from a JSON input file, extracts relevant information, and generates an XML output file. It matches funder display names in the JSON file with those in an existing CSV file, applying a similarity check to ensure accurate identification. The script also includes functionality for retrieving and formatting additional grant information, such as investigator details and funding amounts.

# Features
Extracts Grant Data: The script reads a JSON file containing grant information and extracts relevant details such as funder name, award ID, and investigator information.
Funder Display Name Matching: Uses a similarity check to match funder display names in the JSON file with those in an existing CSV file.
Retrieves NSF Award Data: Fetches additional award data from the NSF API, including the start date, amount, and grant title.
Generates XML Output: Converts the extracted data into a structured XML format and saves it to an output file.
Requirements
Python 3.x
Required libraries:
json
xml.etree.ElementTree
xml.dom.minidom
csv
requests
datetime
re
pandas
difflib
You can install the necessary libraries using pip:

# Usage
Run the Script
Execute the Script: Run the script using Python. You will be prompted to enter the path to the JSON input file.

Copy code
python3 Grants_info_xml.py


Review the Output
The script will generate an XML file (output.xml) containing the extracted grant information. This file will be saved in the same directory as the script.
Example Input/Output
Input JSON File: Contains data on grants, including funder display names and award IDs.
CSV File: Contains known funder display names and corresponding codes.
Output XML File: Structured XML with grant information, including matched funder codes and investigator details.
Functions
extract_information: Extracts and processes grant data from the JSON input.
get_funder_code: Matches and retrieves the funder code based on a similarity check.
get_nsf_award_data: Fetches additional data from the NSF API.
format_date: Formats dates from MM/DD/YYYY to YYYYMMDD.
load_funder_info: Loads funder display names and codes from a CSV file.
dict_to_xml: Converts the processed data into XML format.
pretty_print_xml: Formats the XML data for easy reading.
Error Handling
The script handles errors related to file reading, JSON parsing, and API requests, providing informative messages in case of issues.
If a funder display name in the JSON file does not match any entry in the CSV file (based on the similarity check), it will not be included in the final XML output.
Customization
Similarity Threshold: You can adjust the similarity_threshold in the get_funder_code function to make the matching process more or less strict.
