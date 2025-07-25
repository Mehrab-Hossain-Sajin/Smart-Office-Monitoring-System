# -*- coding: utf-8 -*-
"""Hand Detection in Video.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1fGMv1WfvmWLo-GcQmujGtNrbLS1oJGeW

**Mehrab Hossain Sajin**
"""

# 📌 STEP 0: INSTALL REQUIRED LIBRARIES
!pip install opencv-python mediapipe matplotlib

# 📌 STEP 1: IMPORT LIBRARIES
import cv2
import mediapipe as mp
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import Video, display
from google.colab import files

# 📌 STEP 2: UPLOAD IMAGE AND VIDEO FILES
print("⬆️ Please upload 'desk.png' and 'desk_video.mp4'")
uploaded = files.upload()

import cv2
import numpy as np
import matplotlib.pyplot as plt

video_path = "desk_video.mp4"
desk_img_path = "desk.png"

# Define desk bounding boxes (based on desk image layout)
desks = {
    "TANVIR":   (60,  160, 120, 280),
    "SHAFAYET":(140, 160, 200, 280),
    "TOUFIQ":  (220, 160, 280, 280),
    "FAISAL":  (300, 160, 370, 280),
    "MUFRAD":  (380, 160, 440, 280),
    "ANIK":    (460, 160, 520, 280),
    "IMRAN":   (540, 160, 600, 280),
    "EMON":    (620, 160, 680, 280),
}

cap = cv2.VideoCapture(video_path)
fgbg = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=50, detectShadows=False)

output_frames = []
raised_frames = []
frame_idx = 0

# Keep history of motion counts for smoothing
motion_history = {name: 0 for name in desks.keys()}
motion_threshold = 2  # how many frames a hand must be seen
decay = 0.85  # motion score decay factor per frame

while True:
    ret, frame = cap.read()
    if not ret:
        break

    motion_mask = fgbg.apply(frame)
    thresh = cv2.threshold(motion_mask, 200, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    current_motion = set()

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 800:
            continue  # skip small motion

        x, y, w, h = cv2.boundingRect(cnt)
        cx, cy = x + w // 2, y + h // 2

        for name, (dx1, dy1, dx2, dy2) in desks.items():
            # Define strict raised-hand zone above desk
            rx1, ry1, rx2, ry2 = dx1, dy1 - 80, dx2, dy1 - 20
            if rx1 <= cx <= rx2 and ry1 <= cy <= ry2:
                current_motion.add(name)

    # Update motion history
    for name in desks.keys():
        if name in current_motion:
            motion_history[name] += 1
        else:
            motion_history[name] *= decay
            if motion_history[name] < 0.1:
                motion_history[name] = 0

    # Annotate frame
    detected_now = []
    for name, (x1, y1, x2, y2) in desks.items():
        if motion_history[name] >= motion_threshold:
            detected_now.append(name)
            cv2.rectangle(frame, (x1, y1 - 60), (x2, y1), (0, 255, 0), 2)
            cv2.putText(frame, f"{name} Raised Hand", (x1, y1 - 65),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Draw desk box & label
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 1)
        cv2.putText(frame, name, (x1, y2 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

    if detected_now:
        print(f"Frame {frame_idx}: {', '.join(detected_now)} raised hand")
        raised_frames.append((frame_idx, detected_now))

    output_frames.append(frame)
    frame_idx += 1

cap.release()

# Save result
output_path = "motion_based_output.mp4"
height, width, _ = output_frames[0].shape
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, 10, (width, height))

for frame in output_frames:
    out.write(frame)
out.release()

# ✅ Download the video result file
from google.colab import files
files.download(output_path)

