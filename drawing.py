# Function to draw landmarks and connections on frames

import cv2
from config import connections, landmark_names

def draw_landmarks(frame, landmarks, width, height, highlight_idx=None):
    left_side = {11, 13, 15, 23, 25, 27, 29, 31}
    right_side = {12, 14, 16, 24, 26, 28, 30, 32}
    club_head_id = 1000

    # Connections to skip (start_idx, end_idx)
    skip_connections = {
        (0, 11), (0, 12),  # Nose to shoulders
        (11, 12),          # Left shoulder to right shoulder
        (23, 24)           # Left hip to right hip
    }
    
    # Bottom feet connections to add (if not present already)
    extra_foot_connections = [
        (29, 31),  # Left heel to left foot index
        (30, 32),  # Right heel to right foot index
    ]

    for start_idx, end_idx in extra_foot_connections:
        if start_idx in landmarks and end_idx in landmarks:
            x1, y1 = landmarks[start_idx]
            x2, y2 = landmarks[end_idx]

            if (start_idx in left_side and end_idx in left_side):
                color = (0, 0, 255)  # Red
            elif (start_idx in right_side and end_idx in right_side):
                color = (255, 0, 0)  # Blue
            else:
                color = (0, 255, 255)  # Cyan for cross connection

            cv2.line(frame, (int(x1 * width), int(y1 * height)), (int(x2 * width), int(y2 * height)), color, 5)

    for start_idx, end_idx in connections:
        if (start_idx, end_idx) in skip_connections or (end_idx, start_idx) in skip_connections:
            continue  # Skip these connections
        if start_idx in landmarks and end_idx in landmarks:
            x1, y1 = landmarks[start_idx]
            x2, y2 = landmarks[end_idx]

            if start_idx == club_head_id or end_idx == club_head_id:
                color = (0, 255, 0)  # Green for club head connections
            elif start_idx in left_side and end_idx in left_side:
                color = (0, 0, 255)  # Red
            elif start_idx in right_side and end_idx in right_side:
                color = (255, 0, 0)  # Blue
            else:
                color = (0, 255, 255)  # Cyan for cross-body or unknown

            cv2.line(frame, (int(x1 * width), int(y1 * height)), (int(x2 * width), int(y2 * height)), color, 5)

    for idx, (x, y) in landmarks.items():
        if idx == club_head_id:
            color = (0, 255, 0)
            radius = 5
        elif idx == highlight_idx:
            color = (0, 255, 255)  # Yellow highlight
            radius = 5
        elif idx in left_side:
            color = (0, 0, 255)  # Red
            radius = 5
        elif idx in right_side:
            color = (255, 0, 0)  # Blue
            radius = 5
        else:
            color = (0, 255, 255)  # yellow default
            radius = 25

        cv2.circle(frame, (int(x * width), int(y * height)), radius, color, -1)
