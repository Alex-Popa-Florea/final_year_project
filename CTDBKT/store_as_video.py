import os
import cv2

def store_video(cap):
    # Check if the 'raw_videos' directory exists, and create it if it doesn't
    if not os.path.exists('raw_videos'):
        os.makedirs('raw_videos')

    # Get the list of existing files in the "raw_videos" directory
    existing_files = os.listdir('raw_videos')

    # Check if there are existing files
    if existing_files:
        # Find the highest video count from existing file names
        # Note: We exclude '.DS_Store' files (common on macOS) from consideration
        video_count = max([int(file_name.split('_')[2].split('.')[0]) for file_name in existing_files if file_name != '.DS_Store']) + 1
    else:
        # If no existing files, start the video count at 0
        video_count = 0

    # Create a VideoWriter to save the cropped video
    fourcc = cv2.VideoWriter_fourcc(*'H264')
    output_path = os.path.join('raw_videos', f"raw_video_{video_count}.mp4")
    
    # Set up the VideoWriter with the same frame size and a frame rate of 20 frames per second
    writer = cv2.VideoWriter(output_path, fourcc, 20.0, (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
    
    # Return the VideoWriter object
    return writer

def store_video_titled(cap, unique_uids, tid):
    # Check if the 'user_study' directory exists, and create it if it doesn't
    if not os.path.exists('user_study'):
        os.makedirs('user_study')

    # Get the list of existing files in the "user_study" directory
    existing_files = os.listdir('user_study')

    # Create a VideoWriter to save the cropped video
    fourcc = cv2.VideoWriter_fourcc(*'H264')
    output_path = os.path.join('user_study', f"user_study_{str(unique_uids)}_{str(tid)}.mp4")
    
    # Set up the VideoWriter with the same frame size and a frame rate of 20 frames per second
    writer = cv2.VideoWriter(output_path, fourcc, 20.0, (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
    
    # Return the VideoWriter object
    return writer
