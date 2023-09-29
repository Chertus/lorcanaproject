import shutil
import os
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Source directory to be backed up
source_directory = "/home/thomas/Lorcana"

# Destination directory (network share)
base_destination_directory = "\\\\thomasnas\\Shared\\Projects\\Lorcana"

# Create a timestamped backup directory
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
destination_directory = os.path.join(base_destination_directory, f"backup_{timestamp}")

try:
    # Check if the base destination directory exists
    if not os.path.exists(base_destination_directory):
        logging.error(f"Base destination directory {base_destination_directory} does not exist.")
        exit(1)

    # Perform the backup by copying the source to the destination
    shutil.copytree(source_directory, destination_directory)
    logging.info(f"Backup completed successfully from {source_directory} to {destination_directory}")

except shutil.Error as e:
    # This captures errors during the copy process such as file permissions issues.
    logging.error(f"Error copying files: {e}")
except OSError as e:
    # This captures OS-related errors, such as directory not found.
    logging.error(f"OS error: {e}")
except Exception as e:
    logging.error(f"An unexpected error occurred during the backup: {e}")


