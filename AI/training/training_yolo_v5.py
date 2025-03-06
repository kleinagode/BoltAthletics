
from roboflow import Roboflow
from api_key import Auth
API_KEY = Auth().key

rf = Roboflow(api_key=API_KEY)
project = rf.workspace("kyles-workspace").project("basketball-players-detection-flths")
version = project.version(2)
dataset = version.download("yolov5")
                