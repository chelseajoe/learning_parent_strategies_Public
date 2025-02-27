import json
import os
import json
from typing import List, Tuple
from dotenv import load_dotenv
import os
from openai import OpenAI
import getpass

# Load environment variables
load_dotenv()

# Retrieve OpenAI API Key
api_key = os.getenv('OPENAI_API_KEY') or getpass.getpass("Enter or paste your OpenAI API Key: ")

client = OpenAI()

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



# def extract_queries_and_contexts(json_file_path):

#     with open(json_file_path, 'r', encoding='utf-8') as file:
#         data = json.load(file)
        
#     queries_and_contexts = []
    
#     for entry in data:
#         query = entry['query']
#         contexts = [result['context'] for result in entry['results']]
#         queries_and_contexts.append((query, contexts))
    
#     return queries_and_contexts

# # Example usage:
# # json_file_path = 'path/to/your/file.json'
# # queries_and_contexts = extract_queries_and_contexts(json_file_path)
# # print(queries_and_contexts)

# def generate_relevancy_scores_gpt(queries_and_contexts):
#     for query, contexts in queries_and_contexts:
#         relevancy_scores = gpt_relevancy_analysis(query, contexts)


# def gpt_relevancy_analysis(query, contexts):

#     relevancy_scores=[]
#     for context in contexts:
#         prompt = f"""
        

    

#         Given a query, Generate a score from 1-5 on how relevant this retireved context is with 5 being most relevant and 1 being least relevant.

#         Query:
#         {query}

#         Context:
#         {context}

#         Follow the formatting of this example EXACTLY 

#         Relevancy Score:

#         Explantion:
#         """

#         print(f"\n\nPROMPT:\n\n")
#         print(prompt)

        
#         response = client.chat.completions.create(
#             model="gpt-4o",
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant."},
#                 {"role": "user", "content": prompt},
#             ]
#         )

#         output=response.choices[0].message.content
#         relevancy_scores.append(output)


#     # print(response.choices[0].message.content)
#     # print("\n")
#     return relevancy_scores




# def create_final_score_file(header_directory, participant, session):
#     input_file_path = f'{header_directory}/GENERATED_PARENT_STRATEGY/{participant}/{session}/{participant}_{session}_generated_parent_strategy.json'
#     whitehurst_file_path = f'{header_directory}/WHITEHURST/{participant}/{session}/{participant}_{session}_whitehurst.json'
#     output_file_path = f'{header_directory}/FINAL_SCORES/{participant}/{session}/{participant}_{session}_final_scores.json'
    
#     process_parent_strategy(input_file_path, whitehurst_file_path, output_file_path)


#     extract_queries_and_contexts(output_file_path)

# # Example usage
# header_directory = 'DATA'
# participant = 'p10'
# session = 's1'
# create_final_score_file(header_directory, participant, session)






def extract_queries_and_contexts(json_file_path):

    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        
    queries_and_contexts = []
    
    for entry in data:
        query = entry['query']
        contexts = [result['context'] for result in entry['results']]
        queries_and_contexts.append((query, contexts))
    
    return queries_and_contexts

def generate_relevancy_scores_gpt(queries_and_contexts, json_file_path):
    # Load existing JSON data to update
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for entry, (query, contexts) in zip(data, queries_and_contexts):
        # Generate relevancy scores using GPT for the current query and contexts
        relevancy_scores = gpt_relevancy_analysis(query, contexts)
        
        # Update each context with its corresponding relevancy score and explanation
        for i, context in enumerate(entry['results']):
            context['relevancy_score'] = relevancy_scores[i]['relevancy_score']
            context['explanation'] = relevancy_scores[i]['explanation']

    # Write updated data back to the JSON file
    with open(json_file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

def gpt_relevancy_analysis(query, contexts):

    relevancy_scores = []
    
    for context in contexts:
        prompt = f"""
        Given a query, generate a score from 1-5 on how relevant this retrieved context is with 5 being most relevant and 1 being least relevant.

        Query:
        {query}

        Context:
        {context}

        Follow the formatting of this example EXACTLY:

        Relevancy Score:

        Explanation:
        """

        print(f"\n\nPROMPT:\n\n")
        print(prompt)

        # Generate completion using OpenAI GPT
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ]
        )

        output = response.choices[0].message.content.strip()
        print(output)
        relevancy_scores.append(parse_gpt_output(output))

    return relevancy_scores

