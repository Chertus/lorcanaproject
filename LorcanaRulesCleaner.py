import json
import re
import requests
import spacy
from textblob import TextBlob
from bs4 import BeautifulSoup

# Check and install missing prerequisites
def check_and_install_prerequisites():
    import importlib
    missing_packages = []

    # List of required packages
    required_packages = ["spacy", "textblob", "beautifulsoup4"]

    for package in required_packages:
        try:
            importlib.import_module(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("Installing missing packages...")
        import subprocess
        subprocess.run(["pip", "install"] + missing_packages, check=True)
        print("Prerequisites installed.")

# Load JSON data from LorcanaRules.JSON
def load_json_data(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
    return data

# Clean and normalize text
def clean_and_normalize_text(text):
    # Remove special characters, extra spaces, and lowercase the text
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip().lower()
    return cleaned_text

# Analyze URLs and extract relevant information
def analyze_urls(urls):
    analyzed_data = []

    for url in urls:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract relevant data from HTML
                extracted_data = {
                    "title": soup.title.string,
                    "paragraphs": [p.text for p in soup.find_all('p')],
                }
                analyzed_data.append(extracted_data)
        except Exception as e:
            print(f"Error analyzing URL: {url}")
            continue

    return analyzed_data

# Perform sentiment analysis using TextBlob
def perform_sentiment_analysis(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    return sentiment

# Keyword-based AI method
def keyword_based_analysis(text):
    # Define a list of keywords related to card games
    keywords = ["card", "deck", "rules", "player", "strategy", "turn"]

    # Check if any keywords are present in the text
    for keyword in keywords:
        if keyword in text:
            return True
    return False

# Main script
def main():
    # Check and install missing prerequisites
    check_and_install_prerequisites()

    # Load JSON data from LorcanaRules.JSON
    data = load_json_data("LorcanaRules.JSON")
    
    # Initialize spaCy model
    nlp = spacy.load("en_core_web_sm")

    # Process each rule
    for rule in data:
        # Clean and normalize text
        text = rule.get("text", "")
        cleaned_text = clean_and_normalize_text(text)

        # Analyze and store cleaned text
        rule["cleaned_text"] = cleaned_text

        # Analyze URLs and store results
        urls = rule.get("urls", [])
        url_data = analyze_urls(urls)
        rule["url_data"] = url_data

        # Perform sentiment analysis and store sentiment score
        sentiment = perform_sentiment_analysis(cleaned_text)
        rule["sentiment"] = sentiment

        # Apply keyword-based analysis
        keyword_based_result = keyword_based_analysis(cleaned_text)
        rule["keyword_based"] = keyword_based_result

    # Save the processed data back to CleanLorcanaRules.JSON
    with open("CleanLorcanaRules.JSON", 'w') as file:
        json.dump(data, file, indent=4)

if __name__ == "__main__":
    main()

