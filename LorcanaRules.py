import os
import subprocess
import requests
import json
import logging
import re
from bs4 import BeautifulSoup
from textblob import TextBlob

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
    paragraphs = [p.text for p in soup.find_all('p')]
    return paragraphs

def clean_and_normalize_data(data):
    cleaned_data = list(set(data))
    cleaned_data = [item for item in cleaned_data if item.strip() != ""]
    return cleaned_data

def clean_and_normalize_text(text):
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip().lower()
    return cleaned_text

def perform_sentiment_analysis(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    return sentiment

def keyword_based_analysis(text):
    keywords = ["card", "deck", "rules", "player", "strategy", "turn"]
    for keyword in keywords:
        if keyword in text:
            return True
    return False

def main():
    all_data = []
    for url in URLS:
        soup = scrape_website(url)
        if soup:
            data = extract_data_from_soup(soup)
            all_data.extend(data)
    
    cleaned_data = clean_and_normalize_data(all_data)
    
    for rule in cleaned_data:
        cleaned_text = clean_and_normalize_text(rule)
        sentiment = perform_sentiment_analysis(cleaned_text)
        keyword_based_result = keyword_based_analysis(cleaned_text)
        rule["cleaned_text"] = cleaned_text
        rule["sentiment"] = sentiment
        rule["keyword_based"] = keyword_based_result

    with open(os.path.join(SAVE_DIRECTORY, "CleanLorcanaRules.JSON"), "w") as file:
        json.dump(cleaned_data, file, indent=4)

    logging.info("Script completed successfully!")

if __name__ == "__main__":
    main()

