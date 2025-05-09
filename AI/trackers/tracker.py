from ultralytics import YOLO
import supervision as sv
import pickle
import os
import sys
import cv2

# Go in the root folder
sys.path.append("../")
from util import get_center_of_bbox, get_width_of_bbox, get_foot_position

class Tracker:

    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.tracker = sv.ByteTrack()


    def add_position_to_tracks(sekf,tracks):
        for object, object_tracks in tracks.items():
            for frame_num, track in enumerate(object_tracks):
                for track_id, track_info in track.items():
                    bbox = track_info['bbox']
                    if object == 'ball':
                        position= get_center_of_bbox(bbox)
                    else:
                        position = get_foot_position(bbox)
                    tracks[object][frame_num][track_id]['position'] = position


    def detect_frames(self, frames):
        batch_size = 20
        detections = []

        for i in range(0, len(frames), batch_size):
            detections_batch = self.model.predict(frames[i:i+batch_size], conf=0.1)
            detections+= detections_batch
            
        return detections

    def get_obj_tracks(self, frames, read_from_stub=False, stub_path = None):
        
        # For reading from a file for faster dev
        if read_from_stub and stub_path is not None and os.path.exists(stub_path):
            with open(stub_path, 'rb') as  f:
                tracks = pickle.load(f)
            return tracks

        detections = self.detect_frames(frames)

        tracks = {
            "players": [],
            "referees": [],
            "ball": []
        }

        for frame_num, detection, in enumerate(detections):
            cls_names = detection.names
            cls_names_inv = {v:k for k,v in cls_names.items()}

            # Convert to supervision detection format
            detection_supervision = sv.Detections.from_ultralytics(detection)

            # Track obj
            detection_with_tracks = self.tracker.update_with_detections(detection_supervision)

            tracks["players"].append({})
            tracks["referees"].append({})
            tracks["ball"].append({})

            for frame_detection in detection_with_tracks:
                bbox = frame_detection[0].tolist()
                cls_id = frame_detection[3]
                track_id = frame_detection[4]

                if cls_id == cls_names_inv["Player"]:
                    tracks["players"][frame_num][track_id] = {"bbox": bbox}

                
                if cls_id == cls_names_inv["Ref"]:
                    tracks["referees"][frame_num][track_id] = {"bbox": bbox}

            # Only tracking one ball
            for frame_detection in detection_supervision:
                bbox = frame_detection[0].tolist()
                cls_id = frame_detection[3]
                
                if cls_id == cls_names_inv["Ball"]:
                    tracks["ball"][frame_num][1] = {"bbox": bbox}

        if stub_path is not None:
            with open(stub_path, 'wb') as f:
                pickle.dump(tracks, f) 

        # A list of dictionaries
        return tracks       

    def draw_elipse(self, frame, bbox, color, track_id=None):
        
        y2 = int(bbox[3]) # We want the elipse at the bottom
        x_center, _= get_center_of_bbox(bbox)
        width = get_width_of_bbox(bbox)

        cv2.ellipse(
            frame,
            center=(x_center,y2),
            axes=(int(width), int(0.35*width)),
            angle=0.0,
            startAngle=-45,
            endAngle=235,
            color=color,
            thickness=2,
            lineType= cv2.LINE_4
        )

        rectangle_width = 40
        rectangle_height = 20
        x1_rect = x_center - rectangle_width//2
        x2_rect = x_center + rectangle_width//2
        y1_rect = (y2 - rectangle_height//2) + 15
        y2_rect = (y2 + rectangle_height//2) + 15
        
        if track_id is not None:
            cv2.rectangle(
                frame,
                (int(x1_rect), int(y1_rect)),
                (int(x2_rect), int(y2_rect)),
                color,
                cv2.FILLED
            )

            # Visuall only
            x1_txt = x1_rect + 12
            if track_id > 99:
                x1_txt-= 10

            cv2.putText(
                frame,
                f"{track_id}",
                (int(x1_txt), int(y1_rect+15)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0,0,0),
                2
            )


        return frame

    def draw_ball_circle(self, frame, bbox, color, track_id=None):
       
        x_center, y_center = get_center_of_bbox(bbox)

        
        radius = int(get_width_of_bbox(bbox) / 2)

        # Draw the circle
        cv2.circle(
            frame,
            center=(int(x_center), int(y_center)),
            radius=radius,
            color=color,
            thickness=2,
            lineType=cv2.LINE_AA
        )

        return frame

    def draw_annotations(self, video_frames, tracks):

        # With custom bounding boxes
        output_video_frames = []                                         
               
        for frame_num, frame in enumerate(video_frames):
            frame = frame.copy() # So we don't pollute the list

            # Extracting the dicts
            player_dict = tracks["players"][frame_num] 
            ball_dict = tracks["ball"][frame_num] 
            ref_dict = tracks["referees"][frame_num]

            # Draw Players
            for track_id, player in player_dict.items():
                # Give Players their team colors
                color = player.get("team_color", (0,0,255))
                frame = self.draw_elipse(frame, player["bbox"], color, track_id)

            # Draw Refs
            for _, ref in ref_dict.items():
                frame = self.draw_elipse(frame, ref["bbox"], (255,0,255))

            # Draw Ball
            for _, ball in ball_dict.items():
                frame = self.draw_ball_circle(frame, ball["bbox"], (255,255,255))

            output_video_frames.append(frame)

        return output_video_frames