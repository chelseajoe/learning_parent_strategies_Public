import json
import os

def calculate_average_similarity_score(results):
    total_score = sum(result['similary_score'] for result in results)
    return total_score / len(results)

def process_parent_strategy(input_file_path, whitehurst_file_path, output_file_path):
    with open(input_file_path, 'r') as f:
        parent_strategy_data = json.load(f)

    with open(whitehurst_file_path, 'r') as f:
        whitehurst_data = json.load(f)

    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    overall_score = whitehurst_data.get("Overall Score", None)

    for item in parent_strategy_data:
        average_score = calculate_average_similarity_score(item['results'])
        item['average_insight_retrieval_score'] = average_score
        item['whitehurst_overall_score'] = overall_score

    with open(output_file_path, 'w') as f:
        json.dump(parent_strategy_data, f, indent=4)

    print(f"Final scores added for: {input_file_path}")

def create_final_score_file(header_directory, participant, session):
    input_file_path = f'{header_directory}/GENERATED_PARENT_STRATEGY/{participant}/{session}/{participant}_{session}_generated_parent_strategy.json'
    whitehurst_file_path = f'{header_directory}/WHITEHURST/{participant}/{session}/{participant}_{session}_whitehurst.json'
    output_file_path = f'{header_directory}/FINAL_SCORES/{participant}/{session}/{participant}_{session}_final_scores.json'
    
    process_parent_strategy(input_file_path, whitehurst_file_path, output_file_path)

# Example usage
header_directory = 'DATA'
participant = 'p10'
session = 's1'
create_final_score_file(header_directory, participant, session)