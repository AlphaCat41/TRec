# TRec
Screen and audio recording program
## Bugs
- [ ] Unsynchronized between audio and video
- [x] Cannot record sound in screen (Fixed by Enable Stereo Mix)
## How to Enable Stereo Mix (Windows):
1. Right-click the Sound Icon in the system tray.
2. Select "Sounds".
3. Go to the "Recording" tab.
4. Right-click in the empty area and choose "Show Disabled Devices".
5. Find "Stereo Mix", right-click it, and select "Enable".
6. Set it as the default device if needed.
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
