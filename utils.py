# Helper functions for saving, interpolation, smoothing mediapipe pose landmarks.

import json
import cv2
import numpy as np
from config import landmark_names, connections

def save_edits(filename, edits):                                                                    # Saving edited landmarks dictionary to a JSON file 
    with open(filename, "w") as f:
        json.dump({str(k): v for k, v in edits.items()}, f, indent=2)
    print(f"Saved edits to {filename}")

def interpolate_landmarks(lm_start, lm_end, alpha):                                                 # Linearly interpolate landmark positions between two frames with 'alpha' ranging from 0 (start frame) to 1 (end frame)
    return {
        idx: (
            lm_start[idx][0] + alpha * (lm_end[idx][0] - lm_start[idx][0]),
            lm_start[idx][1] + alpha * (lm_end[idx][1] - lm_start[idx][1])
        )
        for idx in lm_start if idx in lm_end
    }

def blend_landmarks(lm_interp, lm_mediapipe, blend_factor):                                         # Blend interpolated landmarks with detected MediaPipe landmarks - 'blend_factor' weights the interpolation (1 = full interp, 0 = full mediapipe).
    return {
        idx: (
            blend_factor * lm_interp[idx][0] + (1 - blend_factor) * lm_mediapipe[idx][0],
            blend_factor * lm_interp[idx][1] + (1 - blend_factor) * lm_mediapipe[idx][1]
        )
        for idx in lm_interp if idx in lm_mediapipe
    }

def smooth_path(path, window_size=5):                                                               # Smooth a path of (x, y) points by averaging over a sliding window 
    if len(path) < window_size:
        return path
    smoothed = []
    for i in range(len(path)):
        x_vals, y_vals = zip(*path[max(0, i - window_size + 1):i + 1])
        smoothed.append((int(sum(x_vals) / len(x_vals)), int(sum(y_vals) / len(y_vals))))
    return smoothed

def get_landmark_at_pos(landmarks, x, y, width, height, radius=10):
    for idx, (lx, ly) in landmarks.items():
        px, py = int(lx * width), int(ly * height)
        if (px - x)**2 + (py - y)**2 <= radius**2:
            return idx
    return None



param_dict = {
    "selected_landmark_idx": None,
    "dragging": False
}

def mouse_callback(event, x, y, flags, param):
    current_landmarks = param["current_landmarks"]
    edited_landmarks = param["edited_landmarks"]
    current_frame_index = param["current_frame_index"]
    width = param["width"]
    height = param["height"]
    landmark_names = param["landmark_names"]

    if not current_landmarks:
        return

    x = int(x / 0.75)
    y = int(y / 0.75)

    if event == cv2.EVENT_LBUTTONDOWN:
        idx = get_landmark_at_pos(current_landmarks, x, y, width, height)
        if idx is not None:
            param["selected_landmark_idx"] = idx
            param["dragging"] = True
            print(f"Selected landmark {landmark_names.get(idx, idx)} for dragging.")
    elif event == cv2.EVENT_LBUTTONUP:
        param["dragging"] = False
        param["selected_landmark_idx"] = None
    elif event == cv2.EVENT_MOUSEMOVE and param.get("dragging") and param.get("selected_landmark_idx") is not None:
        nx, ny = x / width, y / height
        nx, ny = max(0.0, min(1.0, nx)), max(0.0, min(1.0, ny))
        current_landmarks[param["selected_landmark_idx"]] = (nx, ny)
        edited_landmarks[current_frame_index] = current_landmarks.copy()

    