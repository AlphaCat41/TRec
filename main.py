import tkinter as tk
from tkinter import filedialog, BooleanVar, Checkbutton
from PIL import ImageGrab
import threading
import time
import cv2
import numpy as np
import pyaudio
import subprocess
import os
import wave

class TRec:
    def __init__(self, window):
        self.window = window

        window.title('VidRec')
        window.geometry("400x100")
        self.fps = 10
        self.frame_time = 1 / self.fps

        self.isRecording = None 

        self.screen_frames = []   
        self.audio_frames = []
        self.audio_timestamps = []
        self.video_timestamps = [] 

        self.final_file = None
        self.video_file = None
        self.audio_file = None

        self.start_btn = tk.Button(window, text='Start', width=10, command=self.start_recording)
        self.start_btn.grid(row=1, column=0, padx=5, pady=10)

        self.stop_btn = tk.Button(window, text='Stop', width=10, command=self.stop_recording)
        self.stop_btn.grid(row=1, column=1, padx=5)

        self.save_btn = tk.Button(window, text='Save', width=10, command=self.save_recording)
        self.save_btn.grid(row=1, column=2, padx=5)

        self.hasMic = BooleanVar()
        self.chk_mic_btn = Checkbutton(self.window, text='microphone', variable=self.hasMic)
        self.chk_mic_btn.grid(row=0, column=0, padx=5)
      
    def start_recording(self):
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.ACTIVE)
        self.chk_mic_btn.config(state=tk.DISABLED)

        if self.hasMic.get():
            # Start audio recording in a separate thread
            audio_thread = threading.Thread(target=self.record_audio)
            audio_thread.start()
            
        self.isRecording = True  # Clear the event flag to start recording
        screen_thread = threading.Thread(target=self.record_screen)
        screen_thread.start()
     
      
    def stop_recording(self):
        self.isRecording = False
        self.stop_btn.config(state=tk.DISABLED)
        self.start_btn.config(state=tk.ACTIVE)

    def save_recording(self):
        self.save_dir = filedialog.askdirectory(title="Select a directory to save recordings")

        if self.save_dir:
            self.save_all_recording()
            if self.hasMic.get():
                self.merge_audio_video()

            self.isRecording = False
            self.screen_frames = []
            self.audio_frames = []    
            self.start_btn.config(state=tk.ACTIVE)
            self.stop_btn.config(state=tk.ACTIVE)
            self.chk_mic_btn.config(state=tk.ACTIVE)

            tk.messagebox.showinfo("Info",  f"Video saved to '{self.save_dir}' successfully.")


    def record_screen(self):
        while self.isRecording:
            start_time = time.time()

            screenshot = ImageGrab.grab()  # Capture the screen
            self.screen_frames.append(screenshot)  # Save the screenshot as frames

            diff_time = time.time() - start_time
            if diff_time < self.frame_time: # Ensure 10 FPS
                time.sleep(self.frame_time - diff_time)

    def record_audio(self):
        # PyAudio setup
        chunk = 1024  # Record in chunks of 1024 samples
        format = pyaudio.paInt16  # 16 bits per sample
        channels = 2
        rate = 44100  # Record at 44100 samples per second
        
        p = pyaudio.PyAudio()
        stream = p.open(format=format,
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk)
        
        while self.isRecording:
            start_time = time.time()

            data = stream.read(chunk)
            self.audio_frames.append(data)

            diff_time = time.time() - start_time
          
            if diff_time > chunk / rate:
                time.sleep(diff_time - (chunk / rate))

        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        p.terminate()

    def save_all_recording(self):
        self.isRecording = False
        
        if self.hasMic.get():
            self.audio_file = os.path.join(self.save_dir, "audio.wav")
            
            # Save recorded audio to a file
            wf = wave.open(self.audio_file, 'wb')
            wf.setnchannels(2)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(self.audio_frames))
            wf.close()

        self.video_file = os.path.join(self.save_dir, "video.mp4")
        frame = self.screen_frames[0]
        width, height = frame.size
        out = cv2.VideoWriter(self.video_file, cv2.VideoWriter_fourcc(*'mp4v'), 10, (width, height))

        for frame in self.screen_frames:
            frame_np = np.array(frame)
            out.write(cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR))

        out.release()

    def merge_audio_video(self):
        self.output_file = os.path.join(self.save_dir, "output_video.mp4")     
        ffmpeg_path = os.getcwd() + "/ffmpeg/bin/ffmpeg.exe"

        command = f'"{ffmpeg_path}" -y -i "{self.video_file}" -i "{self.audio_file}" -c:v copy -c:a aac "{self.output_file}"' # -y for overwrite video & audio

        try:
            subprocess.run(command, shell=True, check=True)

        except subprocess.CalledProcessError as e:
            print(f"Error occurred: {e}")

if __name__ == "__main__":
    window = tk.Tk()
    TRec(window)
    window.mainloop()
