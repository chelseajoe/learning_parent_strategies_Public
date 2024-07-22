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

    prompt = f"""

    You are provided with a transcript of a parent and child reading a storybook together on a tablet. Your job ist to analyze how well the parent follows the dialogic reading standard below on a scale of 1 - 10 (10 being most aligned with the good dialogic reading practices below)

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
    Distancing prompts - These ask children to relate the pictures or words in the book they are reading to experiences outside the book. istancing prompts help children form a bridge between books and the real world, as well as helping with verbal fluency, conversational abilities, and narrative skills.
    
    Incorporate the 5 types of CROWD prompts and the 4 PEER improvements with examples when you suggest how the parent can improve in your output (If the parent does not incorporate these already in their interaction with their child)

    Transcript BELOW:

    {concatenated_transcript}

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
    - Ask the child more open-ended questions that require critical thinking and imagination.
    - Example: "Why do you think Sam doesn't like green eggs and ham?"

    ... (more examples of how the parent can improve based on formatting of example above)

    """


    # print(prompt)

    # # Ensure the directory exists
    # os.makedirs(os.path.dirname(output_txt_path), exist_ok=True)

    # # Write the result to a text file
    # with open(output_txt_path, 'w') as file:
    #     file.write(prompt)
    
    print(f"\n\nPROMPT:\n\n")
    print(prompt)

    
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


def whitehurst_analysis_generation(header_directory, participant, session):
    # Generate file paths
    file_path = f'{header_directory}/CSV_FILES/{participant}/{session}/{participant}_{session}_output.csv'
    output_txt_path = f'{header_directory}/GENERATED_WHITEHURST/{participant}/{session}/{participant}_{session}_whitehurst.txt'
    # Process transcript and save result
    concatenated_transcripts = concatenate_transcripts(file_path)
    result = gpt_chunking(concatenated_transcripts)
    print(result)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_txt_path), exist_ok=True)
    
    # Write the result to a text file
    with open(output_txt_path, 'a') as file:
        # file.write("PROMPT END ____________________\n")
        file.write(result)

    print(f"Whitehurst analysis generated for: {output_txt_path}")
# Example usage
header_directory = 'DATA'
participant = 'p10'
session = 's1'
whitehurst_analysis_generation(header_directory, participant, session)