# def parse_gpt_output(output):
#     """
#     Parse GPT output to extract relevancy score and explanation.
    
#     Args:
#     output (str): The GPT output string.
    
#     Returns:
#     Dict[str, str]: A dictionary with relevancy score and explanation.
#     """
#     # Split the output into lines
#     lines = output.split('\n')

#     # Extract the relevancy score and explanation
#     relevancy_score = ""
#     explanation = ""
    
#     for line in lines:
#         if "Relevancy Score:" in line:
#             relevancy_score = line.split("Relevancy Score:")[-1].strip()
#         elif "Explanation:" in line:
#             explanation = line.split("Explanation:")[-1].strip()

#     return {
#         "relevancy_score": relevancy_score,
#         "explanation": explanation
#     }

def parse_gpt_output(output):
    """
    Parse GPT output to extract relevancy score and explanation.
    
    Args:
    output (str): The GPT output string.
    
    Returns:
    Dict[str, str]: A dictionary with relevancy score and explanation.
    """
    # Initialize variables
    relevancy_score = ""
    explanation = ""
    
    # Trackers to identify which part of the text we are parsing
    reading_explanation = False
    reading_relevancy_score = False

    for line in output.split('\n'):
        # Identify the start of the relevancy score section
        if "Relevancy Score:" in line:
            relevancy_score = line.split("Relevancy Score:")[-1].strip()
            reading_relevancy_score = True
            reading_explanation = False
            continue
        
        # Identify the start of the explanation section
        if "Explanation:" in line:
            explanation = line.split("Explanation:")[-1].strip()
            reading_explanation = True
            reading_relevancy_score = False
            continue

        # Continue collecting lines for explanation or relevancy score
        if reading_explanation:
            explanation += ' ' + line.strip()

        if reading_relevancy_score:
            relevancy_score += ' ' + line.strip()

    print("\n\nRELEVANCY SCORE PARSE\n")
    print(relevancy_score.strip())
    print("\n\nEXPLANATION\n")
    print(explanation.strip())
    return {
        "relevancy_score": relevancy_score.strip(),
        "explanation": explanation.strip()
    }


# def calculate_precision_at_k(json_file_path):
#     """
#     Calculate the precision_at_k_score for each query in the JSON file, update the file,
#     and calculate the average precision_at_k_score across all queries.
    
#     Args:
#     json_file_path (str): Path to the JSON file containing query data.
#     """
#     # Load the JSON file
#     with open(json_file_path, 'r', encoding='utf-8') as file:
#         data = json.load(file)
    
#     total_precision_at_k_score = 0.0  # Initialize total precision_at_k_score
#     total_queries = len(data)         # Total number of queries

#     # Loop through each query and calculate precision_at_k_score
#     for query_entry in data:
#         results = query_entry['results']
#         relevant_count = 0

#         for result in results:
#             # Convert the relevancy score from string to integer
#             relevancy_score = int(result['relevancy_score'].strip())
            
#             # Count relevant contexts (score >= 4)
#             if relevancy_score >= 4:
#                 relevant_count += 1
        
#         # Calculate precision_at_k_score for this query
#         precision_at_k_score = relevant_count / len(results)  # Divide by the number of contexts
        
#         # Update the query entry with the precision_at_k_score
#         query_entry['precision_at_k_score'] = precision_at_k_score
        
#         # Accumulate precision_at_k_score
#         total_precision_at_k_score += precision_at_k_score

#     # Calculate the average precision_at_k_score
#     average_precision_at_k_score = total_precision_at_k_score / total_queries

#     # Write the updated JSON data back to the file
#     with open(json_file_path, 'w', encoding='utf-8') as file:
#         json.dump(data, file, indent=4)
    
#     # Print the average precision_at_k_score
#     print(f"Average Precision@K Score across all queries: {average_precision_at_k_score:.2f}")

