# import os
# import json

# def add_insights_to_analysis(analysis_file_path, insight_batch_output_file, output_file_path):
#     # Check if the output file exists; create it if not
#     if not os.path.exists(output_file_path):
#         os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

#     with open(output_file_path, 'w') as f:
#         json.dump({}, f, indent=4)  # Initialize with an empty dictionary
    
#     # Read the insight batch output file
#     with open(insight_batch_output_file, 'r') as f:
#         insights = [json.loads(line) for line in f]

#     # Read the existing analysis file
#     with open(analysis_file_path, 'r') as f:
#         analysis_data = json.load(f)
    
#     # Process each insight and add it to the corresponding episode in the analysis data
#     for insight in insights:
#         # request_id = insight['id']
#         content = insight['response']['body']['choices'][0]['message']['content']
        
#         # print(content)
#         # print(request_id)
#         # Find the corresponding episode
#         for episode_key in analysis_data.keys():
#             # print(episode_key)
#             # if 'id' in analysis_data[episode_key]:
#             # if analysis_data[episode_key]['id'] == request_id:
#                 # Add the insight to the corresponding episode
#             analysis_data[episode_key]['insight'] = content
#             continue
    
#     # Write the updated analysis data to the output file
#     with open(output_file_path, 'w') as f:
#         json.dump(analysis_data, f, indent=4)

#     print(f"Updated analysis data written to {output_file_path}")

# def parse_insight_batch(header_directory, participant, session):
#     # Define file paths using f-strings
#     analysis_file_path = f'{header_directory}/ANALYSIS/{participant}/{session}/{participant}_{session}_analysis.json'
#     insight_batch_output_file = f'{header_directory}/BATCH/INSIGHT_OUTPUT/{participant}/{session}/{participant}_{session}_batch_insight_output.jsonl'
#     output_file_path = f'{header_directory}/INSIGHT/{participant}/{session}/{participant}_{session}_insight.json'

#     # # Print the file paths to verify
#     # print(f"Analysis File Path: {analysis_file_path}")
#     # print(f"Insight Batch Output File Path: {insight_batch_output_file}")
#     # print(f"Output File Path: {output_file_path}")

#     # Call your function here with the generated paths
#     add_insights_to_analysis(analysis_file_path, insight_batch_output_file, output_file_path)

# # Example usage
# header_directory = 'DATA'
# participant = 'p25'
# session = 's1'
# parse_insight_batch(header_directory, participant, session)


# import os
# import json

# def add_insights_to_analysis(analysis_file_path, insight_batch_output_file, output_file_path):
#     # Check if the output file exists; create it if not
#     if not os.path.exists(output_file_path):
#         os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

#     with open(output_file_path, 'w') as f:
#         json.dump({}, f, indent=4)  # Initialize with an empty dictionary
    
#     # Read the insight batch output file
#     with open(insight_batch_output_file, 'r') as f:
#         insights = [json.loads(line) for line in f]

#     # Read the existing analysis file
#     with open(analysis_file_path, 'r') as f:
#         analysis_data = json.load(f)
    
#     # Process each insight and add it to the corresponding episode in the analysis data
#     for insight in insights:
#         custom_id = insight.get('custom_id', '')
#         if not custom_id:
#             continue
        
#         # Parse the custom_id to get the episode number and strategy number
#         parts = custom_id.split('-')
#         if len(parts) != 3 or not parts[0].startswith('request'):
#             continue
#         episode_number = f"Interaction Episode {parts[1]}"
#         strategy_number = int(parts[2]) - 1
        
#         content = insight['response']['body']['choices'][0]['message']['content']
        
#         # Add the insight to the corresponding episode and strategy
#         if episode_number in analysis_data and 'parent_strategies' in analysis_data[episode_number]:
#             if strategy_number < len(analysis_data[episode_number]['parent_strategies']):
#                 analysis_data[episode_number]['parent_strategies'][strategy_number]['insight'] = content
    
