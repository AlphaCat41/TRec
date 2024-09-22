import tkinter as tk
from tkinter import filedialog
from PIL import ImageGrab
import threading
import time
import cv2
import numpy as np
class TRec:
    def __init__(self, window):
        self.window = window
        window.title('VidRec')
        window.geometry("400x100")
        self.isRecording = None 
        self.screen_frames = []     

        self.start_btn = tk.Button(window, text='Start', width=10, command=self.start_recording)
        self.start_btn.grid(row=1, column=1, padx=5, pady=10)

        self.stop_btn = tk.Button(window, text='Stop', width=10, command=self.stop_recording)
        self.stop_btn.grid(row=1, column=2, padx=5)

        self.save_btn = tk.Button(window, text='Save', width=10, command=self.save_recording)
        self.save_btn.grid(row=1, column=3, padx=5)

    def start_recording(self):
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.ACTIVE)
        
        self.isRecording = True  # Clear the event flag to start recording
        screen_thread = threading.Thread(target=self.record_screen)
        screen_thread.start()
     
      
    def stop_recording(self):
        self.isRecording = False
        self.stop_btn.config(state=tk.DISABLED)
        self.start_btn.config(state=tk.ACTIVE)

    def save_recording(self):
        self.save_screen_recording()

        self.screen_frames = []  
        self.start_btn.config(state=tk.ACTIVE)
        self.stop_btn.config(state=tk.ACTIVE)


    def record_screen(self):
        while self.isRecording:
            screenshot = ImageGrab.grab()  # Capture the screen
            self.screen_frames.append(screenshot)  # Save the screenshot as frames
            time.sleep(0.1)  # Adjust the frame rate if needed (here ~10 FPS)

    def save_screen_recording(self):
        # Ask user to select a file name for saving
        file_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])
        
        if not file_path:
            return
        frame = self.screen_frames[0]
        width, height = frame.size
        out = cv2.VideoWriter(file_path, cv2.VideoWriter_fourcc(*'mp4v'), 10, (width, height))

        for frame in self.screen_frames:
            frame_np = np.array(frame)
            out.write(cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR))

        out.release()

        tk.messagebox.showinfo("Info",  "Video saved successfully.")

if __name__ == "__main__":
    window = tk.Tk()
    TRec(window)
    window.mainloop()
