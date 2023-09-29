import cv2
import pytesseract
import json
from collections.abc import MutableMapping

def extract_text_from_image(image_path):
    # Load the image using OpenCV
    image = cv2.imread(image_path)

    # Use pytesseract to extract text from the image
    text = pytesseract.image_to_string(image)

    return text

def associate_images_with_text(data_lake_path, cleaned_card_data_path):
    # Helper function to recursively convert list of dictionaries to dictionary
    def merge_dict(dct, merge_dct):
        for k, v in merge_dct.items():
            if (k in dct and isinstance(dct[k], MutableMapping) and
                    isinstance(merge_dct[k], MutableMapping)):
                merge_dict(dct[k], merge_dct[k])
            else:
                dct[k] = merge_dct[k]
        return dct

    with open(data_lake_path, 'r') as data_lake_file:
        data_lake = json.load(data_lake_file)

    if not isinstance(data_lake, dict):
        # If data_lake is not a dictionary, convert it to an empty dictionary
        data_lake = {}

    with open(cleaned_card_data_path, 'r') as cleaned_card_data_file:
        cleaned_card_data = json.load(cleaned_card_data_file)

    updated_data_lake = {}

    for card_id, card_info in data_lake.items():  # Iterate through dictionary items
        # Assuming each card has an associated image file with a name like 'card_1.jpg'
        image_path = f'/path/to/card_images/{card_id}.jpg'

        # Extract text from the image
        extracted_text = extract_text_from_image(image_path)

        # Match the extracted text with cleaned_card_data
        matched_card = cleaned_card_data.get(extracted_text)

        if matched_card:
            # If a match is found, update the data lake with the card information
            updated_data_lake[card_id] = {
                "image_path": image_path,
                "card_info": matched_card
            }
        else:
            # Handle cases where no match is found
            print(f"No match found for card ID {card_id}")

    # Merge updated_data_lake with the existing data_lake to keep both images and previous data
    merged_data_lake = merge_dict(data_lake, updated_data_lake)

    # Save the updated data lake
    with open(data_lake_path, 'w') as updated_data_lake_file:
        json.dump(merged_data_lake, updated_data_lake_file, indent=4)

if __name__ == "__main__":
    data_lake_path = '/home/thomas/Lorcana/data_lake.json'
    cleaned_card_data_path = '/home/thomas/Lorcana/cleaned_card_data.json'

    associate_images_with_text(data_lake_path, cleaned_card_data_path)

