import os
import subprocess
import requests
import json
from bs4 import BeautifulSoup
import pytesseract
from PIL import Image
from difflib import SequenceMatcher

# Check for virtual environment setup
if not os.path.isfile("run_lorcana.sh") or not os.access("run_lorcana.sh", os.X_OK):
    # Create a virtual environment
    subprocess.run(["python3", "-m", "venv", "venv"], check=True)
    
    # Create run_lorcana.sh script
    with open("run_lorcana.sh", "w") as f:
        f.write("#!/bin/bash\n")
        f.write("source venv/bin/activate\n")
        f.write("python3 lorcanaapipull.py\n")
    
    # Make the script executable
    os.chmod("run_lorcana.sh", 0o755)
    
    # Install required libraries in the virtual environment
    subprocess.run(["venv/bin/pip", "install", "requests", "beautifulsoup4", "pytesseract", "Pillow"], check=True)

# Check for required Python libraries
def check_and_install_prerequisites():
    required_packages = {
        "requests": "requests",
        "beautifulsoup4": "bs4",
        "pytesseract": "pytesseract",
        "Pillow": "PIL"
    }
    missing_packages = []
    
    for package, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required libraries: {', '.join(missing_packages)}")
        print("Please ensure you've activated the virtual environment and installed the required libraries.")
        exit(1)

check_and_install_prerequisites()

BASE_API_URL = "https://api.lorcana-api.com/cards/"

def adaptive_scrape_card_data_from_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    potential_card_elements = soup.find_all(size=lambda value: value and int(value) > 3)
    
    card_data = []
    for card_element in potential_card_elements:
        card_info = {}
        card_info['name'] = card_element.text.strip()
        card_data.append(card_info)
    return card_data

def string_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def ai_cross_examine(api_data, scraped_data):
    for card in api_data:
        similarities = [string_similarity(card['name'].lower(), scraped_card['name'].lower()) for scraped_card in scraped_data]
        if max(similarities) < 0.8:
            print(f"Potential data discrepancy for card: {card['name']}")

def fetch_card_data_from_api(card_name):
    endpoint = BASE_API_URL + card_name
    response = requests.get(endpoint)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve data for {card_name}. Status code: {response.status_code}")
        return None

def clean_data(cards):
    cleaned_cards = []
    for card in cards:
        cleaned_cards.append(card)
    return cleaned_cards

def main():
    scraped_card_data = []
    websites = ["https://lorcania.com/cards", "https://lorcanaplayer.com/cards/"]
    for website in websites:
        scraped_card_data.extend(adaptive_scrape_card_data_from_website(website))

    all_card_data = []
    for card in scraped_card_data:
        card_data = fetch_card_data_from_api(card['name'])
        if card_data:
            all_card_data.append(card_data)

    ai_cross_examine(all_card_data, scraped_card_data)

    cleaned_card_data = clean_data(all_card_data)

    SAVE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(SAVE_DIRECTORY, "cleaned_card_data.json"), "w") as file:
        json.dump(cleaned_card_data, file)

    with open(os.path.join(SAVE_DIRECTORY, "data_lake.json"), "w") as file:
        json.dump(all_card_data, file)

if __name__ == "__main__":
    main()

