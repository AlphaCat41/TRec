# TRec
Screen and audio recording program
## Bugs
- [x] Unsynchronized between audio and video (Fixed by Calculate CHUNK_SIZE)
    - CHUNK_SIZE = RATE / FPS [samples / frame]
        - Audio Sample Rate (RATE) = 44,100 samples per second (standard audio sampling rate)
        - Video Frame Rate (FPS) = 30 frames per second (typical video frame rate). 
- [x] Cannot record the audio output (Fixed by use Stereo Mix)

## Dependencies
1. FFmpeg (https://phoenixnap.com/kb/ffmpeg-windows) Extract in TRec folder
## How to run
1. install packages
```
pip freeze > requirements.txt
```
```
pip install -r requirements.txt
```
2. Run main.py
```
python main.py
```
