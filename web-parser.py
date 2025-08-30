import requests
import urllib3
from bs4 import BeautifulSoup
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def clean_json_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
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
    
    print(f"Cleaned JSON file saved to {file_path}")

def parse_passive_value(block):
    """
    Parse a block to extract full text description in order,
    including all <a> and <span> tags, without duplicating content.
    """
    # Use stripped_strings to get all text nodes in order
    return " ".join(s.strip() for s in block.stripped_strings)

def parse_oils_and_values(table_row):
    emotions_list = []
    value_list = []
    passive_name = None

    columns = table_row.find_all("td")
    if len(columns) < 2:
        return None

    # Extract emotions (oils)
    for link in columns[0].find_all("a", class_="item_currency"):
        oil_name = link.get_text(strip=True)
        if oil_name:
            emotions_list.append(oil_name)

    # Extract passive name
    passive_link = columns[1].find("a")
    passive_name = passive_link.get_text(strip=True) if passive_link else None

    # Extract passive values
    for block in columns[1].find_all("div", class_="implicitMod"):
        description = parse_passive_value(block)
        if description:
            value_list.append(description)

    if passive_name:
        return {passive_name: {"value": value_list, "emotions": emotions_list}}
    return None

def add_to_map(map_data, passive_name, value_list, emotions_list):
    emotion_weights = {
        "Diluted Liquid Ire": 1,
        "Diluted Liquid Guilt": 3,
        "Diluted Liquid Greed": 9,
        "Liquid Paranoia": 27,
        "Liquid Envy": 81,
        "Liquid Disgust": 243,
        "Liquid Despair": 729,
        "Concentrated Liquid Fear": 2187,
        "Concentrated Liquid Suffering": 6561,
        "Concentrated Liquid Isolation": 19683
    }

    weight = sum(emotion_weights.get(emotion, 0) for emotion in emotions_list)

    map_data[passive_name] = {
        "value": value_list,
        "emotions": emotions_list,
        "weight": weight
    }

def main():
    url = "https://poe2db.tw/us/Liquid_Emotions#LiquidEmotionsPassives"
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.content, "html.parser")

    table_rows = soup.find_all("tr")
    combined_output = {}

    for row in table_rows:
        parsed_data = parse_oils_and_values(row)
        if parsed_data:
            for passive_name, data in parsed_data.items():
                add_to_map(combined_output, passive_name, data["value"], data["emotions"])

    # Sort by weight
    sorted_output = dict(sorted(combined_output.items(), key=lambda item: item[1]["weight"]))

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(sorted_output, f, indent=4)

    print("Parsing completed. Results saved to data.json")
    
    clean_json_file("data.json")

if __name__ == "__main__":
    main()
