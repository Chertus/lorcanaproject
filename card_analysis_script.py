#!/usr/bin/env python

import os
import json
import cv2
import subprocess
import importlib
import multiprocessing
import shutil
import spacy
from PIL import Image
import pytesseract
import tensorflow as tf

# Constants
REQUIRED_PACKAGES_FILE = "requirements.txt"
DATA_DIRECTORY = "data"
OUTPUT_DIRECTORY = "output"
CLEANED_CARD_DATA_FILE = "cleaned_card_data.json"
DATA_LAKE_FILE = "data_lake.json"
SPACY_MODEL_DIR = "spacy_models"
OBJECT_DETECTION_MODEL_PATH = "fine_tuned_object_detection_model"
NLP_MODEL_NAME = "en_core_web_sm"
CONFIDENCE_THRESHOLD_OBJECT_DETECTION = 0.9
CONFIDENCE_THRESHOLD_NLP = 0.9

def check_and_install_prerequisites():
    try:
        with open(REQUIRED_PACKAGES_FILE, "r") as req_file:
            required_packages = req_file.readlines()
            for package in required_packages:
                subprocess.run(["pip", "install", package.strip()])
    except FileNotFoundError:
        print(f"Error: {REQUIRED_PACKAGES_FILE} not found. Create a requirements.txt file with required packages.")
        exit(1)

    # Check if spaCy is installed, and if not, install it
    try:
        importlib.import_module("spacy")
    except ImportError:
        print("spaCy is not installed. Installing spaCy...")
        subprocess.run(["pip", "install", "spacy"])

def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, config="--psm 6")
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from {image_path}: {str(e)}")
        return ""

def process_card_image(args):
    card_filename, object_detection_model, nlp = args
    card_name = os.path.splitext(card_filename)[0]
    card_path = os.path.join(DATA_DIRECTORY, card_filename)
    card_image = cv2.imread(card_path)
    
    # Use object detection to identify ROIs for different parts of the card
    detected_regions = object_detection_model(card_image)
    
    # Extract text from card image ROIs
    extracted_text = {}
    for label, coordinates in detected_regions.items():
        if label == "name" and coordinates[0] >= CONFIDENCE_THRESHOLD_OBJECT_DETECTION:
            x1, y1, x2, y2 = coordinates[1]
            roi = card_image[y1:y2, x1:x2]
            # Extract text from the ROI using Tesseract OCR
            text = extract_text_from_image(roi)
            extracted_text[label] = text

    # Analyze text data using NLP
    doc = nlp(extracted_text.get("name", ""))

    # Extract meaningful information from NLP analysis (e.g., card type, abilities)
    card_type = ""
    abilities = []
    keywords = ["card", "deck", "rules", "player", "strategy", "turn"]
    for token in doc:
        for keyword in keywords:
            if token.similarity(nlp(keyword)) >= CONFIDENCE_THRESHOLD_NLP:
                if token.pos_ == "NOUN":
                    card_type = token.text
                elif token.pos_ == "VERB":
                    abilities.append(token.text)

    # Combine extracted information
    card_info = {
        "name": card_name,
        "type": card_type,
        "abilities": abilities,
    }
    
    return card_info

def load_spacy_model():
    spacy_model_dir = os.path.join(SPACY_MODEL_DIR, NLP_MODEL_NAME)
    if not os.path.exists(spacy_model_dir):
        print("SpaCy model directory not found. Please download and save the model.")
        exit(1)
    return spacy.load(spacy_model_dir)

def main():
    check_and_install_prerequisites()
    
    # Create the output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIRECTORY):
        os.makedirs(OUTPUT_DIRECTORY)
    
    # Create the spaCy model directory if it doesn't exist
    if not os.path.exists(SPACY_MODEL_DIR):
        os.makedirs(SPACY_MODEL_DIR)
    
    # Initialize object detection model
    object_detection_model = tf.saved_model.load(OBJECT_DETECTION_MODEL_PATH)
    
    # Load the spaCy model
    nlp = load_spacy_model()
    
    # Get a list of card filenames to process
    card_filenames = [filename for filename in os.listdir(DATA_DIRECTORY) if filename.endswith(".jpg")]
    
    # Create a multiprocessing pool
    num_processes = multiprocessing.cpu_count()
    with multiprocessing.Pool(processes=num_processes) as pool:
        args_list = [(filename, object_detection_model, nlp) for filename in card_filenames]
        results = pool.map(process_card_image, args_list)
    
    # Combine results
    combined_data = [result for result in results if result]
    
    # Write the combined data to the data lake file
    data_lake_path = os.path.join(OUTPUT_DIRECTORY, DATA_LAKE_FILE)
    with open(data_lake_path, "w") as data_lake_output_file:
        json.dump(combined_data, data_lake_output_file, indent=4)
    
    print("Card analysis and data lake update completed.")

if __name__ == "__main__":
    main()

