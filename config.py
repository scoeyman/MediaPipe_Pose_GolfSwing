# Contains global constants and landmark definitions used by the main.py code

import cv2
import mediapipe as mp

# Paths for Video Input and Outputs
VIDEO_PATH = r"E:\golf swing ai\swings\4_tiger driver\Tiger - Driver1Front.mp4"                 # video file being processed
SAVE_FILE = r"E:\golf swing ai\swings\4_tiger driver\edited_landmarks.json"                     # text file to save mediapipe pose landmark locations
OUTPUT_PATH = r"E:\golf swing ai\swings\4_tiger driver\playback_output.mp4"                     # pose predictions on top of original video save location 
OUTPUT_PATH_BLACK = r"E:\golf swing ai\swings\4_tiger driver\playback_black.mp4"                # pose predictions with back background save location 

# Settings for Editing
EDIT_JUMP = 1                                                                                   # frames to jump when going next/previous while editing video predictions     
MAX_PATH_LENGTH = 5                                                                             # number of points stored for club head path smoothing (club head trail)

# Landmark Definitions - Different Body Part Locations
landmark_names = {
    0: 'NOSE',
    11: 'LEFT_SHOULDER', 12: 'RIGHT_SHOULDER',
    13: 'LEFT_ELBOW', 14: 'RIGHT_ELBOW',
    15: 'LEFT_WRIST', 16: 'RIGHT_WRIST', 
    23: 'LEFT_HIP', 24: 'RIGHT_HIP',
    25: 'LEFT_KNEE', 26: 'RIGHT_KNEE',
    27: 'LEFT_ANKLE', 28: 'RIGHT_ANKLE',
    29: 'LEFT_HEEL', 30: 'RIGHT_HEEL',
    31: 'LEFT_FOOT_INDEX', 32: 'RIGHT_FOOT_INDEX',
    1000: 'CLUB_HEAD'}                                                                          # 1000 is a custom landmark to track club head

# Add custom landmarks like CLUB_HEAD
custom_landmarks = {
    1000: 'CLUB_HEAD'
}
landmark_names.update(custom_landmarks)

# Landmark Connections - Drawing Lines Between Body Part Locations
connections = [
    (11, 13), (13, 15), (12, 14), (14, 16),
    (11, 12), (23, 24), (23, 25), (25, 27),
    (24, 26), (26, 28), (27, 29), (28, 30),
    (27, 31), (28, 32), (11, 23), (12, 24),
    (0, 11), (0, 12)]

