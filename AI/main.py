# Very dependant on the quality of the footage

from util import read_video, save_video
from trackers import Tracker
from team_assigner import TeamAssigner
from camera_movement_estimator import CameraMovementEstimator


def main():
    # Read Videos and fps
    video_frames, fps = read_video('video/test_clip_3.mp4')

    # Init the tracker
    tracker = Tracker('models/basketbal_computer_vision.pt')

    tracks = tracker.get_obj_tracks(video_frames,
                                    read_from_stub=True,
                                    stub_path='stubs/track_stubs.pkl')

    # Get object positions 
    tracker.add_position_to_tracks(tracks)

    # Camera Movement Estimator
    camera_movement_estimator = CameraMovementEstimator(video_frames[0])
    camera_movement_per_frame = camera_movement_estimator.get_camera_movement(video_frames,
                                                                                read_from_stub=True,
                                                                                stub_path='stubs/camera_movement_stub.pkl')
    camera_movement_estimator.add_adjust_positions_to_tracks(tracks,camera_movement_per_frame)

    # Assign Players to Teams
    team_assigner = TeamAssigner()
    team_assigner.assign_team_color(video_frames[0], tracks["players"][0])

    for frame_num, player_track in enumerate(tracks['players']):
        for player_id, track in player_track.items():
            team = team_assigner.get_player_team(video_frames[frame_num],
                                                 track['bbox'],
                                                 player_id)
            
            tracks['players'][frame_num][player_id]['team'] = team
            tracks['players'][frame_num][player_id]['team_color'] = team_assigner.team_colors[team]


    # Draw Output
    # Draw Object Tracks
    outut_video_frames = tracker.draw_annotations(video_frames, tracks)

    # Draw Camera Movement
    outut_video_frames = camera_movement_estimator.draw_camera_movement(outut_video_frames, camera_movement_per_frame)

    # Save video and match the fps
    save_video(outut_video_frames, 'output_videos/Bolt_atletics_analyzed.avi', fps)

if __name__ == '__main__':
    main()