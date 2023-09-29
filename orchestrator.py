import tkinter as tk
from tkinter import ttk
import threading
import time
import random  # This is for simulating the comprehension percentage. You can replace this with actual logic.
import os

class OrchestratorGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Lorcana Orchestrator and Training")
        self.geometry("500x400")

        # Orchestrator section
        self.orchestrator_frame = ttk.LabelFrame(self, text="Orchestrator", padding=(10, 5))
        self.orchestrator_frame.pack(padx=10, pady=10, fill=tk.X)

        self.script_names = ["requirements.txt", "lorcana_rules_extractor.py", "image_association.py", "interactions_json.py", "locanaapipull.py", "text_analysis.py", "train_and_export_model.py"]
        self.script_status = {name: ttk.Label(self.orchestrator_frame, text=name) for name in self.script_names}

        for name, label in self.script_status.items():
            label.pack(anchor=tk.W, pady=2)

        # Training section
        self.training_frame = ttk.LabelFrame(self, text="Training", padding=(10, 5))
        self.training_frame.pack(padx=10, pady=10, fill=tk.X)

        self.start_button = ttk.Button(self.training_frame, text="Start Training", command=self.start_training)
        self.start_button.pack(pady=10)

        self.stop_button = ttk.Button(self.training_frame, text="Stop Training", command=self.stop_training, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        self.comprehension_label = ttk.Label(self.training_frame, text="Comprehension: 0%")
        self.comprehension_label.pack(pady=10)

    def run_script(self, script_name):
        # Check if the script_name ends with .py to determine if it's a Python script
        if script_name.endswith(".py"):
            os.system(f"python {script_name}")
        # Simulate running for non-Python scripts (like requirements.txt)
        else:
            time.sleep(random.randint(2, 5))
        label = self.script_status[script_name]
        label.config(text=script_name + " ✓", foreground="green")

    def start_orchestrator(self):
        for script in self.script_names:
            self.run_script(script)

    def start_training(self):
        self.start_button["state"] = tk.DISABLED
        self.stop_button["state"] = tk.NORMAL
        self.training_thread = threading.Thread(target=self.train_model)
        self.training_thread.start()

    def stop_training(self):
        self.start_button["state"] = tk.NORMAL
        self.stop_button["state"] = tk.DISABLED
        # Logic to stop the training and save the model

    def train_model(self):
        comprehension = 0
        while comprehension < 90:  # Simulating until comprehension exceeds 90%
            time.sleep(1)  # Simulating training time
            comprehension += random.randint(1, 5)  # Simulating comprehension increase
            comprehension = min(comprehension, 90)
            self.comprehension_label.config(text=f"Comprehension: {comprehension}%")

    def run(self):
        orchestrator_thread = threading.Thread(target=self.start_orchestrator)
        orchestrator_thread.start()
        self.mainloop()

if __name__ == "__main__":
    app = OrchestratorGUI()
    app.run()

