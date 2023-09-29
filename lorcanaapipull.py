import requests
import json
import os

# Define the API base URL
api_base_url = "https://api.lorcana-api.com/strict/"

# Read the list of card names from ListofLorcanaCards.txt
with open("ListofLorcanaCards.txt", "r") as file:
    card_names = file.read().splitlines()

# Initialize a dictionary to store card data
all_card_data = {}

# Create a directory to store card images
image_dir = "card_images"
os.makedirs(image_dir, exist_ok=True)

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
        
        # Verify that both card text and images are present before saving
        if "body-text" in card_data and "image-urls" in card_data:
            # Create a subfolder for each card
            card_dir = os.path.join(image_dir, formatted_card_name)
            os.makedirs(card_dir, exist_ok=True)
            
            # Download the card image and save it in the card's subfolder
            image_url = card_data.get("image-urls", {}).get("large")
            if image_url:
                image_extension = image_url.split(".")[-1]
                image_filename = f"{formatted_card_name}.{image_extension}"
                image_path = os.path.join(card_dir, image_filename)
                with open(image_path, "wb") as image_file:
                    image_file.write(requests.get(image_url).content)
                card_data["image_filename"] = image_path
            
            # Save the card data in a JSON file within the card's subfolder
            card_data_path = os.path.join(card_dir, "card_data.json")
            with open(card_data_path, "w") as json_file:
                json.dump(card_data, json_file, indent=4)
            
            all_card_data[formatted_card_name] = card_data
        else:
            print(f"Card data for {card_name} is incomplete and will not be saved.")
    else:
        print(f"Failed to fetch data for {card_name}")

# Save the collected card data as a JSON file
with open("lorcana_card_data.json", "w") as json_file:
    json.dump(all_card_data, json_file, indent=4)

print("Card data and images have been fetched and saved with verification.")

