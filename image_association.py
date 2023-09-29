import cv2
import pytesseract
import json
import logging
from collections.abc import MutableMapping

# Constants
DATA_LAKE_PATH = '/home/thomas/Lorcana/data_lake.json'
CLEANED_CARD_DATA_PATH = '/home/thomas/Lorcana/cleaned_card_data.json'
IMAGE_DIRECTORY = '/path/to/card_images/'

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_text_from_image(image_path):
    try:
        # Load the image using OpenCV
        image = cv2.imread(image_path)
        if image is None:
            logging.error(f"Failed to read image at {image_path}")
            return ""

        # Use pytesseract to extract text from the image
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        logging.error(f"Error extracting text from {image_path}: {str(e)}")
        return ""

def associate_images_with_text(data_lake_path, cleaned_card_data_path):
    try:
        with open(data_lake_path, 'r') as data_lake_file:
            data_lake = json.load(data_lake_file)
    except Exception as e:
        logging.error(f"Error reading data lake file: {str(e)}")
        data_lake = {}

    try:
        with open(cleaned_card_data_path, 'r') as cleaned_card_data_file:
            cleaned_card_data = json.load(cleaned_card_data_file)
    except Exception as e:
        logging.error(f"Error reading cleaned card data file: {str(e)}")
        cleaned_card_data = {}

    updated_data_lake = {}

    for card_id, card_info in data_lake.items():
        image_path = f'{IMAGE_DIRECTORY}{card_id}.jpg'
        extracted_text = extract_text_from_image(image_path)

        matched_card = cleaned_card_data.get(extracted_text)
        if matched_card:
            updated_data_lake[card_id] = {
                "image_path": image_path,
                "card_info": matched_card
            }
        else:
            logging.warning(f"No match found for card ID {card_id}")

    # Merge updated_data_lake with the existing data_lake
    data_lake.update(updated_data_lake)

    try:
        with open(data_lake_path, 'w') as updated_data_lake_file:
            json.dump(data_lake, updated_data_lake_file, indent=4)
    except Exception as e:
        logging.error(f"Error writing to data lake file: {str(e)}")

if __name__ == "__main__":
    associate_images_with_text(DATA_LAKE_PATH, CLEANED_CARD_DATA_PATH)

