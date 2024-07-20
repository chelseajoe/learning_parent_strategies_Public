from openai import OpenAI
import os
import json
from dotenv import load_dotenv
import getpass

# Load environment variables
load_dotenv()

# Retrieve OpenAI API Key
api_key = os.getenv('OPENAI_API_KEY') or getpass.getpass("Enter or paste your OpenAI API Key: ")

client = OpenAI()

def analyze_parent_strategy_prompt(input_text):

    prompt = f""" 
Extract as many insights as you can identify from the following scene, paying attention to the parent's parenting and pedagogical approaches. In the Reflection, the parent strategy can only be 1 of 4 categories, [Successful], [Largely Successful], [Somewhat Successful], or [Failure]. The Summary of Current Context should describe the overall context and affect of the child (what the parent strategy used is a reaction to). Identify whether the affect of the child in [affect]. The parent and child are reading a storybook on a tablet.


Here is the scene below:
{input_text}

Follow this format from this example EXACTLY:

Summary of Current Context:
The current scene depicts an interaction between a parent and a child centered around a tablet activity that involves mimicking physical gestures. The child shows signs of [disengagemen] with the tablet storybook and is looking around the room.

Parent Strategy:
The parent is providing a series of clear and specific directives ("Hands on the knees," "Hands on someone else's knees," "Hands on someone else's head"), which helps guide the child's actions. The parent models the gestures to demonstrate what is expected and uses a playful tone to make the activity engaging. The parent gives a series of clear and specific directives, such as "Hands on the knees" and "Hands on someone else's head," while also modeling these actions. The child observes the parent's actions, showing moments of compliance, hesitation, and playful defiance. The scene is characterized by a warm and playful atmosphere, with both the parent and child smiling and interacting positively.

PS Analysis:
This approach indicates an understanding of the importance of modeling behavior for children. The parent's corrections are gentle and straightforward, which likely helps the child understand the desired behavior without feeling chastised. The playful tone and physical modeling keep the learning process fun and engaging, which can enhance the child's motivation and willingness to participate. This exemplifies a positive parenting and pedagogical strategy: using clear instructions, modeling, and play to teach and correct behavior.

Child Response:
The child initially mimics some of the parent's gestures but also shows moments of playful defiance, such as keeping their hands on their head when instructed to place them on their knees. The child also expresses curiosity and engagement by asking questions and smiling throughout the interaction. 

CR Analysis:
The child's mixed responses demonstrate an awareness of the instructions and a natural inclination to test boundaries playfully. The child's behaviors, such as looking at the parent and smiling, indicate a positive and engaged interaction. This shows that the child is attentive and finds the activity enjoyable, even when not fully complying with every directive.

Reflection:
Parent Strategy was [Largely Successful]. However, the parent could improve compliance and engagement by praising the child's efforts and providing immediate positive reinforcement when the child follows instructions. Additionally, allowing the child to lead some of the actions or make choices within the activity could foster a sense of autonomy and further encourage participation. Moving forward, the parent should continue using playful and clear directives while being flexible and responsive to the child's actions to maintain a positive and effective learning environment.

----

Summary of Current Context:
The scene depicts a parent and child engaged in selecting and interacting with content on a tablet. The child is [excited], and awaiting to make a decision on which storybook they should read next.

Parent Strategy:
The parent is using descriptive narration and facilitating choice-making to engage the child with the content on the tablet. The parent lists previously read books and introduces new options while also responding to the child's preferences.

PS Analysis:
This approach demonstrates an understanding of the importance of giving children agency and involving them in decision-making processes. By listing previously read stories and providing options, the parent encourages the child to think critically about their choices and preferences. This strategy fosters a sense of autonomy and can boost the child's confidence. Additionally, the parent's use of descriptive language and active listening helps keep the child engaged and ensures a collaborative selection process.

Child Response:
The child is highly engaged, intently watching the tablet, pointing towards the screen, and verbally expressing their desire to pick a story. The child leans closer to the tablet when interested and seems to relax and agree when the parent offers alternative choices.

CR Analysis:
The child's active participation, such as pointing, talking animatedly, and making choices, shows that the parent's strategy effectively captures the child's attention and encourages a sense of involvement. The child’s positive reactions, including smiling and looking content, indicate that the interaction is enjoyable and that the child feels heard and validated.

Reflection:
Parent Strategy was [Successful]. The strategy is successful because it fosters a positive and interactive engagement by involving the child in decision-making processes, which enhances their sense of autonomy and confidence. The parent's descriptive narration and responsive approach maintain the child's interest and make the activity collaborative and enjoyable. 
... (repeat for as many insights as you can identify)

"""

    return prompt

def compile_frame_text(frame_data):
    compiled_text = "\n".join([line for line in frame_data if line.strip()])
    return compiled_text

def create_batch_file(input_file, batch_file_path):
    # Read the JSON file
    with open(input_file, 'r') as file:
        data = json.load(file)

    episode_number = 1
    current_scene = []

    # Create the batch file
    with open(batch_file_path, 'w') as file:
        for episode, details in data.items():
            # Get the scene content
            scene = details.get("scene", [])
            
            # Compile the text from the scene
            compiled_text = compile_frame_text(scene)

            prompt = analyze_parent_strategy_prompt(compiled_text)
            # Create the request
            request = {
                "custom_id": f"request-{episode_number}",
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

            print(f"\n\nPROMPT FOR EPISODE {episode}\n\n")
            print(prompt)

            # Write the request to the batch file
            file.write(json.dumps(request) + "\n")
            episode_number += 1

    print(f"Batch file created at {batch_file_path}.")

    # return lines
    return batch_file_path

def upload_jsonl_file(jsonl_file_path):
    with open(jsonl_file_path, "rb") as file:
        response = client.files.create(
            file=file,
            purpose='batch'
        )
    return response

def create_batch(input_file_id):
    batch = client.batches.create(
        input_file_id=input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"description": "Batch processing for parenting strategy analysis"}
    )
    return batch

def ensure_directory_exists(file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

def batch_analysis_processing(header_directory, participant, session):
    input_file = f'{header_directory}/ANNOTATIONS/{participant}/{session}/{participant}_{session}_chunk_annotations.json'
    # output_folder = f'{header_directory}/ANALYSIS'
    # intermediate_json_path = f'{output_folder}/intermediate/{participant}/{session}/{participant}_{session}_intermediate_analysis.json'
    batch_file_path = f'{header_directory}/BATCH/ANALYSIS_INPUT/{participant}/{session}/{participant}_{session}_batch_analysis_input.jsonl'
    # final_json_path = f'{output_folder}/{participant}/{session}/{participant}_{session}_analysis.json'

    # input_file, output_folder, intermediate_json_path, batch_file_path, final_json_path = generate_file_paths(header_directory, participant, session)
    
    # Pre - generate output file for easier use
    output_file_path = f'{header_directory}/BATCH/ANALYSIS_OUTPUT/{participant}/{session}/output.jsonl'
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    # Ensure the output directory exists
    ensure_directory_exists(batch_file_path)

    # Step 1: Create batch input file
    batch_input_file = create_batch_file(input_file, batch_file_path)

    # Step 2: Upload batch input file and get file ID
    upload_response = upload_jsonl_file(batch_input_file)
    file_id = upload_response.id

    # Step 3: Create the batch
    batch = create_batch(file_id)

    print(f"Batch created successfully. Batch ID: {batch.id}")

if __name__ == "__main__":
    # Example usage
    header_directory = 'DATA'  # Replace with your actual header directory path
    participant = 'p25'
    session = 's1'

    batch_analysis_processing(header_directory, participant, session)