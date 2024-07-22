import os
import base64
import json
import glob
from openai import OpenAI
from dotenv import load_dotenv
from getpass import getpass

# Load environment variables
load_dotenv()

# Retrieve OpenAI API Key
api_key = os.getenv('OPENAI_API_KEY') or getpass("Enter or paste your OpenAI API Key: ")

# Initialize OpenAI client
client = OpenAI()

# Function to encode the image to base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def find_video_file(header_directory, participant, session):
    search_pattern = f'{header_directory}/DAMI/{participant}/{session}/{participant}_{session}_*vid*.mp4'
    video_files = glob.glob(search_pattern)
    if video_files:
        return video_files[0]  # Return the first match found
    else:
        raise FileNotFoundError(f"No video file found matching pattern {search_pattern}")

def create_jsonl_file(data, folder_path, jsonl_file, base_prompt, frame_rate=30):

    # Create directory if it doesn't exist
    jsonl_dir = os.path.dirname(jsonl_file)
    if not os.path.exists(jsonl_dir):
        os.makedirs(jsonl_dir)

    with open(jsonl_file, 'w') as f:
        for index, chunk in enumerate(data):
            frame_images = []
            frame_numbers = []
            transcripts = []

            for line in chunk['Lines']:
                # Convert Timestamp to seconds
                minutes, seconds = map(int, line['Timestamp'].split(':'))
                total_seconds = minutes * 60 + seconds

                # Calculate frame number
                frame_number = total_seconds * frame_rate + 45
                frame_path = os.path.join(folder_path, f"frame_{frame_number:04d}.png")

                if not os.path.exists(frame_path):
                    frame_number -= 45
                    frame_path = os.path.join(folder_path, f"frame_{frame_number:04d}.png")

                if os.path.exists(frame_path):
                    base64_image = encode_image(frame_path)
                    frame_images.append(base64_image)
                    frame_numbers.append(frame_number)
                    transcripts.append(line['Transcript'])

            cot_prompt = f"""
            Q: Create a transcript of the interaction analyzed from the given images. I have compiled a list of key frames for you and have attached a transcript for each key frame.

            Consider the auditory context of the current scene. The parent and child are reading a storybook together on a tablet. Here is the transcript of what is currently being said:

            {" ".join([f'Frame {frame_number}: "{transcript}"' for frame_number, transcript in zip(frame_numbers, transcripts)])}

            Here is the context of the previous few moments (if there is no context, then this is the start of the interaction):
            {base_prompt}

            A: Let's think step by step about what is happening in the current scene and output your step by step analysis and the parent action and child reaction organized as exactly follows:

            Output your analysis in the form of a transcript and follow this format EXACTLY:

            For example:
            Child: (turned around, not looking at the parent or the book)
            Parent: Jamie, let's look at the book.
            Child: (not looking at the book)
            Parent: Okay, can you place your hands on your knees?
            """

            # Create image payloads
            image_payloads = [{"image": base64_image, "resize": 768} for base64_image in frame_images]


            # Prepare messages including image payloads
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

            # print(f"\n\nPROMPT FOR FRAMES {frame_numbers}\n\n")
            # print(json.dumps(payload))

            request = {
                "custom_id": f"request-{index}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": payload
            }

            f.write(json.dumps(request) + "\n")

def upload_jsonl_file(jsonl_file_path):
    with open(jsonl_file_path, "rb") as file:
        response = client.files.create(
            file=file,
            purpose='batch'
        )
    return response

def create_batch(batch_input_file_id):
    response = client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
            "description": "batch processing job"
        }
    )
    return response

def batch_video_annotation(header_directory, participant, session):
    try:
        video_path = find_video_file(header_directory, participant, session)
        print(f"Video file found: {video_path}")
    except FileNotFoundError as e:
        print(e)
        return

    folder_path = f'{header_directory}/OUTPUT_FRAMES/{participant}/{session}'
    json_file = f'{header_directory}/CHUNK_DATA/{participant}/{session}/{participant}_{session}_chunk_data.json'
    jsonl_file = f'{header_directory}/BATCH/ANNOTATION_INPUT/{participant}/{session}/{participant}_{session}_batch_annotation_input.jsonl'
    output_file = f'{header_directory}/BATCH/ANNOTATION_OUTPUT/{participant}/{session}/output.jsonl'
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    base_prompt = ""

    with open(json_file, 'r') as file:
        data = json.load(file)

    create_jsonl_file(data, folder_path, jsonl_file, base_prompt)

    upload_response = upload_jsonl_file(jsonl_file)
    batch_input_file_id = upload_response.id
    print(f"Uploaded batch input file ID: {batch_input_file_id}")

    batch_response = create_batch(batch_input_file_id)
    print(f"Created batch job ID: {batch_response.id}")

# Example usage
header_directory = 'DATA'
participant = 'p10'
session = 's1'
batch_video_annotation(header_directory, participant, session)