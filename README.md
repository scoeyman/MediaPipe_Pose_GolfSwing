PoseLandmark Video Editor
----------------------------
An interactive Python tool built on [MediaPipe](https://google.github.io/mediapipe/) and OpenCV to edit, interpolate, and visualize human pose landmarks in video files (specifically golf swings).


Features
-----------
- Frame-by-frame manual landmark editing
- Custom landmarks (e.g., golf club head support)
- Drag & drop interface for precise control
- Smoothed landmark interpolation in playback


How to Run
------------
1. Place your input video path in `config.py`
2. Run the main script: main.py
3. Keyboard Controls:
- q = Quit and save
- s = Save current frame’s landmarks
- n	= Next frame (by EDIT_JUMP)
- p	= Previous frame
- d	= Delete edits for current frame
- c	= Add custom CLUB_HEAD point
- m	= Toggle edit/playback mode


Configuration (config.py)
---------------------------
You can modify these parameters for loading and saving videos:
VIDEO_PATH = "input_video.mp4"
OUTPUT_PATH = "output_video.mp4"
OUTPUT_PATH_BLACK = "output_black.mp4"
SAVE_FILE = "edited_landmarks.json"


Output
--------
- A JSON file is saved with edited landmarks: edited_landmarks.json
- output_video.mp4: with original background and overlays
- output_black.mp4: black background + pose + smoothed club path


Requirements
-------------
Install dependencies with: pip install -r requirements.txt
