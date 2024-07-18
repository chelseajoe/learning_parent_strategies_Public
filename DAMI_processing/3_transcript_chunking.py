import csv
from dotenv import load_dotenv
import os
from openai import OpenAI
import getpass
# Load environment variables
load_dotenv()

# Retrieve OpenAI API Key
api_key = os.getenv('OPENAI_API_KEY') or getpass.getpass("Enter or paste your OpenAI API Key: ")

# output_txt_path = 'chunking_attempts/v5_result.txt'

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


def gpt_chunking(concatenated_transcript):
    client = OpenAI()

    # realtime chunking attempt

    prompt = f"""

    You are provided with a transcript of a parent and child reading a storybook together on a tablet. Your task is to divide the transcript into a series of interaction chunks between the parent and the child. Segment the interactions logically, ensuring each chunk represents a meaningful part of their dialogue and actions. Output the first and last line of each chunk, and for each line, only output the first statement ending in punctuation of each line. The start of the next chunk must always the the line right after the last line of the last chunk. The maximum number of chunks you may make is 20. Incorporate ALL lines in the transcript.
    
    Transcript BELOW:

    {concatenated_transcript}

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


    # print(prompt)

    # # Ensure the directory exists
    # os.makedirs(os.path.dirname(output_txt_path), exist_ok=True)

    # # Write the result to a text file
    # with open(output_txt_path, 'w') as file:
    #     file.write(prompt)
        
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
    )


    # print(response.choices[0].message.content)
    # print("\n")
    return response.choices[0].message.content


# Example usage
file_path = 'CSV_FILES/p11/s1/p11_s1_output.csv'
# api_key = 'your-openai-api-key'  # Replace with your actual OpenAI API key
concatenated_transcripts = concatenate_transcripts(file_path)
# prompt = "Please split the transcript based on the given criteria."

result = gpt_chunking(concatenated_transcripts)
print(result)

output_txt_path = 'CHUNK_TXT/p11/s1/p11_s1_chunking.txt'

# Ensure the directory exists
os.makedirs(os.path.dirname(output_txt_path), exist_ok=True)

# Write the result to a text file
with open(output_txt_path, 'a') as file:
    # file.write(prompt)
    file.write("PROMPT END ____________________\n")
    file.write(result)