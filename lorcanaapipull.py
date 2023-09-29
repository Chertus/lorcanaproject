import os
import subprocess
import requests
import json
import logging
from bs4 import BeautifulSoup
from difflib import SequenceMatcher

# Constants
BASE_API_URL = "https://api.lorcana-api.com/cards/"
SAVE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_environment():
    if not os.path.isfile("run_lorcana.sh") or not os.access("run_lorcana.sh", os.X_OK):
        subprocess.run(["python3", "-m", "venv", "venv"], check=True)
        with open("run_lorcana.sh", "w") as f:
            f.write("#!/bin/bash\n")
            f.write("source venv/bin/activate\n")
            f.write("python3 lorcanaapipull.py\n")
        os.chmod("run_lorcana.sh", 0o755)
        subprocess.run(["venv/bin/pip", "install", "requests", "beautifulsoup4", "pytesseract", "Pillow"], check=True)

def adaptive_scrape_card_data_from_website(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        potential_card_elements = soup.find_all(size=lambda value: value and int(value) > 3)
        return [{"name": card_element.text.strip()} for card_element in potential_card_elements]
    except requests.RequestException as e:
        logging.error(f"Error scraping {url}: {e}")
        return []

def string_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def fetch_card_data_from_api(card_name):
    endpoint = BASE_API_URL + card_name
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Failed to retrieve data for {card_name}: {e}")
        return None

def ai_cross_examine(api_data, scraped_data):
    for card in api_data:
        similarities = [string_similarity(card['name'].lower(), scraped_card['name'].lower()) for scraped_card in scraped_data]
        if max(similarities) < 0.8:
            logging.warning(f"Potential data discrepancy for card: {card['name']}")

def main():
    setup_environment()

    websites = ["https://lorcania.com/cards", "https://lorcanaplayer.com/cards/"]
    scraped_card_data = [data for website in websites for data in adaptive_scrape_card_data_from_website(website)]

    all_card_data = [data for card in scraped_card_data if (data := fetch_card_data_from_api(card['name']))]

    ai_cross_examine(all_card_data, scraped_card_data)

    with open(os.path.join(SAVE_DIRECTORY, "cleaned_card_data.json"), "w") as file:
        json.dump(all_card_data, file, indent=4)

    with open(os.path.join(SAVE_DIRECTORY, "data_lake.json"), "w") as file:
        json.dump(all_card_data, file, indent=4)

    logging.info("Script completed successfully!")

if __name__ == "__main__":
    main()

