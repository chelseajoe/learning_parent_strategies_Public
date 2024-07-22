# from txt_to_csv import convert_txt_to_csv 
# from mp4_to_frames import split_video_to_frames
# from transcript_chunking import transcript_chunking_process
# from chunk_to_json import extract_interaction_chunks
# from video_annotation
# from interaction_analysis
# from insights_evaluation
# from whitehurst_analysis


# # PART 1: TXT to CSV
# input_file = 'DAMI/p11/s1/p11_s1_transcription.txt'
# output_file = 'CSV_FILES/p11/s1/p11_s1_output.csv'
# convert_txt_to_csv(input_file, output_file)


# # PART 2: MP4 to FRAMES
# csv_file = 'CSV_FILES/p11/s1/p11_s1_output.csv'
# video_path = 'DAMI/p11/s1/p11_s1_vid1.mp4'
# base_output_folder = 'OUTPUT_FRAMES'
# split_video_to_frames(csv_file, video_path, base_output_folder)


# # PART 3: MP4 to FRAMES
# file_path = 'CSV_FILES/p11/s1/p11_s1_output.csv'
# output_txt_path = 'CHUNK_TXT/p11/s1/p11_s1_chunking.txt'
# transcript_chunking_process(file_path, output_txt_path)


# # PART 4: CHUNK to JSON
# txt_file_path = 'CHUNK_TXT/p11/s1/p11_s1_chunking.txt'
# csv_file_path = 'CSV_FILES/p11/s1/p11_s1_output.csv'
# output_json_path = 'CHUNK_DATA/p11/s1/p11_s1_chunk_data.json'
# extract_interaction_chunks(txt_file_path, csv_file_path, output_json_path = 'CHUNK_DATA/p11/s1/p11_s1_chunk_data.json')


# from video_annotation import ...
# from interaction_analysis import ...
# from insights_evaluation import ...
# from whitehurst_analysis import ...


# def process_data(participant, session):
#     # Define file paths dynamically using participant and session
#     input_file = f'DAMI/{participant}/{session}/{participant}_{session}_transcription.txt'
#     output_file = f'CSV_FILES/{participant}/{session}/{participant}_{session}_output.csv'

#     # PART 1: TXT to CSV
#     convert_txt_to_csv(input_file, output_file)

#     # PART 2: MP4 to FRAMES
#     csv_file = output_file
#     video_path = f'DAMI/{participant}/{session}/{participant}_{session}_vid1.mp4'
#     base_output_folder = 'OUTPUT_FRAMES'
#     split_video_to_frames(csv_file, video_path, base_output_folder)

#     # PART 3: Transcript Chunking
#     file_path = csv_file
#     output_txt_path = f'CHUNK_TXT/{participant}/{session}/{participant}_{session}_chunking.txt'
#     transcript_chunking_process(file_path, output_txt_path)

#     # PART 4: CHUNK to JSON
#     txt_file_path = output_txt_path
#     csv_file_path = output_file
#     output_json_path = f'CHUNK_DATA/{participant}/{session}/{participant}_{session}_chunk_data.json'
#     extract_interaction_chunks(txt_file_path, csv_file_path, output_json_path)


# # Example usage
# participant = 'p11'
# session = 's1'
# process_data(participant, session)

# from preprocess_code.txt_to_csv import convert_txt_to_csv 
# from preprocess_code.mp4_to_frames import split_video_to_frames
# from preprocess_code.transcript_chunking import transcript_chunking_process
# from preprocess_code.chunk_to_json import extract_interaction_chunks

# import glob
# import os


# def find_video_path(header_directory, participant, session):
#     directory_pattern = f'{header_directory}/DAMI/{participant}/{session}/'
#     search_pattern = os.path.join(directory_pattern, f'{participant}_{session}_vid*.mp4')
#     video_files = glob.glob(search_pattern)
#     if video_files:
#         return video_files[0]
#     else:
#         return None

# def process_data(header_directory, participant, session):
#     # Define file paths dynamically using header_directory, participant, and session
#     input_file = f'{header_directory}/DAMI/{participant}/{session}/{participant}_{session}_transcription.txt'
#     output_file = f'{header_directory}/CSV_FILES/{participant}/{session}/{participant}_{session}_output.csv'

#     # PART 1: TXT to CSV
#     convert_txt_to_csv(input_file, output_file)

#     # PART 2: MP4 to FRAMES
#     csv_file = output_file
#     video_path = find_video_path(header_directory, participant, session)
#     if video_path:
#         base_output_folder = f'{header_directory}/OUTPUT_FRAMES'
#         split_video_to_frames(csv_file, video_path, base_output_folder)
#     else:
#         print(f"No video file found for {participant} in session {session}")

