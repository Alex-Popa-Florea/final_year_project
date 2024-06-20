import os
import cv2

# Function to store a user study video
def store_video_titled(cap, unique_uids, tid):
    if not os.path.exists('user_study'):
        os.makedirs('user_study')

    fourcc = cv2.VideoWriter_fourcc(*'H264')
    output_path = os.path.join('user_study', f"user_study_{str(unique_uids)}_{str(tid)}.mp4")
    
    writer = cv2.VideoWriter(output_path, fourcc, 1.0, (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
    
    return writer
