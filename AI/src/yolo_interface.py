from ultralytics import YOLO

model = YOLO('yolov8x')

INPUT_VIDEO =  "C:\\Users\\klein\\Documents\\GitHub\\BoltAthletics\\AI\\Video\\test_clip.mp4"
results = model.predict(INPUT_VIDEO, save = True, device = 'cuda') # Cuda means use the GPU