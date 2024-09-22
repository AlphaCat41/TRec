import tkinter as tk

class VidRec:
    def __init__(self, window):
        self.window = window
        window.title('VidRec')
        window.geometry("400x100") 
        self.isRecord = False
        self.data_record = []       

        self.start_btn = tk.Button(window, text='Start', width=10, command=self.start_record)
        self.start_btn.grid(row=1, column=1, padx=5, pady=10)

        self.stop_btn = tk.Button(window, text='Stop', width=10, command=self.stop_record)
        self.stop_btn.grid(row=1, column=2, padx=5)

        self.save_btn = tk.Button(window, text='Save', width=10, command=self.save_record)
        self.save_btn.grid(row=1, column=3, padx=5)

    def start_record(self):
        self.isRecord = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.ACTIVE)

    def stop_record(self):
        self.isRecord = False
        self.stop_btn.config(state=tk.DISABLED)
        self.start_btn.config(state=tk.ACTIVE)

    def save_record(self):
        self.start_btn.config(state=tk.ACTIVE)
        self.stop_btn.config(state=tk.ACTIVE)
        self.data_record = []

if __name__ == "__main__":
    window = tk.Tk()
    VidRec(window)
    window.mainloop()
