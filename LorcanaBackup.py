import shutil

# Source directory to be backed up
source_directory = "/home/thomas/Lorcana"

# Destination directory (network share)
destination_directory = "\\\\thomasnas\\Shared\\Projects\\Lorcana"

try:
    # Perform the backup by copying the source to the destination
    shutil.copytree(source_directory, destination_directory)
    print(f"Backup completed successfully from {source_directory} to {destination_directory}")
except Exception as e:
    print(f"An error occurred during the backup: {str(e)}")

