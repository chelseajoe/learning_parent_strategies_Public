import json
import os
import shutil

def parse_interaction_episodes(input_json_path, annotation_json_path, output_json_path):
    # Read the input JSON file line by line
    input_data = []
    with open(input_json_path, 'r') as infile:
        for line in infile:
            input_data.append(json.loads(line))
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    
    # Make a copy of the annotation JSON file
    shutil.copy(annotation_json_path, output_json_path)
    
    # Read the copied annotation JSON file
    with open(output_json_path, 'r') as outfile:
        annotation_data = json.load(outfile)
    
    # Iterate through each interaction episode in the input JSON file
    for episode_index, episode in enumerate(input_data):
        episode_key = f"Interaction Episode {episode_index + 1}"
        # Ensure episode["scene"] is a list of strings
        # scene = episode.get("scene", []) if isinstance(episode.get("scene"), list) else []
        print(json.dumps(episode['response']['body']['choices'][0]['message']['content']))
        # print(json.dumps(annotation_data))
        annotation_data[episode_key] = {
            "scene":annotation_data[episode_key]["scene"],
            "parent_strategy": episode['response']['body']['choices'][0]['message']['content'],
            "parent_strategies": []
        }

        # Parse content for each section
        sections = ["Summary of Current Context", "Parent Strategy", "PS Analysis", "Child Response", "CR Analysis", "Reflection"]
        parent_strategies = episode['response']['body']['choices'][0]['message']['content'].split("\n\n---\n\n")
        cleaned_strategies = [strategy.replace("**", "").replace("##", "") for strategy in parent_strategies]


        

        for strategy in cleaned_strategies:
            print("\n\nSTRATEGY ---------\n\n\n")
            print(strategy)
            
            strategy_content = {}
            for section in sections:
                if section in strategy:
                    # section_content = strategy.split(section + ":")[1].split("\n\n")[0].strip()
                    section_content = strategy.split(section)[1].split("\n\n")[0].strip()
                    cleaned_section_content = section_content.replace(":", "").strip()

                    section_key = section.lower().replace(" ", "_")
                    strategy_content[section_key] = cleaned_section_content
            
            annotation_data[episode_key]["parent_strategies"].append(strategy_content)
    
    # Save the updated annotation data to the output JSON file
    with open(output_json_path, 'w') as outfile:
        json.dump(annotation_data, outfile, indent=4)

def parse_analysis_batch(header_directory, participant, session):
    input_json_path = f'{header_directory}/BATCH/ANALYSIS_OUTPUT/{participant}/{session}/{participant}_{session}_batch_analysis_output.jsonl'
    annotation_json_path = f'{header_directory}/ANNOTATIONS/{participant}/{session}/{participant}_{session}_chunk_annotations.json'
    output_json_path = f'{header_directory}/ANALYSIS/{participant}/{session}/{participant}_{session}_analysis.json'
    
    parse_interaction_episodes(input_json_path, annotation_json_path, output_json_path)

# Example usage
header_directory = 'DATA'
participant = 'p25'
session = 's1'
parse_analysis_batch(header_directory, participant, session)