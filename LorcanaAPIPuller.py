import requests
import json
import os

# Define the API base URL
api_base_url = "https://api.lorcana-api.com/strict/"

# Read the list of card names from ListofLorcanaCards.txt
with open("ListofLorcanaCards.txt", "r") as file:
    card_names = file.read().splitlines()

# Create a directory to store card data and images
project_dir = "lorcana_cards"
os.makedirs(project_dir, exist_ok=True)

# Initialize a dictionary to store card data
all_card_data = {}

# Loop through each card name, fetch the data, and store it in the dictionary
for card_name in card_names:
    # Replace spaces with underscores and convert to lowercase
    formatted_card_name = card_name.replace(" ", "_").lower()
    
    # Make the API request
    url = f"{api_base_url}{formatted_card_name}"
    response = requests.get(url)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        card_data = response.json()
        
        # Create a subfolder for each card
        card_dir = os.path.join(project_dir, formatted_card_name)
        os.makedirs(card_dir, exist_ok=True)
        
        # Download the card image and save it in the card's subfolder
        image_url = card_data.get("image-urls", {}).get("large")
        if image_url:
            image_extension = image_url.split(".")[-1]
            image_filename = f"{formatted_card_name}.{image_extension}"
            image_path = os.path.join(card_dir, image_filename)
            with open(image_path, "wb") as image_file:
                image_file.write(requests.get(image_url).content)
            card_data["image_filename"] = image_filename
        
        # Save the card data in a JSON file within the card's subfolder
        card_data_path = os.path.join(card_dir, "card_data.json")
        with open(card_data_path, "w") as json_file:
            json.dump(card_data, json_file, indent=4)
        
        all_card_data[formatted_card_name] = card_data
    else:
        print(f"Failed to fetch data for {card_name}")

# Save a summary of collected card data as a JSON file in the project directory
summary_data_path = os.path.join(project_dir, "summary_card_data.json")
with open(summary_data_path, "w") as json_file:
    json.dump(all_card_data, json_file, indent=4)

print("Card data and images have been fetched and saved with the specified structure.")

