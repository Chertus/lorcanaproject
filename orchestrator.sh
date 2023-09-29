#!/bin/bash

# Check if the virtual environment exists
if [ ! -d "lorcana_venv" ]; then
    python3 -m venv lorcana_venv
fi

# Activate the virtual environment
source lorcana_venv/bin/activate

# Upgrade pip to the latest version
pip install --upgrade pip

# List of modules to check and potentially update
MODULES=("tensorflow" "tensorflow-datasets" "spacy" "beautifulsoup4" "pytesseract" "Pillow" "requests" "psutil")

# For each module, check the installed version against the latest version
for MODULE in "${MODULES[@]}"; do
    # Get the installed version
    INSTALLED_VERSION=$(pip show $MODULE | grep "^Version: " | awk '{print $2}')
    
    # Get the latest version available on PyPI
    LATEST_VERSION=$(pip search $MODULE | grep "^$MODULE " | awk '{print $2}' | tr -d '[]')
    
    # If the versions differ, update the module
    if [ "$INSTALLED_VERSION" != "$LATEST_VERSION" ]; then
        pip install --upgrade $MODULE
    fi
done

# Special handling for spaCy's en_core_web_sm model
INSTALLED_SPACY_VERSION=$(python -c "import spacy; print(spacy.about.__version__)" 2>/dev/null)
LATEST_SPACY_VERSION=$(pip search spacy | grep "^spacy " | awk '{print $2}' | tr -d '[]')

if [ "$INSTALLED_SPACY_VERSION" != "$LATEST_SPACY_VERSION" ]; then
    python -m spacy download en_core_web_sm
fi

# Run the Python orchestrator script
python orchestrator.py

# Deactivate the virtual environment
deactivate

