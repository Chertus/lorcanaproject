import os
import subprocess
import requests
import json
import logging
from bs4 import BeautifulSoup

# URLs to scrape
URLS = [
    "https://lorcanaplayer.com/how-to-play-disney-lorcana-rules/",
    "https://www.polygon.com/23832801/disney-lorcana-how-to-play-guide",
    "https://infinite.tcgplayer.com/article/How-to-Play-Disney-Lorcana-Rules-Mechanics-Winning-and-More/fe2cfafc-7d0c-4b73-973c-2d5c7340b0a1/"
]

# Directory to save data
SAVE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_virtual_environment():
    if not os.path.isdir("venv"):
        logging.info("Setting up virtual environment...")
        subprocess.run(["python3", "-m", "venv", "venv"], check=True)
        subprocess.run(["venv/bin/pip", "install", "requests", "beautifulsoup4"], check=True)
    else:
        logging.info("Virtual environment already set up.")

def scrape_website(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup
    except requests.RequestException as e:
        logging.error(f"Error scraping {url}: {e}")
        return None

def extract_data_from_soup(soup):
    # Extract textual content
    paragraphs = [p.text for p in soup.find_all('p')]
    return paragraphs

def clean_and_normalize_data(data):
    cleaned_data = list(set(data))
    cleaned_data = [item for item in cleaned_data if item.strip() != ""]
    return cleaned_data

def main():
    setup_virtual_environment()
    
    all_data = []
    for url in URLS:
        soup = scrape_website(url)
        if soup:
            data = extract_data_from_soup(soup)
            all_data.extend(data)
    
    cleaned_data = clean_and_normalize_data(all_data)
    
    with open(os.path.join(SAVE_DIRECTORY, "LorcanaRules.JSON"), "w") as file:
        json.dump(cleaned_data, file, indent=4)

    logging.info("Script completed successfully!")

if __name__ == "__main__":
    main()