#     # PART 3: Transcript Chunking
#     file_path = csv_file
#     output_txt_path = f'{header_directory}/CHUNK_TXT/{participant}/{session}/{participant}_{session}_chunking.txt'
#     transcript_chunking_process(file_path, output_txt_path)

#     # PART 4: CHUNK to JSON
#     txt_file_path = output_txt_path
#     csv_file_path = output_file
#     output_json_path = f'{header_directory}/CHUNK_DATA/{participant}/{session}/{participant}_{session}_chunk_data.json'
#     extract_interaction_chunks(txt_file_path, csv_file_path, output_json_path)
    
# # def process_data(header_directory, participant, session):
# #     # Define file paths dynamically using header_directory, participant, and session
# #     input_file = f'{header_directory}/DAMI/{participant}/{session}/{participant}_{session}_transcription.txt'
# #     output_file = f'{header_directory}/CSV_FILES/{participant}/{session}/{participant}_{session}_output.csv'

# #     # PART 1: TXT to CSV
# #     convert_txt_to_csv(input_file, output_file)

# #     # PART 2: MP4 to FRAMES
# #     csv_file = output_file
# #     video_path = f'{header_directory}/DAMI/{participant}/{session}/{participant}_{session}_vid1.mp4'
# #     base_output_folder = f'{header_directory}/OUTPUT_FRAMES'
# #     split_video_to_frames(csv_file, video_path, base_output_folder)

# #     # PART 3: Transcript Chunking
# #     file_path = csv_file
# #     output_txt_path = f'{header_directory}/CHUNK_TXT/{participant}/{session}/{participant}_{session}_chunking.txt'
# #     transcript_chunking_process(file_path, output_txt_path)

# #     # PART 4: CHUNK to JSON
# #     txt_file_path = output_txt_path
# #     csv_file_path = output_file
# #     output_json_path = f'{header_directory}/CHUNK_DATA/{participant}/{session}/{participant}_{session}_chunk_data.json'
# #     extract_interaction_chunks(txt_file_path, csv_file_path, output_json_path)


# # Example usage
# header_directory = 'DATA'
# participant = 'p11'
# session = 's1'
# process_data(header_directory, participant, session)



from DAMI_preprocessing.txt_to_csv import convert_txt_to_csv 
from DAMI_preprocessing.mp4_to_frames import split_video_to_frames
from DAMI_preprocessing.transcript_chunking import transcript_chunking_process
from DAMI_preprocessing.chunk_to_json import extract_interaction_chunks

import glob
import os


def find_video_path(header_directory, participant, session):
    directory_pattern = f'{header_directory}/DAMI/{participant}/{session}/'
    search_pattern = os.path.join(directory_pattern, f'{participant}_{session}_*vid*.mp4')
    video_files = glob.glob(search_pattern)
    if video_files:
        print(f"Found video file(s): {video_files}")
        return video_files[0]
    else:
        print(f"No video file found for search pattern: {search_pattern}")
        return None

def process_data(header_directory, participant, session):
    # Define file paths dynamically using header_directory, participant, and session
    input_file = f'{header_directory}/DAMI/{participant}/{session}/{participant}_{session}_transcription.txt'
    output_file = f'{header_directory}/CSV_FILES/{participant}/{session}/{participant}_{session}_output.csv'

    # PART 1: TXT to CSV
    print("Starting PART 1: TXT to CSV")
    convert_txt_to_csv(input_file, output_file)
    print("Finished PART 1: TXT to CSV\n")

    # PART 2: MP4 to FRAMES
    print("Starting PART 2: MP4 to FRAMES")
    csv_file = output_file
    video_path = find_video_path(header_directory, participant, session)
    if video_path:
        base_output_folder = f'{header_directory}/OUTPUT_FRAMES'
        split_video_to_frames(csv_file, video_path, base_output_folder)
        print("Finished PART 2: MP4 to FRAMES\n")
    else:
        print(f"No video file found for {participant} in session {session}. Skipping PART 2.\n")

    # PART 3: Transcript Chunking
    print("Starting PART 3: Transcript Chunking")
    file_path = csv_file
    output_txt_path = f'{header_directory}/CHUNK_TXT/{participant}/{session}/{participant}_{session}_chunking.txt'
    transcript_chunking_process(file_path, output_txt_path)
    print("Finished PART 3: Transcript Chunking\n")

    # PART 4: CHUNK to JSON
    print("Starting PART 4: CHUNK to JSON")
    txt_file_path = output_txt_path
    csv_file_path = output_file
    output_json_path = f'{header_directory}/CHUNK_DATA/{participant}/{session}/{participant}_{session}_chunk_data.json'
    extract_interaction_chunks(txt_file_path, csv_file_path, output_json_path)
    print("Finished PART 4: CHUNK to JSON\n")

# Example usage
header_directory = 'DATA'
participant = 'p10'
session = 's1'
process_data(header_directory, participant, session)