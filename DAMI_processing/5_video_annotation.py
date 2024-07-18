# import os
# import base64
# import requests
# import getpass
# import pandas as pd
# import time
# import asyncio
# import aiohttp
# import json


# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Retrieve OpenAI API Key
# api_key = os.getenv('OPENAI_API_KEY') or getpass.getpass("Enter or paste your OpenAI API Key: ")

# # Function to encode the image to base64
# def encode_image(image_path):
#     with open(image_path, "rb") as image_file:
#         return base64.b64encode(image_file.read()).decode('utf-8')

# # Function to call OpenAI Vision API with a base64 image
# async def call_openai_vision(base64_image, cot_prompt):
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {api_key}"
#     }

#     payload = {
#         "model": "gpt-4o",
#         # "model": "gpt-4-turbo",
#         "messages": [
#             {
#                 "role": "user",
#                 "content": [
#                     {
#                         "type": "text",
#                         "text": cot_prompt
#                     },
#                     {
#                         "type": "image_url",
#                         "image_url": {
#                             "url": f"data:image/jpeg;base64,{base64_image}"
#                         }
#                     }
#                 ]
#             }
#         ],
#         "max_tokens": 1000
#     }

#     async with aiohttp.ClientSession() as session:
#         async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload) as response:
#             response_json = await response.json()
#             if 'choices' in response_json and len(response_json['choices']) > 0:
#                 return response_json['choices'][0]['message']['content']
#             else:
#                 return "Error: No response from OpenAI API"

# # Function to save the output to a text file
# def save_output_to_file(output_file, frame_number, content):
#     with open(output_file, 'a', newline='') as file:
#         file.write(f"{content}\n\n")

# async def process_frames(folder_path, output_file, base_prompt, json_file, frame_rate=30):
#     # Load JSON file to get interaction chunks
#     with open(json_file, 'r') as file:
#         data = json.load(file)

#     # Check if the output directory exists, if not, create it
#     output_dir = os.path.dirname(output_file)
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)

#     # Loop through each interaction chunk
#     previous_outputs = []

#     for chunk in data:
#         for line in chunk['Lines']:
#             # Convert Timestamp to seconds
#             minutes, seconds = map(int, line['Timestamp'].split(':'))
#             total_seconds = minutes * 60 + seconds

#             # Calculate frame number
#             frame_number = total_seconds * frame_rate + 45
#             frame_path = os.path.join(folder_path, f"frame_{frame_number:04d}.png")

#             if not os.path.exists(frame_path):
#                 frame_number -= 45
#                 frame_path = os.path.join(folder_path, f"frame_{frame_number:04d}.png")

#             if os.path.exists(frame_path):
#                 print(f"Processing frame: {frame_path}")
#             else:
#                 print(f"Frame {frame_number} does not exist.")
            
#             print(f"Processing frame {frame_number}...")

#             # Encode the image to base64
#             base64_image = encode_image(frame_path)

#             # Update the CoT prompt with the latest 3 outputs as context
#             context = "\n\n".join(previous_outputs[-3:])

#             cot_prompt = f"""
            
#             Q: Create a transcript of the interaction analyzed from the given scene.

#             Consider the auditory context of the current scene. The parent and child are reading a storybook together on a tablet. Here is the transcript of what is currently being said by the {line['Speaker']}:

#             "{line['Transcript']}"

#             Here is the context of the previous few moments (if there is no context, then this is the start of the interaction):
#             {context}

#             A: Let's think step by step about what is happening in the current scene and output your step by step analysis and the parent action and child reaction organized as exactly follows:

#             Output your analysis in the form of a transcript and follow this format EXACTLY:

#             For example:
#             Child: (turned around, not looking at the parent or the book)
#             Parent: Jamie, let's look at the book.
#             Child: (not looking at the book)
#             Parent: Okay, can you place your hands on your knees?

#             """

#             print(cot_prompt)

#             # Call OpenAI API asynchronously
#             content = (f"Frame {frame_number}:\n\n")
#             content += await call_openai_vision(base64_image, cot_prompt)

#             # Save output to file
#             save_output_to_file(output_file, frame_number, content)

#             # Append the current output to the list of previous outputs
#             previous_outputs.append(content)

# def main():
#     # Usage
#     # output_folder = 'dataset_processing/output_frames'  # Replace with your frames folder path

#     # print(f"Video path: {video_path}")
#     print(f"Current working directory: {os.getcwd()}")

#     # output_folder = 'output_frames/p10/s2'
#     output_folder = 'output_frames/p17/s2'
#     # output_file = 'openai_vision_output1-4.txt'
#     output_file = 'annotations/CHUNKTEST.txt'
#     # csv_file = 'csv_files/p10_s2_output.csv'  # Replace with your CSV file path
#     csv_file = 'CHUNK_DATA/v1_p17_s2.json'
#     # Process the frames and get OpenAI vision analysis
#     base_prompt = ""
#     asyncio.run(process_frames(output_folder, output_file, base_prompt, csv_file))

