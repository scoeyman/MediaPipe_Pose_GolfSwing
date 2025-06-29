import cv2
import bisect
import numpy as np
import json
import mediapipe as mp
import config
import utils
from drawing import draw_landmarks


def main():
    # Load the video and get video properties
    cap = cv2.VideoCapture(config.VIDEO_PATH)
    width, height = int(cap.get(3)), int(cap.get(4))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Set up video writers for output (with and without overlays)
    out = cv2.VideoWriter(config.OUTPUT_PATH, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
    out_black = cv2.VideoWriter(config.OUTPUT_PATH_BLACK, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    # Initializing MediaPipe Pose
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()

    # Load saved landmark edits, or initialize empty variable
    try:
        with open(config.SAVE_FILE, "r") as f:
            edited_landmarks_raw = json.load(f)
        edited_landmarks = {int(k): v for k, v in edited_landmarks_raw.items()}
    except FileNotFoundError:
        edited_landmarks = {}

    sorted_frames = sorted(edited_landmarks.keys())
    current_frame_index = 0
    current_landmarks = {}
    mode = 'edit'
    club_head_path = []
    selected_landmark_idx = None
    dragging = False
    cached_results = None
    cached_frame_index = -1
    last_loaded_frame = None

    param_dict = {
        "current_landmarks": current_landmarks,
        "edited_landmarks": edited_landmarks,
        "current_frame_index": current_frame_index,
        "width": width,
        "height": height,
        "landmark_names": config.landmark_names
    }

    cv2.namedWindow("Pose Editor/Playback")
    cv2.setMouseCallback("Pose Editor/Playback", utils.mouse_callback, param_dict)


    while True:
        cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_index)
        ret, frame = cap.read()
        if not ret:
            print("End of video.")
            break

        if current_frame_index != cached_frame_index:
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cached_results = pose.process(image_rgb)
            cached_frame_index = current_frame_index

        results = cached_results

        if mode == 'edit':
            if current_frame_index != last_loaded_frame:
                if current_frame_index in edited_landmarks:
                    current_landmarks = {int(k): tuple(v) for k, v in edited_landmarks[current_frame_index].items()}
                elif results.pose_landmarks:
                    current_landmarks = {
                        idx: (results.pose_landmarks.landmark[idx].x, results.pose_landmarks.landmark[idx].y)
                        for idx in config.landmark_names if idx < 1000
                    }
                else:
                    current_landmarks = {}
                last_loaded_frame = current_frame_index

                # Add CLUB_HEAD if not already present
                if 1000 not in current_landmarks and 16 in current_landmarks:
                    rx, ry = current_landmarks[16]  # Right wrist
                    current_landmarks[1000] = (rx + 0.05, ry + 0.05)
            
            param_dict["current_landmarks"] = current_landmarks
            param_dict["current_frame_index"] = current_frame_index
            
            draw_landmarks(frame, current_landmarks, width, height, selected_landmark_idx)
            text = f"Edit Mode | Frame: {current_frame_index}"
            if selected_landmark_idx is not None:
                name = config.landmark_names.get(selected_landmark_idx, str(selected_landmark_idx))
                x, y = current_landmarks[selected_landmark_idx]
                text += f" | Editing {name} at ({x:.3f}, {y:.3f})"
            cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            scaled_frame = cv2.resize(frame, (int(frame.shape[1] * 0.75), int(frame.shape[0] * 0.75)))
            cv2.imshow("Pose Editor/Playback", scaled_frame)

            key = cv2.waitKey(int(1000 / fps)) & 0xFF
            if key == ord('q'):
                utils.save_edits(config.SAVE_FILE, edited_landmarks)
                break
            elif key == ord('s'):
                edited_landmarks[current_frame_index] = current_landmarks.copy()
                sorted_frames = sorted(edited_landmarks.keys())
                print(f"Saved frame {current_frame_index}")
            elif key == ord('n'):
                current_frame_index = min(current_frame_index + config.EDIT_JUMP, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1)
            elif key == ord('p'):
                current_frame_index = max(current_frame_index - config.EDIT_JUMP, 0)
            elif key == ord('d'):
                if current_frame_index in edited_landmarks:
                    del edited_landmarks[current_frame_index]
                    sorted_frames = sorted(edited_landmarks.keys())
                    print(f"Deleted frame {current_frame_index}")
            elif key == ord('c'):
                current_landmarks[1000] = (0.5, 0.5)
                print("Added CLUB_HEAD at (0.5, 0.5)")
            elif key == ord('m'):
                print("Switching to playback mode")
                mode = 'playback'

        elif mode == 'playback':
            if len(edited_landmarks) == 0:
                landmarks_to_draw = {
                    idx: (results.pose_landmarks.landmark[idx].x, results.pose_landmarks.landmark[idx].y)
                    for idx in config.landmark_names if idx < 1000 and results.pose_landmarks
                }
            else:
                pos = bisect.bisect_left(sorted_frames, current_frame_index)
                if current_frame_index in edited_landmarks:
                    landmarks_to_draw = {int(k): tuple(v) for k, v in edited_landmarks[current_frame_index].items()}
                elif pos == 0:
                    if results.pose_landmarks:
                        landmarks_to_draw = {
                            idx: (results.pose_landmarks.landmark[idx].x, results.pose_landmarks.landmark[idx].y)
                            for idx in config.landmark_names if idx < 1000
                        }
                    else:
                        landmarks_to_draw = {}
                elif pos >= len(sorted_frames):
                    landmarks_to_draw = {int(k): tuple(v) for k, v in edited_landmarks[sorted_frames[-1]].items()}
                else:
                    f0, f1 = sorted_frames[pos - 1], sorted_frames[pos]
                    lm0 = {int(k): tuple(v) for k, v in edited_landmarks[f0].items()}
                    lm1 = {int(k): tuple(v) for k, v in edited_landmarks[f1].items()}
                    alpha = (current_frame_index - f0) / (f1 - f0)
                    interp = utils.interpolate_landmarks(lm0, lm1, alpha)

                    if results.pose_landmarks:
                        mp_landmarks = {
                            idx: (results.pose_landmarks.landmark[idx].x, results.pose_landmarks.landmark[idx].y)
                            for idx in config.landmark_names if idx < 1000
                        }
                    else:
                        mp_landmarks = interp

                    blend_factor = max(0.3, min(1.0, 1.0 - abs(0.5 - alpha) * 2))
                    landmarks_to_draw = utils.blend_landmarks(interp, mp_landmarks, blend_factor)
                    for cid in config.custom_landmarks:
                        if cid in lm0 and cid in lm1:
                            landmarks_to_draw[cid] = (
                                lm0[cid][0] + alpha * (lm1[cid][0] - lm0[cid][0]),
                                lm0[cid][1] + alpha * (lm1[cid][1] - lm0[cid][1])
                            )

            # Update club head path list for path tracer
            club_head_id = 1000
            if club_head_id in landmarks_to_draw:
                cx, cy = landmarks_to_draw[club_head_id]
                px, py = int(cx * width), int(cy * height)
                club_head_path.append((px, py))
                if len(club_head_path) > config.MAX_PATH_LENGTH:
                    club_head_path.pop(0)
            else:
                club_head_path.clear()  # Clear if club head missing

            param_dict["current_landmarks"] = current_landmarks
            param_dict["edited_landmarks"] = edited_landmarks
            param_dict["current_frame_index"] = current_frame_index
            
            draw_landmarks(frame, landmarks_to_draw, width, height)
            
            # Draw club head path tracer (fading green trail)
            smoothed_path = utils.smooth_path(club_head_path, window_size=5)
            for i in range(1, len(smoothed_path)):
                start_point = smoothed_path[i - 1]
                end_point = smoothed_path[i]
                alpha = i / len(smoothed_path)  # 0 to 1 for fade
                color = (0, 255, 0)  
                thickness = 3
                cv2.line(frame, start_point, end_point, color, thickness)

            cv2.putText(frame, f"Playback Mode | Frame: {current_frame_index} | Press 'm' for edit",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            scaled_frame = cv2.resize(frame, (int(frame.shape[1] * 0.75), int(frame.shape[0] * 0.75)))
            cv2.imshow("Pose Editor/Playback", scaled_frame)

            # === Output 1: Original video frame with overlay ===
            out.write(frame)

            # === Output 2: Black background version ===
            black_frame = np.zeros_like(frame)
            draw_landmarks(black_frame, landmarks_to_draw, width, height)
            for i in range(1, len(smoothed_path)):
                cv2.line(black_frame, smoothed_path[i - 1], smoothed_path[i], (0, 255, 0), 3)
            out_black.write(black_frame)

            key = cv2.waitKey(int(1000 / fps)) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('m'):
                print("Switching to edit mode")
                mode = 'edit'
                last_loaded_frame = None
            elif key == ord('n'):
                current_frame_index = min(current_frame_index + 1, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1)
            elif key == ord('p'):
                current_frame_index = max(current_frame_index - 1, 0)
            else:
                current_frame_index = min(current_frame_index + 1, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1)

    out.release()
    out_black.release()
    print(f"Playback saved to {config.OUTPUT_PATH}")
    print(f"Black playback saved to {config.OUTPUT_PATH_BLACK}")


