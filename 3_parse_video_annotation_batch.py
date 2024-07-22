# import os
# import json
# import base64
# import asyncio

# def process_frames(folder_path, output_file, json_file, transcripts, frame_rate=30):
#     # Load JSON file to get interaction chunks
#     with open(json_file, 'r') as file:
#         data = json.load(file)

#     # Check if the output directory exists, if not, create it
#     output_dir = os.path.dirname(output_file)
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)

#     frame_info = {}

#     for chunk_index, chunk in enumerate(data):
#         frame_images = []
#         frame_numbers = []
#         chunk_transcripts = transcripts[chunk_index]  # Get transcripts for this chunk

#         for line_index, line in enumerate(chunk['Lines']):
#             # Convert Timestamp to seconds
#             minutes, seconds = map(int, line['Timestamp'].split(':'))
#             total_seconds = minutes * 60 + seconds
#             print("TOTAL SECONDS: ", total_seconds)

#             # Calculate frame number
#             frame_number = total_seconds * frame_rate + 45
#             print("FRAME NUMBER: ", frame_number)
#             frame_path = os.path.join(folder_path, f"frame_{frame_number:04d}.png")

#             if not os.path.exists(frame_path):
#                 print(f"Frame: {frame_number} before subtraction")
#                 frame_number -= 45
#                 print(f"Frame: {frame_number} after subtraction")
#                 frame_path = os.path.join(folder_path, f"frame_{frame_number:04d}.png")

#             if os.path.exists(frame_path):
#                 print(f"Processing frame: {frame_path}")
#                 # Encode the image to base64
#                 base64_image = encode_image(frame_path)
#                 frame_images.append(base64_image)
#                 frame_numbers.append(frame_number)
#             else:
#                 print(f"Frame {frame_number} does not exist.")

#         # Update frame_info with analyzed frames for the current chunk
#         frame_info[chunk_index] = {
#             'frame_numbers': frame_numbers,
#             'transcripts': chunk_transcripts
#         }

#     # Save the frame info to a JSON file or any other storage
#     with open(output_file, 'w') as file:
#         json.dump(frame_info, file, indent=4)

#     print(f"Frame analysis saved to {output_file}")

# def encode_image(image_path):
#     with open(image_path, "rb") as image_file:
#         return base64.b64encode(image_file.read()).decode('utf-8')


# def extract_jsonl_content(file_path, frame_info_file):
#     """
#     Reads a JSONL file and extracts the 'content' field from each line while
#     printing the frame numbers that were analyzed.

#     Parameters:
#     file_path (str): Path to the JSONL file.
#     frame_info_file (str): Path to the JSON file containing frame analysis info.

#     Returns:
#     list: A list of tuples where each tuple contains content and analyzed frames.
#     """
#     contents = []

#     try:
#         with open(file_path, 'r') as file:
#             data = [json.loads(line.strip()) for line in file]
        
#         with open(frame_info_file, 'r') as file:
#             frame_info = json.load(file)

#         for i, chunk in enumerate(data):
#             try:
#                 content = chunk['response']['body']['choices'][0]['message']['content']
#                 analyzed_frames = frame_info.get(i, {}).get('frame_numbers', [])
#                 contents.append((content, analyzed_frames))
#             except KeyError:
#                 print(f"KeyError: Missing expected fields in line {i + 1} of {file_path}")

#     except FileNotFoundError:
#         print(f"FileNotFoundError: The file {file_path} does not exist.")
#     except json.JSONDecodeError:
#         print(f"JSONDecodeError: Error decoding JSON in file {file_path}.")
    
#     return contents


# # Example usage
# output_folder = 'DATA/OUTPUT_FRAMES/p11/s1'
# output_file = 'DATA/ANNOTATIONS/p11/s1/p11_s1_chunk_annotations.json'
# json_file = 'DATA/CHUNK_DATA/p11/s1/p11_s1_chunk_data.json'
# jsonl_file_path = 'DATA/BATCH/ANNOTATION_OUTPUT/p07/s2/p07_s2_batch_annotation_output.jsonl'
# # Extract transcripts and process frames
# transcripts = extract_jsonl_content(jsonl_file_path)
# process_frames(output_folder, output_file, json_file, transcripts)

# # def encode_image(image_path):
# #     with open(image_path, "rb") as image_file:
# #         return base64.b64encode(image_file.read()).decode('utf-8')

# # # Example usage
# # output_folder = 'DATA/OUTPUT_FRAMES/p11/s1'
# # output_file = 'DATA/ANNOTATIONS/p11/s1/p11_s1_chunk_annotations.json'
# # json_file = 'DATA/CHUNK_DATA/p11/s1/p11_s1_chunk_data.json'

# # process_frames(output_folder, output_file, json_file)

# # # Example usage
# # jsonl_file_path = 'path/to/your/file.jsonl'
# # frame_info_file = 'ANNOTATIONS/p11/s1/p11_s1_chunk_annotations.json'
# # content_list = extract_jsonl_content(jsonl_file_path, frame_info_file)

