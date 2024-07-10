import csv
import json
from dotenv import load_dotenv
import os
from openai import OpenAI
import getpass

# Load environment variables
load_dotenv()

# Retrieve OpenAI API Key
api_key = os.getenv('OPENAI_API_KEY') or getpass.getpass("Enter or paste your OpenAI API Key: ")

# Initialize OpenAI client
client = OpenAI()

# Ensure output directory exists
output_dir = 'chunking_attempts'
os.makedirs(output_dir, exist_ok=True)

# Prepare the batch input file path
batch_input_file_path = os.path.join(output_dir, 'p10_s2_batch_input.jsonl')

def concatenate_transcripts(file_path):
    concatenated_transcripts = ""
    
    with open(file_path, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        line_number = 0
        
        for row in csvreader:
            speaker = row['Speaker']
            transcript = row['Transcript']
            concatenated_transcripts += f"Line [{line_number}]: {speaker}: {transcript}\n"
            line_number += 1
    
    return concatenated_transcripts

def prepare_batch_input(file_paths):
    with open(batch_input_file_path, 'w') as jsonl_file:
        for file_path in file_paths:
            concatenated_transcripts = concatenate_transcripts(file_path)
            prompt = f"""
            You are provided with a transcript of a parent and child reading a storybook together on a tablet. Your task is to divide the transcript into a series of interaction chunks between the parent and the child. Segment the interactions logically, ensuring each chunk represents a meaningful part of their dialogue and actions. Output the first and last line of each chunk, and for each line, only output the first statement ending in punctuation of each line. The start of the next chunk must always the line right after the last line of the last chunk. The maximum number of chunks you may make is 20. Incorporate ALL lines in the transcript.

            Transcript BELOW:

            {concatenated_transcripts}

            Follow this format from this example EXACTLY:

            Interaction Chunk 1:

            (first) Line [0] child: Can we do this one? 
            (last) Line [5] parent: Hands on someone else's head.

            Interaction Chunk 2:

            (first) Line [6]: parent: Don't take off the camera 'cause it's supposed to look at you. 
            (last) Line [8] parent: I don't know. [crosstalk 00:00:29] Maybe all of them.

            Interaction Chunk 3:

            (first) Line [9] child: When can we choose it?
            (last) Line [13] parent: Loading.

            ... (maximum number of chunks is 20)
            """

            jsonl_file.write(json.dumps({
                "custom_id": f"transcript_chunking_batch_p10_s2",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-4o",
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                }
            }) + "\n")

# List of CSV file paths to process
file_paths = [
    'csv_files/p10_s2_output.csv',
    # Add more file paths as needed
]

# Prepare batch input file
prepare_batch_input(file_paths)

# Upload the batch input file
batch_input_file = client.files.create(
  file=open(batch_input_file_path, "rb"),
  purpose="batch"
)

# Create and submit the batch job
test = client.batches.create(
    input_file_id=batch_input_file.id,
    endpoint="/v1/chat/completions",
    completion_window="24h",
    metadata={
        "description": "Chunking transcripts"
    }
)

print(test)

print("Batch job submitted successfully!")
