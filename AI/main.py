from util import read_video, save_video
from trackers import Tracker

def main():
    # Read Videos and fps
    video_frames, fps = read_video('video/test_clip_3.mp4')

    # Init the tracker
    tracker = Tracker('models/basketbal_computer_vision.pt')

    tracks = tracker.get_obj_tracks(video_frames,
                                    read_from_stub=True,
                                    stub_path='stubs/track_stubs.pkl')

    # Draw Output
    # Draw Object Tracks
    outut_video_frames = tracker.draw_annotations(video_frames, tracks)


    # Save video and match the fps
    save_video(outut_video_frames, 'output_videos/Bolt_atletics_analyzed.avi', fps)

if __name__ == '__main__':
    main()