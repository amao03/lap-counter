import cv2
import numpy as np

def warm_video(input_video, output_video, warmth_factor):
    cap = cv2.VideoCapture(input_video)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video, fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Increase the red and decrease the blue channels
        frame[:, :, 2] = np.clip(frame[:, :, 2] + warmth_factor, 0, 255)
        frame[:, :, 0] = np.clip(frame[:, :, 0] - warmth_factor // 2, 0, 255)

        out.write(frame)

    cap.release()
    out.release()