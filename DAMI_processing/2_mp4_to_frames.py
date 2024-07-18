import cv2
import os
import pandas as pd


def split_video_to_frames(csv_file, video_path, base_output_folder):
    frame_buffer = 45
    frame_rate = 30

    # Load CSV file to get timestamps
    df = pd.read_csv(csv_file)
    
    # Convert Timestamp to seconds
    df['Seconds'] = df['Timestamp'].str.split(':').apply(lambda x: int(x[0]) * 60 + int(x[1]))

    print(f"Current working directory: {os.getcwd()}")

    # Parse the video_path to get the desired subfolder structure
    filename = os.path.basename(video_path)
    parts = filename.split('_')
    
    if len(parts) >= 2:
        subfolder = f"{parts[0]}/{parts[1]}"
    else:
        print("Error: Video filename does not contain enough parts to form the output folder structure.")
        return

    # Create the output folder path
    output_folder = os.path.join(base_output_folder, subfolder)

    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    print(f"Video path: {video_path}")
    print(f"Output folder: {output_folder}")
    print(f"Current working directory: {os.getcwd()}")

    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    # Check if the video file exists
    if not os.path.isfile(video_path):
        print(f"Error: Video file {video_path} does not exist.")
        return

    # Check if the video opened successfully
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    for index, row in df.iterrows():
        # Convert timestamp to frame number
        frame_number = row['Seconds'] * frame_rate
        
        # Add 45 frame buffer
        original_frame_number = frame_number
        frame_number += frame_buffer
        
        # Set frame number
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        
        # Read the frame
        ret, frame = cap.read()

        # If the frame was not read successfully, subtract the buffer and try again
        if not ret:
            frame_number = frame_number - frame_buffer
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()
        
        print(frame_number)

        # Construct the filename for the output image
        frame_filename = os.path.join(output_folder, f"frame_{frame_number:04d}.png")
        
        # Save the frame as an image
        cv2.imwrite(frame_filename, frame)

        # Print progress every 1000 frames
        if index % 10 == 0:
            print(f"Processed {index} frames...")

    # Release the video capture object
    cap.release()
    print(f"Processed {len(df)} frames to '{output_folder}'.")

# Usage
# csv_file = 'csv_files/p10_s2_output.csv'
# video_path = 'DAMI/p10/s2/p10_s2_mainvid.mp4'
csv_file = 'CSV_FILES/p11/s1/p11_s1_output.csv'
video_path = 'DAMI/p11/s1/p11_s1_vid1.mp4'
base_output_folder = 'OUTPUT_FRAMES'
split_video_to_frames(csv_file, video_path, base_output_folder)
