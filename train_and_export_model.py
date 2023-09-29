import tensorflow as tf
import tensorflow_datasets as tfds
import os
import logging

# Constants
DATASET_NAME = "Lorcana"
DATA_DIR = "/path/to/dataset_directory"
SAVED_MODEL_DIR = "/path/to/saved_model_directory"
PRETRAINED_MODEL_DIR = "/path/to/pretrained_model_directory"

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ensure TensorFlow and TFDS are updated
subprocess.run(["pip", "install", "--upgrade", "tensorflow", "tensorflow-datasets"], check=True)

def get_latest_dataset_version():
    """Get the latest version of the dataset."""
    versions = tfds.builder(DATASET_NAME).versions
    latest_version = str(versions[-1])
    return latest_version

def load_dataset():
    """Load the dataset with a specific subsplit."""
    dataset_version = get_latest_dataset_version()
    logging.info(f"Using dataset version: {dataset_version}")

    (train_data, test_data), info = tfds.load(
        DATASET_NAME,
        split=[f"train[{60}%:]{dataset_version}", f"train[:{60}%]{dataset_version}"],
        data_dir=DATA_DIR,
        as_supervised=True,
        with_info=True,
    )
    return train_data, test_data, info

def train_and_evaluate_model(train_data, test_data):
    """Train and evaluate the model."""
    # Define and compile your TensorFlow model
    model = tf.keras.Sequential([
        tf.keras.layers.Flatten(input_shape=(28, 28)),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(10)
    ])

    model.compile(optimizer='adam',
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                  metrics=['accuracy'])

    # Train the model
    history = model.fit(train_data, epochs=5, validation_data=test_data)

    # Evaluate the model
    test_loss, test_accuracy = model.evaluate(test_data, verbose=2)
    logging.info(f"Test accuracy: {test_accuracy}")

    return model

def main():
    if not os.path.exists(SAVED_MODEL_DIR):
        os.makedirs(SAVED_MODEL_DIR)

    # Load the dataset
    train_data, test_data, info = load_dataset()

    # Check if a trained model already exists
    if os.listdir(SAVED_MODEL_DIR):
        logging.info("Using the existing trained model.")
        model = tf.keras.models.load_model(SAVED_MODEL_DIR)
    else:
        logging.info("Training a new model.")
        model = train_and_evaluate_model(train_data, test_data)
        model.save(SAVED_MODEL_DIR)

    # Optionally, you can perform further operations with the loaded model

if __name__ == "__main__":
    main()

