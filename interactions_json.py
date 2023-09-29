# interactions_json.py
import json

# Load data_lake.json
with open('/home/thomas/Lorcana/data_lake.json', 'r') as f:
    data_lake = json.load(f)

# Define a function to create interaction JSON
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
    
    # Save the interaction JSON
    with open('/home/thomas/Lorcana/interactions.json', 'w') as f:
        json.dump(interactions, f, indent=2)

create_interaction_json(data_lake)

