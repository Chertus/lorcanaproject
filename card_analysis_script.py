#!/usr/bin/env python

import os
import json
import cv2
import pytesseract
import tensorflow as tf
import subprocess
import importlib
import numpy as np
from PIL import Image
import pytesseract
import multiprocessing
import shutil
import spacy

# Constants
REQUIRED_PACKAGES_FILE = "requirements.txt"
DATA_DIRECTORY = "data"
OUTPUT_DIRECTORY = "output"
CLEANED_CARD_DATA_FILE = "cleaned_card_data.json"
DATA_LAKE_FILE = "data_lake.json"
SPACY_MODEL_DIR = "spacy_models"
OBJECT_DETECTION_MODEL_PATH = "fine_tuned_object_detection_model"
NLP_MODEL_NAME = "en_core_web_sm"
CONFIDENCE_THRESHOLD_OBJECT_DETECTION = 0.5
CONFIDENCE_THRESHOLD_NLP = 0.7

# Function to check and install prerequisites
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

# Function to extract text from an image using Tesseract OCR
def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, config="--psm 6")
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from {image_path}: {str(e)}")
        return ""

# Function to process a single card image
def process_card_image(card_filename, result_queue):
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
    for token in doc:
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
    
    # Write the intermediate result to a temporary file
    temp_file = os.path.join(OUTPUT_DIRECTORY, f"{card_name}_temp.json")
    with open(temp_file, "w") as temp_output_file:
        json.dump(card_info, temp_output_file, indent=4)
    
    # Put the temp_file path into the result queue
    result_queue.put(temp_file)

# Function to load the spaCy model
def load_spacy_model():
    spacy_model_dir = os.path.join(SPACY_MODEL_DIR, NLP_MODEL_NAME)
    if not os.path.exists(spacy_model_dir):
        print("SpaCy model directory not found. Please download and save the model.")
        exit(1)
    return spacy.load(spacy_model_dir)

if __name__ == "__main__":
    check_and_install_prerequisites()
    
    # Create the output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIRECTORY):
        os.makedirs(OUTPUT_DIRECTORY)
    
    # Create the spaCy model directory if it doesn't exist
    if not os.path.exists(SPACY_MODEL_DIR):
        os.makedirs(SPACY_MODEL_DIR)
    
    # Initialize object detection model
    object_detection_model = tf.saved_model.load(OBJECT_DETECTION_MODEL_PATH)
    
    # Load the spaCy model (or download and save it if not available)
    nlp = load_spacy_model()
    
    # Get a list of card filenames to process
    card_filenames = [filename for filename in os.listdir(DATA_DIRECTORY) if filename.endswith(".jpg")]
    
    # Create a multiprocessing pool
    num_processes = multiprocessing.cpu_count()  # Adjust the number of processes as needed
    pool = multiprocessing.Pool(processes=num_processes)
    
    # Create a queue for collecting temporary result file paths
    result_queue = multiprocessing.Queue()
    
    # Process card images in parallel
    for card_filename in card_filenames:
        pool.apply_async(process_card_image, (card_filename, result_queue))
    
    # Close the pool and wait for all processes to complete
    pool.close()
    pool.join()
    
    # Combine the intermediate results from temporary files
    combined_data = []
    while not result_queue.empty():
        temp_file = result_queue.get()
        with open(temp_file, "r") as temp_input_file:
            card_info = json.load(temp_input_file)
            combined_data.append(card_info)
        # Remove the temporary file
        os.remove(temp_file)
    
    # Write the combined data to the data lake file
    data_lake_path = os.path.join(OUTPUT_DIRECTORY, DATA_LAKE_FILE)
    with open(data_lake_path, "w") as data_lake_output_file:
        json.dump(combined_data, data_lake_output_file, indent=4)
    
    print("Card analysis and data lake update completed.")

