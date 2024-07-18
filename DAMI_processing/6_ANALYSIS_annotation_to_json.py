from openai import OpenAI
import os
import re
import json
from dotenv import load_dotenv
import getpass
# from googleapiclient import discovery

# Load environment variables
load_dotenv()

# Retrieve OpenAI API Key
api_key = os.getenv('OPENAI_API_KEY') or getpass.getpass("Enter or paste your OpenAI API Key: ")

def analyze_parent_strategy(input_text):
    # print(input_text)
    client = OpenAI()
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
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt
            },
            # {"role": "user", "content": f" Extract an insight from the following scene. Condense your response into two detailed sentences. Pay attention to the parent's parenting and pedagogical approaches:\n\n {input_text}"},
        ]
    )
    print(response.choices[0].message.content)
    print("\n")
    return response.choices[0].message.content
def compile_frame_text(frame_data):
    compiled_text = "\n".join([line for line in frame_data if line.strip()])
    return compiled_text

def parse_text_data(input_file, output_folder):
    frames = {}
    episode_number = 1
    current_scene = []

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with open(input_file, 'r') as file:
        text_data = file.read()

    for line in text_data.split('\n'):
        if line.startswith("Frames "):
            if current_scene:
                compiled_text = compile_frame_text(current_scene)
                parent_strategy = analyze_parent_strategy(compiled_text)
                frames[f"Interaction episode {episode_number}"] = {
                    "scene": current_scene,
                    "parent_strategy": parent_strategy
                }
                current_scene = []
                episode_number += 1
        elif line.strip():
            current_scene.append(line.strip())

    return frames

def clean_text(text):
    # Remove '\n' characters and '**' markers
    cleaned_text = text.replace('\n', '').replace('**', '').strip()
    return cleaned_text

def split_parent_strategy(json_data):
    for episode_key, episode_value in json_data.items():
        parent_strategy = episode_value["parent_strategy"]

        # Split the parent strategy by each section header
        split_sections = parent_strategy.split("Summary of Current Context:")
        # The first section before the first 'Summary of Current Context:' can be discarded.
        split_sections = split_sections[1:]
        # print(split_sections)
        new_parent_strategies = []
        for section in split_sections:
            parts = section.split("Parent Strategy:")
            # context_summary = "Summary of Current Context:\n" + clean_text(parts[0])
            context_summary = clean_text(parts[0])

            if len(parts) > 1:
                remaining_parts = parts[1].split("PS Analysis:")
                # parent_strategy = "Parent Strategy:\n" + clean_text(remaining_parts[0])
                parent_strategy = clean_text(remaining_parts[0])

                if len(remaining_parts) > 1:
                    analysis_sections = remaining_parts[1].split("Child Response:")
                    # ps_analysis = "PS Analysis:\n" + clean_text(analysis_sections[0])
                    ps_analysis = clean_text(analysis_sections[0])

                    if len(analysis_sections) > 1:
                        remaining_parts2 = analysis_sections[1].split("CR Analysis:")
                        # child_response = "Child Response:\n" + clean_text(remaining_parts2[0])
                        child_response = clean_text(remaining_parts2[0])
                        # cr_analysis = "CR Analysis:\n" + clean_text(remaining_parts2[1])
                        cr_analysis = clean_text(remaining_parts2[1])

                        # Split CR Analysis further by Reflection if present
                        reflection_parts = cr_analysis.split("Reflection:")
                        # cr_analysis = "CR Analysis:\n" + clean_text(reflection_parts[0])
                        cr_analysis = clean_text(reflection_parts[0])

                        new_strategy = {
                            "context_summary": context_summary,
                            "parent_strategy": parent_strategy,
                            "ps_analysis": ps_analysis,
                            "child_response": child_response,
                            "cr_analysis": cr_analysis
                        }

                        # Add Reflection if it exists
                        if len(reflection_parts) > 1:
                            # reflection = "Reflection:\n" + clean_text(reflection_parts[1])
                            reflection = clean_text(reflection_parts[1])
                            new_strategy["reflection"] = reflection

                        new_parent_strategies.append(new_strategy)
                    else:
                        print(f"Child Response header not found after PS Analysis in episode '{episode_key}'")
                else:
                    print(f"PS Analysis header not found after Parent Strategy in episode '{episode_key}'")
            else:
                print(f"Parent Strategy header not found after Summary of Current Context in episode '{episode_key}'")

        episode_value["parent_strategies"] = new_parent_strategies

    return json_data

def ensure_directory_exists(file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

def output_to_json_file(file_path, data):
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

def process_and_save_json(input_file_path, output_file_path):
    
    ensure_directory_exists(input_file_path)
    # Read the original JSON file
    with open(input_file_path, 'r') as json_file:
        json_data = json.load(json_file)

    # Process the JSON data
    processed_data = split_parent_strategy(json_data)

    # Ensure the directory for the output file exists
    ensure_directory_exists(output_file_path)

    # Output the processed data to a new JSON file
    output_to_json_file(output_file_path, processed_data)

def main():
    # input_file = 'ANNOTATIONS/p10/s1/p10_s1_chunk_annotations.txt'
    # output_folder = 'ANALYSIS'
    # intermediate_json_path = os.path.join(output_folder, 'intermediate/p10/s1/p10_s1_intermediate_analysisTEST.json')
    # final_json_path = os.path.join(output_folder, 'p10/s1/p10_s1_analysisTEST.json')

    input_file = 'ANNOTATIONS/p11/s1/p11_s1_chunk_annotations.txt'
    output_folder = 'ANALYSIS'
    intermediate_json_path = os.path.join(output_folder, 'intermediate/p11/s1/p11_s1_intermediate_analysis.json')
    final_json_path = os.path.join(output_folder, 'p11/s1/p11_s1_analysis.json')

    frames_data = parse_text_data(input_file, output_folder)

    ensure_directory_exists(intermediate_json_path)

    with open(intermediate_json_path, 'w') as file:
        json.dump(frames_data, file, indent=4)

    process_and_save_json(intermediate_json_path, final_json_path)

if __name__ == "__main__":
    main()