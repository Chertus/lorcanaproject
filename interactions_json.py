import json
import logging

# Constants
DATA_LAKE_PATH = '/home/thomas/Lorcana/data_lake.json'
INTERACTIONS_PATH = '/home/thomas/Lorcana/interactions.json'

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_data_lake():
    try:
        with open(DATA_LAKE_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error reading data lake file: {str(e)}")
        return []

def create_interaction_json(data_lake):
    interactions = []
    
    # Iterate through cards and construct interactions
    for card in data_lake:
        interaction = {
            "card_id": card.get("id"),
            "card_text": card.get("text", ""),
            "analyzed_data": card.get("analyzed_data", {}),
            "extracted_rules": card.get("extracted_rules", {})
        }
        interactions.append(interaction)
    
    try:
        # Save the interaction JSON
        with open(INTERACTIONS_PATH, 'w') as f:
            json.dump(interactions, f, indent=2)
        logging.info(f"Interactions saved to {INTERACTIONS_PATH}")
    except Exception as e:
        logging.error(f"Error writing to interactions file: {str(e)}")

if __name__ == "__main__":
    data_lake = load_data_lake()
    create_interaction_json(data_lake)

