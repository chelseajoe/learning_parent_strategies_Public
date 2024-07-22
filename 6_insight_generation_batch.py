# generate insights for each content in the analysis output so we dont have to retrieve from parsed analysis. want the content in string form to be analyzed by gpt.
import json
import os
from openai import OpenAI
from dotenv import load_dotenv
import getpass

# Load environment variables
load_dotenv()

# Retrieve OpenAI API Key
api_key = os.getenv('OPENAI_API_KEY') or getpass.getpass("Enter or paste your OpenAI API Key: ")

client = OpenAI()

def generate_insights(analysis_output_json_path, batch_file_path):
    print("Starting the generation of insights...")

    # Read the input JSON file line by line
    input_data = []
    batch_input_data = []
    # with open(analysis_output_json_path, 'r') as infile:
    #     for line in infile:
    #         input_data.append(json.loads(line))

    with open(analysis_output_json_path, 'r') as file:
        input_data = json.load(file)
    
    print(f"Loaded {len(input_data)} interaction episodes from {analysis_output_json_path}.")

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(batch_file_path), exist_ok=True)

    # Loop through each episode
    for episode_index, episode in enumerate(input_data.values()):
        episode_key = f"Interaction Episode {episode_index + 1}"
        
        print("EPISODE ----\n\n")
        print(episode)
        # Loop through each parent strategy
        for strategy_index, strategy in enumerate(episode['parent_strategies']):
            print("STRATEGY ----\n\n")
            print(strategy)

            if not strategy:
                break
            # Extract the relevant sections from the strategy
            # summary_of_current_context = strategy['summary_of_current_context']
            # parent_strategy = strategy['parent_strategy']
            # ps_analysis = strategy['ps_analysis']
            # child_response = strategy['child_response']
            # cr_analysis = strategy['cr_analysis']
            # reflection = strategy['reflection']

            try:
                # Extract the relevant sections from the strategy
                summary_of_current_context = strategy['summary_of_current_context']
                parent_strategy = strategy['parent_strategy']
                ps_analysis = strategy['ps_analysis']
                child_response = strategy['child_response']
                cr_analysis = strategy['cr_analysis']
                reflection = strategy['reflection']
            except KeyError as e:
                print(f"Missing key: {e}")
                break
            
            # Combine the sections into one analysis output content
            analysis_output_content = f"""
            Summary of Current Context: {summary_of_current_context}

            Parent Strategy: {parent_strategy}

            PS Analysis: {ps_analysis}

            Child Response: {child_response}

            CR Analysis: {cr_analysis}

            Reflection: {reflection}
            """

            # Create the prompt
            prompt = f"""
            Extract an insight from the following trajectory analysis of a parent-child interaction. Analyze the parent's approach and their relative success -- do not suggest ways in which the parent can improve. Pay attention to the parent's parenting and pedagogical approaches. Your response should be 2 sentences long:
            {analysis_output_content}
            """

            batch_input_data.append({
                "custom_id": f"request-{episode_index + 1}-{strategy_index+1}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-4o",
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                }
            })
            print(f"\n\nPROMPT FOR {episode_key}-{strategy_index+1}\n\n")
            print(prompt)
    # Write the batch input data to a .jsonl file
    with open(batch_file_path, 'w') as outfile:
        for item in batch_input_data:
            json.dump(item, outfile)
            outfile.write('\n')
    
    print(f"Batch input file created at {batch_file_path} with {len(batch_input_data)} requests.")

    # Upload the batch input file
    batch_input_file = client.files.create(
        file=open(batch_file_path, "rb"),
        purpose="batch"
    )
    
    print("Batch input file uploaded.")

    # Create the batch
    batch_input_file_id = batch_input_file.id
    client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
            "description": "Batch processing for insight generation"
        }
    )

    print("Batch created successfully.")

def generate_batch_insights(header_directory, participant, session):
    # analysis_output_json_path = f"{header_directory}/BATCH/ANALYSIS_OUTPUT/{participant}/{session}/{participant}_{session}_batch_analysis_output.jsonl"

    analysis_output_json_path = f"{header_directory}/ANALYSIS/{participant}/{session}/{participant}_{session}_analysis.json"
    batch_file_path = f"{header_directory}/BATCH/INSIGHT_INPUT/{participant}/{session}/{participant}_{session}_insight_input.jsonl"

    # Pre - generate output file for easier use
    output_file_path = f'{header_directory}/BATCH/INSIGHT_OUTPUT/{participant}/{session}/output.jsonl'
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    generate_insights(analysis_output_json_path, batch_file_path)

# Example usage
header_directory = 'DATA'  # Replace with your actual header directory path
participant = 'p10'
session = 's1'
 #16 s2, 12 s1
generate_batch_insights(header_directory, participant, session)