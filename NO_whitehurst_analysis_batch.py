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
client = OpenAI()

def concatenate_transcript(file_path):
    concatenated_transcript = ""
    
    with open(file_path, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        line_number = 0
        
        for row in csvreader:
            speaker = row['Speaker']
            transcript = row['Transcript']
            concatenated_transcript += f"Line [{line_number}]: {speaker}: {transcript}\n"
            line_number += 1
    
    return concatenated_transcript

def prepare_batch_file(transcripts, output_file_path):
    batch_requests = []

    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    
    # Assuming transcripts is a list of transcript strings, one for each request
    for idx, transcript in enumerate(transcripts):
        prompt = f"""
You are provided with a transcript of a parent and child reading a storybook together on a tablet. Your job is to analyze how well the parent follows the dialogic reading standard below on a scale of 1 - 10 (10 being most aligned with the good dialogic reading practices below)

Prompts the child to say something about the book,
Evaluates the child's response,
Expands the child's response by rephrasing and adding information to it, and
Repeats the prompt to make sure the child has learned from the expansion.

Example of PEER: Imagine that the parent and the child are looking at the page of a book that has a picture of a fire engine on it. The parent says, “What is this?” (the prompt) while pointing to the fire truck. The child says, truck, and the parent follows with “That's right (the evaluation); it's a red fire truck (the expansion); can you say fire truck?” (the repetition).

Types of prompts used in dialogic reading to begin PEER sequences -- CROWD acronym:
Completion prompts - You leave a blank at the end of a sentence and get the child to fill it in. Completion prompts provide children with information about the structure of language that is critical to later reading.
Recall prompts - These are questions about what happened in a book a child has already read. Recall prompts help children in understanding story plot and in describing sequences of events.
Open-ended prompts - These prompts focus on the pictures in books. "Tell me what's happening in this picture." Open-ended prompts help children increase their expressive fluency and attend to detail.
Wh- prompts - These prompts usually begin with what, where, when, why, and how questions. Wh- questions teach children new vocabulary.
Distancing prompts - These ask children to relate the pictures or words in the book they are reading to experiences outside the book. Distancing prompts help children form a bridge between books and the real world, as well as helping with verbal fluency, conversational abilities, and narrative skills.

Incorporate the 5 types of CROWD prompts and the 4 PEER improvements with examples when you suggest how the parent can improve in your output (If the parent does not incorporate these already in their interaction with their child)

Transcript BELOW:

{transcript}

Give lines from the transcript for each PEER below:

Follow the formatting of this example EXACTLY -- Include as many quotes, DO NOT INCLUDE ** or ## in your output:

1. Prompting the Child:

Analysis:
The parent prompts the child a few times during the reading, but the prompts are generally basic and not very engaging or challenging. They tend to ask simple identification questions and prompt actions like turning pages.

Quotes:
- Line [0]: "What's that one?"
- Line [22]: "Do you like green eggs and ham?"
- Line [32]: "Who's this?"
- Line [47]: "You can press it."

Score: _/10

2. Evaluating the Child's Response:

Analysis:
The parent occasionally acknowledges the child's responses but doesn't consistently provide clear evaluations. The responses are more acknowledgments rather than evaluations.

Quotes:
- Line [20]: "That guy's name is Sam. Sam-I-am."
- Line [32]: "Who's this? So, silly."

Score: _/10

3. Expanding the Child's Response:

Analysis:
The parent does expand on the child's responses sometimes by adding more information or rephrasing, but it lacks depth and frequent use. When the child identifies Sam, for example, the parent goes on to discuss Sam-I-Am, but this happens infrequently.

Quotes:
- Line [20]: "That guy's name is Sam. Sam-I-am."
- Line [26]: "What a weird name, right?"

Score: _/10

4. Repeating the Prompt:

Analysis:
The parent does not consistently repeat prompts to ensure the child has learned from expansions. There are almost no instances where the parent revisits a point to reinforce the child’s learning.

Quotes:
- There are no clear instances of repetition after expansion.

Score: _/10

Overall Score: _/10

Explanation:
Explain which of the PEER areas that the parent can improve upon and which areas they used well.

How the Parent Can Improve:

Use More Engaging Prompts:
Ask the child more open-ended questions that require critical thinking and imagination.
Example: "Why do you think Sam doesn't like green eggs and ham?"

... (more examples of how the parent can improve based on formatting of example above)
                """
        
        request = {
            "custom_id": f"request-{idx+1}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
            ],
            }
        }
        batch_requests.append(request)
    
    with open(output_file_path, 'w') as f:
        for request in batch_requests:
            f.write(json.dumps(request) + '\n')

    print(f"Batch file created at {output_file_path} with {len(batch_requests)} requests.")

def upload_batch_file(file_path):
    with open(file_path, "rb") as file:
        batch_input_file = client.files.create(
            file=file,
            purpose="batch"
        )
    return batch_input_file.id

def create_batch(file_id):
    batch = client.batches.create(
        input_file_id=file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
            "description": "Whitehurst Dialogic Reading Evaluation Batch"
        }
    )
    print(f"Batch created. Batch ID: {batch.id}")
    return batch.id

def check_batch_status(batch_id):
    status = client.batches.retrieve(batch_id)
    return status

def whitehurst_batch_generation(header_directory, participant, session):
        file_path = f'{header_directory}/CSV_FILES/{participant}/{session}/{participant}_{session}_output.csv'
        output_batch_file = f'{header_directory}/BATCH/WHITEHURST_INPUT/{participant}/{session}/{participant}_{session}_whitehurst_input.json'
        
        # Concatenate transcript
        concatenated_transcript = [concatenate_transcript(file_path)]  # Assuming only one file for now
        
        # Prepare batch file
        prepare_batch_file(concatenated_transcript, output_batch_file)
        
        # Upload batch file
        file_id = upload_batch_file(output_batch_file)
        print(f"Batch file uploaded. File ID: {file_id}")
        
        # Create batch
        batch_id = create_batch(file_id)
        print(f"Batch created. Batch ID: {batch_id}")
        
        # # Check batch status
        # status = check_batch_status(batch_id)
        # print(f"Batch status: {status}")

# Example usage
header_directory = 'DATA'
participant = 'p07'
session = 's2'
whitehurst_batch_generation(header_directory, participant, session)