#     # Write the updated analysis data to the output file
#     with open(output_file_path, 'w') as f:
#         json.dump(analysis_data, f, indent=4)

#     print(f"Updated analysis data written to {output_file_path}")

# def parse_insight_batch(header_directory, participant, session):
#     # Define file paths using f-strings
#     analysis_file_path = f'{header_directory}/ANALYSIS/{participant}/{session}/{participant}_{session}_analysis.json'
#     insight_batch_output_file = f'{header_directory}/BATCH/INSIGHT_OUTPUT/{participant}/{session}/{participant}_{session}_batch_insight_output.jsonl'
#     output_file_path = f'{header_directory}/INSIGHT/{participant}/{session}/{participant}_{session}_insight.json'

#     # # Print the file paths to verify
#     # print(f"Analysis File Path: {analysis_file_path}")
#     # print(f"Insight Batch Output File Path: {insight_batch_output_file}")
#     # print(f"Output File Path: {output_file_path}")

#     # Call your function here with the generated paths
#     add_insights_to_analysis(analysis_file_path, insight_batch_output_file, output_file_path)

# # Example usage
# header_directory = 'DATA'
# participant = 'p06'
# session = 's1'
# parse_insight_batch(header_directory, participant, session)

import os
import json

def add_insights_to_analysis(analysis_file_path, insight_batch_output_file, output_file_path):
    # Check if the output file exists; create it if not
    if not os.path.exists(output_file_path):
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    with open(output_file_path, 'w') as f:
        json.dump({}, f, indent=4)  # Initialize with an empty dictionary
    
    # Read the insight batch output file
    with open(insight_batch_output_file, 'r') as f:
        insights = [json.loads(line) for line in f]

    # Read the existing analysis file
    with open(analysis_file_path, 'r') as f:
        analysis_data = json.load(f)
    
    # Process each insight and add it to the corresponding episode in the analysis data
    for insight in insights:
        custom_id = insight.get('custom_id', '')
        if not custom_id:
            continue
        
        # Parse the custom_id to get the episode number and strategy number
        parts = custom_id.split('-')
        if len(parts) != 3 or not parts[0].startswith('request'):
            continue
        episode_number = f"Interaction Episode {parts[1]}"
        strategy_number = int(parts[2]) - 1
        
        content = insight['response']['body']['choices'][0]['message']['content']
        
        # Add the insight to the corresponding episode and strategy
        if episode_number in analysis_data and 'parent_strategies' in analysis_data[episode_number]:
            if strategy_number < len(analysis_data[episode_number]['parent_strategies']):
                analysis_data[episode_number]['parent_strategies'][strategy_number]['insight'] = content
    
    # Write the updated analysis data to the output file
    with open(output_file_path, 'w') as f:
        json.dump(analysis_data, f, indent=4)

    print(f"Updated analysis data written to {output_file_path}")

def parse_insight_batch(header_directory, participant, session):
    # Define file paths using f-strings
    analysis_file_path = f'{header_directory}/ANALYSIS/{participant}/{session}/{participant}_{session}_analysis.json'
    insight_batch_output_file = f'{header_directory}/BATCH/INSIGHT_OUTPUT/{participant}/{session}/{participant}_{session}_batch_insight_output.jsonl'
    output_file_path = f'{header_directory}/INSIGHTS/{participant}/{session}/{participant}_{session}_insights.json'

    # # Print the file paths to verify
    # print(f"Analysis File Path: {analysis_file_path}")
    # print(f"Insight Batch Output File Path: {insight_batch_output_file}")
    # print(f"Output File Path: {output_file_path}")

    # Call your function here with the generated paths
    add_insights_to_analysis(analysis_file_path, insight_batch_output_file, output_file_path)

# Example usage
header_directory = 'DATA'
participant = 'p10'
session = 's1'
parse_insight_batch(header_directory, participant, session)
