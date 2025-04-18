from ultralytics import YOLO

model = YOLO('models/basketbal_computer_vision.pt')

INPUT_VIDEO =  "video/test_clip_3.mp4"
results = model.predict(INPUT_VIDEO, save = True, device = 'cuda:0') # Cuda means use the GPU