# # for i, (content, frames) in enumerate(content_list):
# #     frames_str = ', '.join(map(str, frames))
# #     print(f"Content {i + 1}:\n{content}\nFrames: {frames_str}\n")

# import json

# def extract_jsonl_content(file_path):
#     """
#     Reads a JSONL file and extracts the 'content' field from each line.

#     Parameters:
#     file_path (str): Path to the JSONL file.

#     Returns:
#     list: A list of content strings extracted from the JSON objects.
#     """
#     contents = []
    
#     try:
#         with open(file_path, 'r') as file:
#             for line in file:
#                 # Parse the JSON object from the line
#                 json_obj = json.loads(line.strip())
                
#                 # Extract the 'content' field if available
#                 try:
#                     content = json_obj['response']['body']['choices'][0]['message']['content']
#                     contents.append(content)
#                 except KeyError:
#                     print(f"KeyError: Missing expected fields in line: {line}")
    
#     except FileNotFoundError:
#         print(f"FileNotFoundError: The file {file_path} does not exist.")
#     except json.JSONDecodeError:
#         print(f"JSONDecodeError: Error decoding JSON in file {file_path}.")
    
#     return contents

# # Example usage
# jsonl_file_path = 'DATA/BATCH/ANNOTATION_OUTPUT/p07/s2/p07_s2_batch_annotation_output.jsonl'
# output_json_file = 'DATA/ANNOTATIONS/p11/s1/p11_s1_chunk_annotations.json'
# content_list = extract_jsonl_content(jsonl_file_path)
# for i, content in enumerate(content_list):
#     print(f"Interaction Episode {i + 1}:\n{content}\n")

import json
import os
import re

def clean_and_parse_content(content):
    # Split the content into lines
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Remove unnecessary characters like '---', '**', '##' and trim whitespace
        stripped_line = line.strip()
        if stripped_line and not re.match(r'^\s*[-*#]+', stripped_line):
            cleaned_lines.append(stripped_line)
        # cleaned_lines.append(stripped_line)
    
    return cleaned_lines

def extract_and_save_jsonl_content(file_path, output_file_path):
    episodes = {}
    episode_counter = 1

    try:
        with open(file_path, 'r') as file:
            content_accumulator = []
            for line in file:
                # print(line)
                # Parse the JSON object from the line
                json_obj = json.loads(line.strip())
                
                # Extract the 'content' field if available
                try:
                    content = json_obj['response']['body']['choices'][0]['message']['content']
                    # Clean and parse the content into lines
                    parsed_lines = clean_and_parse_content(content)
                    print(content)
                    content_accumulator.extend(parsed_lines)
                    
                    # When we detect the end of an interaction episode, save it
                    # if 'end-of-episode' in content:  # Assuming a marker for end of episode
                    episodes[f"Interaction Episode {episode_counter}"] = {"scene": content_accumulator}
                    content_accumulator = []
                    episode_counter += 1
                except KeyError:
                    print(f"KeyError: Missing expected fields in line: {line}")

    except FileNotFoundError:
        print(f"FileNotFoundError: The file {file_path} does not exist.")
        return
    except json.JSONDecodeError:
        print(f"JSONDecodeError: Error decoding JSON in file {file_path}.")
        return

    # Add the last episode if there is any remaining content
    if content_accumulator:
        episodes[f"Interaction Episode {episode_counter}"] = {"scene": content_accumulator}

    # Save the content dictionary to the output JSON file
    try:
        with open(output_file_path, 'w') as file:
            json.dump(episodes, file, indent=4)
        print(f"Data successfully saved to {output_file_path}.")
    except IOError:
        print(f"IOError: Error writing to file {output_file_path}.")

# # Example usage
# jsonl_file_path = 'DATA/BATCH/ANNOTATION_OUTPUT/p07/s2/p07_s2_batch_annotation_output.jsonl'
# output_file_path = 'DATA/ANNOTATIONS/p11/s1/p11_s1_chunk_annotations.json'
# extract_and_save_jsonl_content(jsonl_file_path, output_file_path)

def parse_video_annotation(header_directory, participant, session):
    # Define the file paths based on the parameters
    jsonl_file_path = f'{header_directory}/BATCH/ANNOTATION_OUTPUT/{participant}/{session}/{participant}_{session}_batch_annotation_output.jsonl'
    output_file_path = f'{header_directory}/ANNOTATIONS/{participant}/{session}/{participant}_{session}_chunk_annotations.json'
    
    # Ensure the output directory exists
    output_dir = os.path.dirname(output_file_path)
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"Directory {output_dir} created.")
        except OSError as e:
            print(f"Error creating directory {output_dir}: {e}")
            return

    # Call the function to extract and save content
    extract_and_save_jsonl_content(jsonl_file_path, output_file_path)

# Example usage
header_directory = 'DATA'
participant = 'p10'
session = 's1'
parse_video_annotation(header_directory, participant, session)