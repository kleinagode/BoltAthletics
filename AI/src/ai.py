import cv2
from ultralytics import YOLO
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

# Load the YOLOv8 model (pre-trained on COCO dataset)
model = YOLO('yolov8n.pt')

# Load the basketball game video
video_path = "C:\\Users\\klein\\Documents\\GitHub\\BoltAthletics\\AI\\Video\\test_clip.mp4"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error: Could not open video file.")
    exit()

# Set up the Matplotlib figure
fig, ax = plt.subplots()
img_display = ax.imshow(np.zeros((720, 1280, 3), dtype=np.uint8))
plt.axis('off')

# Update function for animation
def update(frame):
    ret, frame = cap.read()
    if not ret:
        cap.release()
        plt.close()
        return

    # Use YOLO to detect objects in the frame
    results = model(frame)

    # Loop through detections
    for result in results[0].boxes.data:
        x1, y1, x2, y2, score, class_id = result.tolist()
        class_name = results[0].names[int(class_id)]

        # Draw bounding boxes for players
        if class_name == "person" and score > 0.5:
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

    # Convert frame to RGB for Matplotlib
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img_display.set_data(frame_rgb)

# Use FuncAnimation to create the video effect
ani = FuncAnimation(fig, update, interval=1)
plt.show()

cap.release()
cv2.destroyAllWindows()