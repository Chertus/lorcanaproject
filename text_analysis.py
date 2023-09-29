import spacy
import json
from collections.abc import MutableMapping

def analyze_text(text):
    # Load the English NLP model
    nlp = spacy.load("en_core_web_sm")

    # Process the text using spaCy
    doc = nlp(text)

    # Analyze the text here (e.g., extract entities, relationships, etc.)
    # You can add your custom logic for text analysis

    return doc.to_json()

def update_data_lake_with_text_analysis(data_lake_path):
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

    updated_data_lake = {}

    for card_id, card_info in data_lake.items():  # Iterate through dictionary items
        # Assuming you want to analyze the text associated with each card
        text_to_analyze = card_info.get("card_info", {}).get("text", "")

        if text_to_analyze:
            # Perform text analysis
            analysis_result = analyze_text(text_to_analyze)

            # Update the card_info with the analysis result
            card_info["text_analysis"] = analysis_result

        updated_data_lake[card_id] = card_info

    # Merge updated_data_lake with the existing data_lake to keep both images and previous data
    merged_data_lake = merge_dict(data_lake, updated_data_lake)

    # Save the updated data lake
    with open(data_lake_path, 'w') as updated_data_lake_file:
        json.dump(merged_data_lake, updated_data_lake_file, indent=4)

if __name__ == "__main__":
    data_lake_path = '/home/thomas/Lorcana/data_lake.json'
    update_data_lake_with_text_analysis(data_lake_path)