# if __name__ == "__main__":
#     main()


import os
import base64
import requests
import getpass
import json
import asyncio
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Retrieve OpenAI API Key
api_key = os.getenv('OPENAI_API_KEY') or getpass.getpass("Enter or paste your OpenAI API Key: ")

# Function to encode the image to base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to call OpenAI Vision API with multiple base64 images
async def call_openai_vision(base64_images, cot_prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Create image payloads
    image_payloads = [{"image": base64_image, "resize": 768} for base64_image in base64_images]

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": cot_prompt},
                    *image_payloads
                ]
            }
        ],
    }

    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload) as response:
            response_json = await response.json()
            if 'choices' in response_json and len(response_json['choices']) > 0:
                return response_json['choices'][0]['message']['content']
            else:
                return "Error: No response from OpenAI API"

# Function to save the output to a text file
def save_output_to_file(output_file, frame_number, content):
    with open(output_file, 'a', newline='') as file:
        file.write(f"{content}\n\n")

async def process_frames(folder_path, output_file, base_prompt, json_file, frame_rate=30):
    # Load JSON file to get interaction chunks
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Check if the output directory exists, if not, create it
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    previous_outputs = []

    for chunk in data:
        # chunk = data[-1]
        frame_images = []
        frame_numbers = []
        transcripts = []
        
        for line in chunk['Lines']:
            # Convert Timestamp to seconds
            minutes, seconds = map(int, line['Timestamp'].split(':'))
            total_seconds = minutes * 60 + seconds
            print("TOTAL SECONDS: ", total_seconds)

            # Calculate frame number
            frame_number = total_seconds * frame_rate + 45
            print("FRAME NUMBER: ", frame_number)
            frame_path = os.path.join(folder_path, f"frame_{frame_number:04d}.png")

            if not os.path.exists(frame_path):
                print(f"Frame: {frame_number} before subtraction")
                frame_number -= 45
                print(f"Frame: {frame_number} after subtraction")
                frame_path = os.path.join(folder_path, f"frame_{frame_number:04d}.png")

            if os.path.exists(frame_path):
                print(f"Processing frame: {frame_path}")
            else:
                print(f"Frame {frame_number} does not exist.")

            print(f"Processing frame {frame_number}...")

            # Encode the image to base64
            base64_image = encode_image(frame_path)

            frame_images.append(base64_image)
            frame_numbers.append(frame_number)
            transcripts.append(line['Transcript'])

        # Update the CoT prompt with the latest 3 outputs as context
        context = "\n\n".join(previous_outputs[-3:])

        cot_prompt = f"""
        Q: Create a transcript of the interaction analyzed from the given images. I have compiled a list of key frames for you and have attached a transcript for each key frame.

        Consider the auditory context of the current scene. The parent and child are reading a storybook together on a tablet. Here is the transcript of what is currently being said:

        {" ".join([f'Frame {frame_number}: "{transcript}"' for frame_number, transcript in zip(frame_numbers, transcripts)])}

        Here is the context of the previous few moments (if there is no context, then this is the start of the interaction):
        {context}

        A: Let's think step by step about what is happening in the current scene and output your step by step analysis and the parent action and child reaction organized as exactly follows:

        Output your analysis in the form of a transcript and follow this format EXACTLY:

        For example:
        Child: (turned around, not looking at the parent or the book)
        Parent: Jamie, let's look at the book.
        Child: (not looking at the book)
        Parent: Okay, can you place your hands on your knees?
        """

        print(cot_prompt)

        # Call OpenAI API asynchronously
        content = (f"Frames {', '.join(map(str, frame_numbers))}:\n\n")
        content += await call_openai_vision(frame_images, cot_prompt)

        # Save output to file
        save_output_to_file(output_file, frame_numbers[0], content)

        # Append the current output to the list of previous outputs
        previous_outputs.append(content)

def main():
    print(f"Current working directory: {os.getcwd()}")

    # output_folder = 'OUTPUT_FRAMES/p10/s1'
    # output_file = 'ANNOTATIONS/p10/s1/p10_s1_chunk_annotations.txt'
    # json_file = 'CHUNK_DATA/p10/s1/p10_s1_chunk_data.json'

    output_folder = 'OUTPUT_FRAMES/p11/s1'
    output_file = 'ANNOTATIONS/p11/s1/p11_s1_chunk_annotations.txt'
    json_file = 'CHUNK_DATA/p11/s1/p11_s1_chunk_data.json'

    base_prompt = ""
    asyncio.run(process_frames(output_folder, output_file, base_prompt, json_file))

if __name__ == "__main__":
    main()
