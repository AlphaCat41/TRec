import tkinter as tk
from tkinter import ttk
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
import sys
from pydub import AudioSegment

class TRec:
    def __init__(self, window):
        self.window = window

        window.title('TRec')
        window.geometry("400x120")
        self.fps = 10
        self.rate = 44100  # Record at 44100 samples per second
        self.frame_time = 1 / self.fps
        self.seconds = 0

        self.isRecording = None 

        self.screen_frames = []   
        self.audio_frames = []
     
        self.final_file = None
        self.video_file = None
        self.audio_file = None

        self.start_btn = tk.Button(window, text='Start', width=10, command=self.start_recording)
        self.start_btn.grid(row=1, column=0, padx=5, pady=10)

        self.stop_btn = tk.Button(window, text='Stop', width=10, command=self.stop_recording)
        self.stop_btn.grid(row=1, column=1, padx=5)
        self.stop_btn.config(state=tk.DISABLED)

        self.save_btn = tk.Button(window, text='Save', width=10, command=self.save_recording)
        self.save_btn.grid(row=1, column=2, padx=5)
        self.save_btn.config(state=tk.DISABLED)

        self.hasMic = BooleanVar()
        self.chk_mic_btn = Checkbutton(self.window, text='microphone', variable=self.hasMic, command=self.setStateCombobox)
        self.chk_mic_btn.grid(row=0, column=0, padx=5)

        self.combo_box = ttk.Combobox(window, values=self.list_audio_devices())
        self.combo_box.grid(row=0, column=1, padx=5)
        self.combo_box.config(state= tk.DISABLED)

        self.timer_label = tk.Label(window, text="00:00:00", font=("Helvetica", 35))
        self.timer_label.grid(row=2, column=1, padx=5)
      
    def setStateCombobox(self):
        if self.hasMic.get():
            self.combo_box.config(state= tk.ACTIVE)
        else:
            self.combo_box.config(state= tk.DISABLED)

    def updateTime(self):
        if self.isRecording:
            minutes = self.seconds // 60
            seconds = self.seconds % 60

            if (minutes > 60):
                hours = minutes // 60
                minutes = minutes % 60
            else:
                hours = 0

            time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            self.timer_label.config(text=time_str)
            self.window.after(1000, self.updateTime) # Update every 1 second
            self.seconds += 1

    def clear(self):
        self.seconds = 0
        self.isRecording = False
        self.timer_label.config(text="00:00:00")
        self.screen_frames = []
        self.audio_frames = []    
        self.start_btn.config(state=tk.ACTIVE)
        self.stop_btn.config(state=tk.ACTIVE)
        self.save_btn.config(state=tk.DISABLED)
        self.chk_mic_btn.config(state=tk.ACTIVE)

    def list_audio_devices(self):
        devices = []
        p = pyaudio.PyAudio()

        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:  # Filter to show only input devices
                devices.append(f"{i}: {device_info['name']}")

        return devices

    def start_recording(self):
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.ACTIVE)
        self.save_btn.config(state=tk.ACTIVE)
        self.chk_mic_btn.config(state=tk.DISABLED)

        if self.hasMic.get():
            # Start audio recording in a separate thread
            if not self.combo_box.get():
                tk.messagebox.showinfo("Info",  f"Please select audio device")
                self.clear()
                return
            
            self.input_device_index = int(self.combo_box.get().split(':')[0])
            audio_thread = threading.Thread(target=self.record_audio)
            audio_thread.start()
            
        self.isRecording = True  # Clear the event flag to start recording
        screen_thread = threading.Thread(target=self.record_screen)
        screen_thread.start()
        self.updateTime()
     
      
    def stop_recording(self):
        self.isRecording = False
        self.stop_btn.config(state=tk.DISABLED)
        self.start_btn.config(state=tk.ACTIVE)
        self.save_btn.config(state=tk.ACTIVE)

    def save_recording(self):
        self.save_dir = filedialog.askdirectory(title="Select a directory to save recordings")

        if self.save_dir:
            self.save_all_recording()
            if self.hasMic.get():
                self.merge_audio_video()

            self.clear()
            tk.messagebox.showinfo("Info",  f"Video saved to '{self.save_dir}' successfully.")


    def record_screen(self):
        try:
            while self.isRecording:
                start_time = time.time()

                screenshot = ImageGrab.grab()  # Capture the screen
                self.screen_frames.append(screenshot)  # Save the screenshot as frames

                diff_time = time.time() - start_time

                if diff_time < self.frame_time: # Ensure 10 FPS
                    time.sleep(self.frame_time - diff_time)

        except Exception as e:
            tk.messagebox.showerror("Error",  f"{e}")
            self.clear()
            sys.exit(1)  # Exit with an error status

    def record_audio(self):
        # PyAudio setup
        format = pyaudio.paInt16  # 16 bits per sample
        channels = 2
        chunk = int(self.rate / self.fps)  # Record in chunks of 1024 samples

        try:
            p = pyaudio.PyAudio()
            stream = p.open(format=format,
                            channels=channels,
                            rate=self.rate,
                            input=True,
                            input_device_index=self.input_device_index,
                            frames_per_buffer=chunk)
            
            while self.isRecording:
                start_time = time.time()

                data = stream.read(chunk)
                self.audio_frames.append(data)

                diff_time = time.time() - start_time
            
                if diff_time < self.frame_time: # Ensure 10 FPS
                    time.sleep(self.frame_time - diff_time)

        except Exception as e:
            tk.messagebox.showerror("Error",  f"{e}")
            self.clear()
            sys.exit(1)  # Exit with an error status
            
        finally:
            # Stop and close the stream
            self.isRecording = False
            stream.stop_stream()
            stream.close()
            p.terminate()

    # Amplify the Audio
    def amplify_audio(self, input_file, output_file, increase_db=10):
        sound = AudioSegment.from_wav(input_file)
        louder_sound = sound + increase_db  # Increase volume by X decibels
        louder_sound.export(output_file, format="wav")
        self.audio_file = output_file

    def save_all_recording(self):
        self.isRecording = False
        
        try:
            if self.hasMic.get():
                self.audio_file = os.path.join(self.save_dir, "audio.wav")
                
                # Save recorded audio to a file
                wf = wave.open(self.audio_file, 'wb')
                wf.setnchannels(2)
                wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
                wf.setframerate(44100)
                wf.writeframes(b''.join(self.audio_frames))
                wf.close()

                amplified_audio_file = os.path.join(self.save_dir, "audio.wav")
                self.amplify_audio(self.audio_file, amplified_audio_file, increase_db=20)

            self.video_file = os.path.join(self.save_dir, "video.mp4")
            frame = self.screen_frames[0]
            width, height = frame.size
            out = cv2.VideoWriter(self.video_file, cv2.VideoWriter_fourcc(*'mp4v'), 10, (width, height))

            for frame in self.screen_frames:
                frame_np = np.array(frame)
                out.write(cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR))

            out.release()

        except Exception as e:
            tk.messagebox.showerror("Error",  f"{e}")
            sys.exit(1)  # Exit with an error status

    def merge_audio_video(self):
        self.output_file = os.path.join(self.save_dir, "output_video.mp4")     

        command = f'ffmpeg -y -i "{self.video_file}" -i "{self.audio_file}" -c:v copy -c:a aac "{self.output_file}"' # -y for overwrite video & audio

        try:
            subprocess.run(command, shell=True, check=True)

        except subprocess.CalledProcessError as e:
            tk.messagebox.showerror("Error",  f"{e}")        
            self.clear()      
            sys.exit(1)

if __name__ == "__main__":
    window = tk.Tk()
    TRec(window)
    window.mainloop()
