from ultralytics import YOLO

model = YOLO('basketbal_computer_vision.pt')

INPUT_VIDEO =  "C:\\Users\\klein\\Documents\\GitHub\\BoltAthletics\\AI\\Video\\test_clip_4.mp4"
results = model.predict(INPUT_VIDEO, save = True, device = 'cuda:0') # Cuda means use the GPU