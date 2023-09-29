import spacy
import json
import logging
from collections.abc import MutableMapping

# Constants
DATA_LAKE_PATH = '/home/thomas/Lorcana/data_lake.json'

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def analyze_text(text):
    """Analyze the given text using spaCy and return the analysis result."""
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    return doc.to_json()

def merge_dict(dct, merge_dct):
    """Recursively merge two dictionaries."""
    for k, v in merge_dct.items():
        if (k in dct and isinstance(dct[k], MutableMapping) and
                isinstance(merge_dct[k], MutableMapping)):
            merge_dict(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]
    return dct

def update_data_lake_with_text_analysis(data_lake_path):
    """Update the data lake with text analysis results."""
    try:
        with open(data_lake_path, 'r') as data_lake_file:
            data_lake = json.load(data_lake_file)

        if not isinstance(data_lake, dict):
            logging.error("Data lake is not a dictionary. Initialization required.")
            return

        updated_data_lake = {}

        for card_id, card_info in data_lake.items():
            text_to_analyze = card_info.get("card_info", {}).get("text", "")
            if text_to_analyze:
                analysis_result = analyze_text(text_to_analyze)
                card_info["text_analysis"] = analysis_result
            updated_data_lake[card_id] = card_info

        merged_data_lake = merge_dict(data_lake, updated_data_lake)

        with open(data_lake_path, 'w') as updated_data_lake_file:
            json.dump(merged_data_lake, updated_data_lake_file, indent=4)

        logging.info("Data lake updated with text analysis results.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    update_data_lake_with_text_analysis(DATA_LAKE_PATH)

