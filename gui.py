import tkinter as tk
from tkinter import ttk
import multiprocessing
import train_until_comprehension
import queue
import psutil

class TrainingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Training GUI")

        self.frame = ttk.Frame(self.root, padding="10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.start_button = ttk.Button(self.frame, text="Start Training", command=self.start_training)
        self.start_button.grid(row=0, column=0, sticky=tk.W, pady=5)

        self.stop_button = ttk.Button(self.frame, text="Stop Training", command=self.stop_training, state=tk.DISABLED)
        self.stop_button.grid(row=1, column=0, sticky=tk.W, pady=5)

        self.estimated_time_label = ttk.Label(self.frame, text="Estimated Time Remaining: N/A")
        self.estimated_time_label.grid(row=2, column=0, sticky=tk.W, pady=5)

        self.cpu_label = ttk.Label(self.frame, text="CPU Usage: N/A")
        self.cpu_label.grid(row=3, column=0, sticky=tk.W, pady=5)

        self.memory_label = ttk.Label(self.frame, text="Memory Usage: N/A")
        self.memory_label.grid(row=4, column=0, sticky=tk.W, pady=5)

        self.disk_label = ttk.Label(self.frame, text="Disk Utilization: N/A")
        self.disk_label.grid(row=5, column=0, sticky=tk.W, pady=5)

        self.process = None
        self.queue = multiprocessing.Queue()

    def update_resource_monitor(self):
        cpu_usage = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()
        disk_usage = psutil.disk_usage('/')

        self.cpu_label["text"] = f"CPU Usage: {cpu_usage}%"
        self.memory_label["text"] = f"Memory Usage: {memory_info.percent}%"
        self.disk_label["text"] = f"Disk Utilization: {disk_usage.percent}%"

        self.root.after(2000, self.update_resource_monitor)

    def update_timer(self):
        try:
            estimated_time = self.queue.get_nowait()
            self.estimated_time_label["text"] = f"Estimated Time Remaining: {estimated_time:.2f} seconds"
            self.root.after(1000, self.update_timer)
        except queue.Empty:
            self.root.after(1000, self.update_timer)

    def start_training(self):
        self.process = multiprocessing.Process(target=train_until_comprehension.main, args=(self.queue,))
        self.process.start()
        self.start_button["state"] = tk.DISABLED
        self.stop_button["state"] = tk.NORMAL
        self.update_timer()
        self.update_resource_monitor()

    def stop_training(self):
        if self.process:
            self.process.terminate()
            self.process.join()
        self.start_button["state"] = tk.NORMAL
        self.stop_button["state"] = tk.DISABLED
        self.estimated_time_label["text"] = "Estimated Time Remaining: N/A"

app = tk.Tk()
TrainingApp(app)
app.mainloop()

