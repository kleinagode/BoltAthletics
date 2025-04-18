import cv2

def read_video(video_path):
    capture = cv2.VideoCapture(video_path)
    if not capture.isOpened():
        print(f"Error: Unable to open video file: {video_path}")
        return [], 0

    fps = capture.get(cv2.CAP_PROP_FPS) # have to match the source fps
    frames = []

    while True:
        ret, frame = capture.read()
        if not ret:
            break
        frames.append(frame)

    capture.release()
    return frames, fps


def save_video(out_video_frames, out_video_path, fps):
    if not out_video_frames:
        print("Warning: No frames to save!")
        return

    height, width = out_video_frames[0].shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(out_video_path, fourcc, fps, (width, height))

    for frame in out_video_frames:
        out.write(frame)
    out.release()


