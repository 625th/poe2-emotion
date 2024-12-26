import requests
import urllib3
from bs4 import BeautifulSoup
import json

# Disable SSL warnings to prevent cluttering output
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
def clean_json_file(file_path):

    with open(file_path, "r", encoding="utf-8") as f:

        data = json.load(f)

    

    # Recursive function to traverse and clean the data

    def clean_spaces(obj):

        if isinstance(obj, dict):

            return {k: clean_spaces(v) for k, v in obj.items()}

        elif isinstance(obj, list):

            return [clean_spaces(item) for item in obj]

        elif isinstance(obj, str):

            return obj.replace(" %", "%")  # Remove space before '%'

        return obj



    cleaned_data = clean_spaces(data)



    with open(file_path, "w", encoding="utf-8") as f:

        json.dump(cleaned_data, f, indent=4)

    

    print(f"Cleaned JSON file saved to {{file_path}}")

# Function to parse passive mods
def parse_passive_value(block):
    """
    Parse a block to extract full text description, including KeywordPopups.
    """
    description_parts = []
    for child in block.children:
        if child.name == "span" and "mod-value" in child.get("class", []):
            description_parts.append(child.get_text(strip=True))
        elif child.name == "span" and "KeywordPopups" in child.get("class", []):
            description_parts.append(child.get_text(strip=True))
        elif isinstance(child, str):
            description_parts.append(child.strip())
    return " ".join(filter(None, description_parts)) or None

# Function to parse oils (emotions) and passive names along with their values
def parse_oils_and_values(table_row):
    """
    Parses oils (emotions) from the first column and passive skill name with values from the second column.
    """
    emotions_list = []  # List for oils (now called "emotions")
    value_list = []  # List for passive values
    passive_name = None

    # Split columns
    columns = table_row.find_all("td")
    if len(columns) < 2:
        return None  # Skip invalid rows

    # Extract oils (emotions) from the first column
    for link in columns[0].find_all("a", class_="item_currency"):
        oil_name = link.get_text(strip=True)
        if oil_name:
            emotions_list.append(oil_name)

    # Extract passive name and values from the second column
    passive_link = columns[1].find("a")
    passive_name = passive_link.get_text(strip=True) if passive_link else None

    # Parse passive descriptions
    for block in columns[1].find_all("div", class_="implicitMod"):
        description = parse_passive_value(block)
        if description:
            value_list.append(description)

    # Return structured data only if a passive name exists
    if passive_name:
        return {passive_name: {"value": value_list, "emotions": emotions_list}}
    return None

# Main script execution
def main():
    url = "https://poe2db.tw/us/Distilled_Emotions#DistilledEmotionsPassives"  # Replace with the actual URL
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all rows in the table
    table_rows = soup.find_all("tr")

    # Initialize the final dictionary for combined data
    combined_output = {}

    # Process each row
    for row in table_rows:
        parsed_data = parse_oils_and_values(row)
        if parsed_data:
            combined_output.update(parsed_data)

    # Save the combined output dictionary to a single JSON file
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(combined_output, f, indent=4)

    print("Parsing completed. Results saved to data.json")
    
    clean_json_file("data.json")

# Run the main function
if __name__ == "__main__":
    main()