def calculate_precision_and_average_insight(json_file_path, precision_file_path):
    """
    Calculate the precision_at_k_score for each query and average_insight_retrieval_score for each context
    in the JSON file, update the file, and calculate the overall average scores.
    
    Args:
    json_file_path (str): Path to the JSON file containing query data.
    """
    # Load the JSON file
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    total_precision_at_k_score = 0.0  # Initialize total precision_at_k_score
    total_average_insight_score = 0.0 # Initialize total average_insight_retrieval_score
    total_queries = len(data)         # Total number of queries
    total_contexts = 0                # Total number of contexts across all queries

    # Loop through each query and calculate precision_at_k_score and average_insight_retrieval_score
    for query_entry in data:
        results = query_entry['results']
        relevant_count = 0
        context_insight_total = 0.0   # Total insight score for the current query's contexts
        
        for result in results:
            # Convert the relevancy score from string to integer
            relevancy_score = int(result['relevancy_score'].strip())
            
            # Convert and accumulate the average_insight_retrieval_score
            insight_score = float(result['similary_score'])
            context_insight_total += insight_score
            
            # Count relevant contexts (score >= 4)
            if relevancy_score >= 4:
                relevant_count += 1
        
        # Calculate precision_at_k_score for this query
        precision_at_k_score = relevant_count / len(results)  # Divide by the number of contexts
        
        # Calculate average_insight_retrieval_score for this query
        average_insight_score = context_insight_total / len(results)  # Average of context scores
        
        # Update the query entry with the precision_at_k_score and average_insight_retrieval_score
        query_entry['precision_at_k_score'] = precision_at_k_score
        query_entry['average_insight_retrieval_score'] = average_insight_score
        
        # Print average_insight_retrieval_score for each query
        print(f"Query: {query_entry['query']}")
        print(f"Average Insight Retrieval Score: {average_insight_score:.4f}\n")
        
        # Accumulate scores for overall calculation
        total_precision_at_k_score += precision_at_k_score
        total_average_insight_score += average_insight_score
        total_contexts += len(results)  # Accumulate total contexts

    # Calculate the overall average precision_at_k_score and average_insight_retrieval_score
    average_precision_at_k_score = total_precision_at_k_score / total_queries
    overall_average_insight_score = total_average_insight_score / total_queries

    # Write the updated JSON data back to the file
    with open(json_file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

    # os.makedirs(os.path.dirname(precision_file_path), exist_ok=True)

    # # Write the updated JSON data back to the file
    # with open(precision_file_path, 'a', encoding='utf-8') as file:
    #     file.write(f"Scores for: {precision_file_path}")
    #     file.write(f"\nOverall Average Precision@K Score across all queries: {average_precision_at_k_score:.2f}")
    #     file.write(f"\nOverall Average Insight Retrieval Score across all contexts: {overall_average_insight_score:.4f}")
    #     file.write(f"\n")
    
    # Print the overall average scores
    print(f"Overall Average Precision@K Score across all queries: {average_precision_at_k_score:.2f}")
    print(f"Overall Average Insight Retrieval Score across all contexts: {overall_average_insight_score:.4f}")



def create_final_score_file(header_directory: str, participant: str, session: str) -> None:
    """
    Create the final score file by processing parent strategy and updating with relevancy scores.
    
    Args:
    header_directory (str): Directory path containing the data.
    participant (str): Participant ID.
    session (str): Session ID.
    """
    input_file_path = f'{header_directory}/GENERATED_PARENT_STRATEGY/{participant}/{session}/{participant}_{session}_generated_parent_strategy.json'
    whitehurst_file_path = f'{header_directory}/WHITEHURST/{participant}/{session}/{participant}_{session}_whitehurst.json'
    output_file_path = f'{header_directory}/FINAL_SCORES/{participant}/{session}/{participant}_{session}_final_scores.json'
    average_scores_file_path = f'{header_directory}/AVERAGE_SCORES/{participant}/{session}/{participant}_{session}_average_scores.json'
    
    # process_parent_strategy(input_file_path, whitehurst_file_path, output_file_path)

    # # Extract queries and contexts from the final scores file
    # queries_and_contexts = extract_queries_and_contexts(output_file_path)

    # # Update the final scores file with relevancy scores
    # generate_relevancy_scores_gpt(queries_and_contexts, output_file_path)

    calculate_precision_and_average_insight(output_file_path, average_scores_file_path)

# Example usage
header_directory = 'DATA'
participant = 'p25'
session = 's1'
create_final_score_file(header_directory, participant, session)