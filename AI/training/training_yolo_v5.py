# Does not work


from yolov5 import train

# Location to the dataset
dataset_location =  "C:\\Users\\klein\\Documents\\GitHub\\BoltAthletics\\AI\\training\\basketball-players-detection-2"

# Train the model
train.run(
    task='detect',
    mode='train',
    model='yolov5x.pt',
    data=f'{dataset_location}\\data.yaml',
    epochs=100,
    imgsz=640
)
