import os
import json
import re

def extract_parenting_strategy(content):
    """Extracts the Parenting Strategy section from the provided content."""
    match = re.search(r'Parenting Strategy:\s*(.*?)\s*Child Response:', content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

def create_parent_strategy_file(retrieval_scores_file_path, parent_strategy_batch_output_file, output_file_path):
    # Ensure the output file's directory exists; create it if not
    output_dir = os.path.dirname(output_file_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created directory: {output_dir}")
    
    # Initialize the output file with an empty dictionary if it does not exist
    if not os.path.exists(output_file_path):
        with open(output_file_path, 'w') as f:
            json.dump({}, f, indent=4)
            print(f"Initialized empty output file: {output_file_path}")

    # Read the parent strategy batch output file
    with open(parent_strategy_batch_output_file, 'r') as f:
        parent_strategies = [json.loads(line) for line in f]
        print(f"Loaded {len(parent_strategies)} parent strategies from {parent_strategy_batch_output_file}")

    # Read the existing retrieval scores file
    with open(retrieval_scores_file_path, 'r') as f:
        retrieval_scores_data = json.load(f)
        print(f"Loaded retrieval scores data from {retrieval_scores_file_path}")

    # Ensure we have the same number of parent strategies and retrieval queries
    assert len(parent_strategies) == len(retrieval_scores_data), f"Mismatch between parent strategies and retrieval scores. Retrieval: {len(retrieval_scores_data)}, Parent Strategies: {len(parent_strategies)}"
    print(f"Verified matching count of parent strategies and retrieval queries: {len(parent_strategies)}")

    # Process each parent strategy and add it to the corresponding area in retrieval scores data
    for index, parent_strategy in enumerate(parent_strategies):
        content = parent_strategy['response']['body']['choices'][0]['message']['content']
        extracted_strategy = extract_parenting_strategy(content)
        retrieval_scores_data[index]['full_generated_parent_strategy'] = content
        retrieval_scores_data[index]['generated_parent_strategy'] = extracted_strategy
        print(f"Added extracted parenting strategy to query index {index}")

    # Write the updated retrieval scores data to the output file
    with open(output_file_path, 'w') as f:
        json.dump(retrieval_scores_data, f, indent=4)
        print(f"Saved updated retrieval scores data to {output_file_path}")

# # Example usage
# retrieval_scores_file_path = 'DATA/RETRIEVAL_SCORES/p13/s1/p13_s1_retrieval_scores.json'
# parent_strategy_batch_output_file = 'DATA/BATCH/PARENT_STRATEGY_OUTPUT/p13/s1/p13_s1_batch_parent_strategy_output.jsonl'
# output_file_path = 'DATA/GENERATED_PARENT_STRATEGY/p13/s1/p13_s1_generated_parent_strategy.json'

# create_parent_strategy_file(retrieval_scores_file_path, parent_strategy_batch_output_file, output_file_path)

# def parse_insight_batch(header_directory, participant, session):
#     # Define file paths using f-strings
#     analysis_file_path = f'{header_directory}/ANALYSIS/{participant}/{session}/{participant}_{session}_analysis.json'
#     insight_batch_output_file = f'{header_directory}/BATCH/INSIGHT_OUTPUT/{participant}/{session}/{participant}_{session}_batch_insight_output.jsonl'
#     output_file_path = f'{header_directory}/INSIGHTS/{participant}/{session}/{participant}_{session}_insights.json'

#     # # Print the file paths to verify
#     # print(f"Analysis File Path: {analysis_file_path}")
#     # print(f"Insight Batch Output File Path: {insight_batch_output_file}")
#     # print(f"Output File Path: {output_file_path}")

#     # Call your function here with the generated paths
#     add_insights_to_analysis(analysis_file_path, insight_batch_output_file, output_file_path)

# # Example usage
# header_directory = 'DATA'
# participant = 'p18'
# session = 's1'
# parse_insight_batch(header_directory, participant, session)

def create_parent_strategy_full(header_directory, participant, session):
    # Define file paths using f-strings
    retrieval_scores_file_path = f'{header_directory}/RETRIEVAL_SCORES/{participant}/{session}/{participant}_{session}_retrieval_scores.json'
    parent_strategy_batch_output_file = f'{header_directory}/BATCH/PARENT_STRATEGY_OUTPUT/{participant}/{session}/{participant}_{session}_batch_parent_strategy_output.jsonl'
    output_file_path = f'{header_directory}/GENERATED_PARENT_STRATEGY/{participant}/{session}/{participant}_{session}_generated_parent_strategy.json'

    # Print the file paths to verify
    print(f"Retrieval Scores File Path: {retrieval_scores_file_path}")
    print(f"Parent Strategy Batch Output File Path: {parent_strategy_batch_output_file}")
    print(f"Output File Path: {output_file_path}")

    # Call your function here with the generated paths
    create_parent_strategy_file(retrieval_scores_file_path, parent_strategy_batch_output_file, output_file_path)

# Example usage
header_directory = 'DATA'
participant = 'p13'
session = 's1'
create_parent_strategy_full(header_directory, participant, session)