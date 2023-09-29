import requests
import json
import os

# Define the API base URL
api_base_url = "https://api.lorcana-api.com/strict/"

# Read the list of card names from ListofLorcanaCards.txt
with open("ListofLorcanaCards.txt", "r") as file:
    card_names = file.read().splitlines()

# Initialize the new JSON structure
data_lake = {
    "cards": [],
    "rules": {
        "turnOrder": "",
        "winConditions": "",
        "specialRules": []
    },
    "interactions": [],
    "chatbotQA": []
}

# Create a directory to store card images
image_dir = "card_images"
os.makedirs(image_dir, exist_ok=True)

def validate_data(data):
    required_fields = ["type", "body-text", "image-urls"]
    for field in required_fields:
        if field not in data:
            return False
    return True

def normalize_data(data):
    # Convert all string data to lowercase for consistency
    for key in data:
        if isinstance(data[key], str):
            data[key] = data[key].lower()
    return data

def transform_data(data, card_name):
    # Transform data into the desired structured format for the AI model
    card_data = {
        "id": card_name.replace(" ", "_").lower(),
        "name": card_name,
        "type": data.get("type", ""),
        "description": data.get("body-text", ""),
        "abilities": [],  # Placeholder, modify as needed
        "image": data.get("image-urls", {}).get("large", ""),
        "stats": {}  # Placeholder, modify as needed
    }
    return card_data

# Loop through each card name and fetch the data
for card_name in card_names:
    formatted_card_name = card_name.replace(" ", "_").lower()
    url = f"{api_base_url}{formatted_card_name}"
    response = requests.get(url)

    if response.status_code == 200:
        card_data_api = response.json()

        # Validate, normalize, and transform data
        if validate_data(card_data_api):
            normalized_data = normalize_data(card_data_api)
            transformed_data = transform_data(normalized_data, card_name)
            data_lake["cards"].append(transformed_data)

# TODO: Add the extracted rules from the graphics and other resources to the rules section

# Save the cleaned and organized data to data_lake.json
with open("data_lake.json", "w") as json_file:
    json.dump(data_lake, json_file, indent=4)

print("Card data has been fetched, cleaned, and saved.")

