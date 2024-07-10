import json
import os
# import sys

# def split_parent_strategy(json_data):
#     for episode_key, episode_value in json_data.items():
#         parent_strategy = episode_value["parent_strategy"]

#         # Split the parent strategy by each section header
#         split_sections = parent_strategy.split("Summary of Current Context")
#         # print("HELLO")
#         # print(split_sections)
#         # print("_____________\n")
#         # The first section before the first 'Summary of Current Context:' can be discarded.
#         split_sections = split_sections[1:]
#         # print("HELLO\n")
#         # print(split_sections)
#         # print("_____________\n")
#         # print("HELLO\n")
#         # print(split_sections[0])
#         # print("_____________\n")

#         new_parent_strategies = []
#         for section in split_sections:
#             parts = section.split("Parent Strategy:")
#             context_summary = "Summary of Current Context:\n" + parts[0].strip()
#             # print("HELLO\n")
#             # print(parts)
#             # print("_____________\n")
#             if len(parts) > 1:
#                 remaining_parts = parts[1].split("PS Analysis:")
#                 parent_strategy = "Parent Strategy:\n" + remaining_parts[0].strip()

#                 # print("HELLO\n")
#                 # print(remaining_parts)
#                 # print("_____________\n")
                
#                 if len(remaining_parts) > 1:
#                     analysis_sections = remaining_parts[1].split("Child Response:")
#                     ps_analysis = "PS Analysis:\n" + analysis_sections[0].strip()

#                     if len(analysis_sections) > 1:
#                         remaining_parts2 = analysis_sections[1].split("CR Analysis:")
#                         child_response = "Child Response:\n" + remaining_parts2[0].strip()
#                         cr_analysis = "CR Analysis:\n" + remaining_parts2[1].strip()

#                         # print("HELLO\n")
#                         # print(remaining_parts)
#                         # print("_____________\n")
            
#                         # # Check if there is a reflection section
#                         # reflection_parts = cr_analysis.split("Reflection")
#                         # reflection = "Reflection:\n" + reflection_parts[1].strip() if len(reflection_parts) > 1 else ""
                        
#                         # print("HELLO\n")
#                         # print(reflection)
#                         # print("_____________\n")
            
#                         # # Remove ".. (repeat for as many insights as you can identify)" if it exists
#                         # reflection = "Reflection:\n" + reflection.replace("... (repeat for as many insights as you can identify)", "").strip()
#                          # Check if there is a reflection section
#                         reflection_parts = cr_analysis.split("Reflection:")
#                         reflection_text = reflection_parts[1].strip() if len(reflection_parts) > 1 else ""
                        
#                         # Remove ".. (repeat for as many insights as you can identify)" if it exists
#                         reflection = "Reflection:\n" + reflection_text.replace("... (repeat for as many insights as you can identify)", "").strip()
                        
#                         print("HELLO\n")
#                         print(reflection)
#                         print("_____________\n")
            
#                         new_parent_strategies.append({
#                             "context_summary": context_summary,
#                             "parent_strategy": parent_strategy,
#                             "ps_analysis": ps_analysis,
#                             "child_response": child_response,
#                             "cr_analysis": cr_analysis,
#                             "reflection": reflection
#                         })
#                     else:
#                         print(f"Child Response header not found after PS Analysis in episode '{episode_key}'")
#                 else:
#                     print(f"PS Analysis header not found after Parent Strategy in episode '{episode_key}'")
#             else:
#                 print(f"Parent Strategy header not found after Summary of Current Context in episode '{episode_key}'")

#         episode_value["parent_strategies"] = new_parent_strategies

#     return json_data

# def split_parent_strategy(json_data):
#     for episode_key, episode_value in json_data.items():
#         parent_strategy = episode_value["parent_strategy"]

#         # Split the parent strategy by each section header
#         split_sections = parent_strategy.split("Summary of Current Context")
#         # The first section before the first 'Summary of Current Context:' can be discarded.
#         split_sections = split_sections[1:]

#         new_parent_strategies = []
#         for section in split_sections:
#             parts = section.split("Parent Strategy:")
#             context_summary = "Summary of Current Context:\n" + parts[0].strip()

#             if len(parts) > 1:
#                 remaining_parts = parts[1].split("PS Analysis:")
#                 parent_strategy = "Parent Strategy:\n" + remaining_parts[0].strip()

#                 if len(remaining_parts) > 1:
#                     analysis_sections = remaining_parts[1].split("Child Response:")
#                     ps_analysis = "PS Analysis:\n" + analysis_sections[0].strip()

#                     if len(analysis_sections) > 1:
#                         remaining_parts2 = analysis_sections[1].split("CR Analysis:")
#                         child_response = "Child Response:\n" + remaining_parts2[0].strip()
#                         cr_analysis = "CR Analysis:\n" + remaining_parts2[1].strip()

#                         # Remove any reflection section
#                         reflection_parts = cr_analysis.split("Reflection:")
#                         cr_analysis = "CR Analysis:\n" + reflection_parts[0].strip()

#                         new_parent_strategies.append({
#                             "context_summary": context_summary,
#                             "parent_strategy": parent_strategy,
#                             "ps_analysis": ps_analysis,
#                             "child_response": child_response,
#                             "cr_analysis": cr_analysis
#                         })
#                     else:
#                         print(f"Child Response header not found after PS Analysis in episode '{episode_key}'")
#                 else:
#                     print(f"PS Analysis header not found after Parent Strategy in episode '{episode_key}'")
#             else:
#                 print(f"Parent Strategy header not found after Summary of Current Context in episode '{episode_key}'")

#         episode_value["parent_strategies"] = new_parent_strategies

#     return json_data

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


def process_and_save_json(input_file_path, output_file_path):
    def ensure_directory_exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

    def output_to_json_file(file_path, data):
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

    # Read the original JSON file
    with open(input_file_path, 'r') as json_file:
        json_data = json.load(json_file)

    # Process the JSON data
    processed_data = split_parent_strategy(json_data)

    # Ensure the directory for the output file exists
    ensure_directory_exists(output_file_path)

    # Output the processed data to a new JSON file
    output_to_json_file(output_file_path, processed_data)

# Example usage
input_file_path = 'JSON_DATA/reprompt_v1/p17_s2_multi_insights_chunk_toxic.json'
output_file_path = 'JSON_DATA/reprompt_v1/p17_s2_multi_insights_chunk_toxic_separated.json'

process_and_save_json(input_file_path, output_file_path)