import json
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import os
from openai import OpenAI
import getpass
from itertools import combinations
import re
import sys
import time

# Load environment variables
load_dotenv()

# Retrieve OpenAI API Key
api_key = os.getenv('OPENAI_API_KEY') or getpass.getpass("Enter or paste your OpenAI API Key: ")

client = OpenAI()

def generate_parent_strategy_batch(info_tuple_list, batch_file_path):
    print("Starting the generation of parent strategies...")
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(batch_file_path), exist_ok=True)

    batch_input_data = []

    for index, (query, parent_strategy, insight) in enumerate(info_tuple_list):
        prompt = f"""
        {insight}

        Based on the extracted insights above from the activity of a specific parent, generate a parenting strategy that this parent would use for the following scene and explain your reasoning behind your strategy:

        {query}

        Follow this format from this example:

        [INPUT] Child: (looks intently at the tablet, scrolling through the storybook options, smiles and occasionally points to different titles)
        
        Parenting Strategy: Utilize the child's evident interest and engagement to introduce a collaborative decision-making process about the storybook. Employ descriptive commentary and open-ended questions to deepen the child's thinking and involvement.

        Child Response: The child considers the question thoughtfully, their eyes lighting up with excitement. The child displays increased enthusiasm, eagerly suggesting that they read the book together immediately. Their engaged and enthusiastic response demonstrates a high level of interest and anticipation.
        
        Parent: (Sitting close to the child, glancing at the tablet screen) "I see you're excited about choosing a book! What do you think this story might be about?" (points to one of the book covers)

        Child: (Thoughtfully) "It looks like it's about a cat. Maybe the cat goes on adventures?"

        Reasoning: This strategy makes use of the child's enthusiasm and focuses on their interests by involving them in the process of selecting a story. Asking open-ended questions encourages the child to think critically and voice their thoughts, which further engages them in the activity. The parent's responsive commentary and inquisitiveness help validate the child's engagement, fostering a supportive learning environment. This approach keeps the reading activity dynamic and interactive, and by collaboratively deciding on the book, the child feels a sense of ownership and excitement about the reading process. The parent's supportive attitude and expressive interaction methodically enhance the child's literacy development and lifelong love for reading.
        """

        batch_input_data.append({
            "custom_id": f"request-{index + 1}",
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

        # print(f"\n\nPROMPT FOR request-{index + 1}\n\n")
        # print(prompt)

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
            "description": "Batch processing for parent strategy generation"
        }
    )

    print("Batch created successfully.")


def load_faiss_index_from_file(train_insight_file_path, faiss_save_path, embeddings):
    if os.path.exists(faiss_save_path):
        # Load FAISS index from file
        new_db = FAISS.load_local(faiss_save_path, embeddings, allow_dangerous_deserialization=True)
    else:
        # If the file doesn't exist, create the FAISS index
        new_db = create_faiss_index_from_json(train_insight_file_path, faiss_save_path)
        # new_db = db
        
    return new_db

def create_faiss_index_from_json(train_insight_file_path, faiss_save_path):
    # Load the JSON data
    with open(train_insight_file_path, 'r') as file:
        data_dict = json.load(file)
    
    # Extract context summaries
    context_summaries = []
    for episode, content in data_dict.items():
        for strategy in content["parent_strategies"]:

            # check if strategy or summary key exists
            if not strategy:
                continue

            summary_of_current_context = strategy.get("summary_of_current_context")
            
            if summary_of_current_context is None:
                print(f"Key 'summary_of_current_context' not found in strategy: {strategy}")
                continue 
            # print(strategy)
            context_summaries.append(strategy['summary_of_current_context'])

    # Create a FAISS index from the context summaries
    embeddings = OpenAIEmbeddings()
    faiss_db = FAISS.from_texts(context_summaries, embeddings)
    
    # Save the FAISS index to file
    faiss_db.save_local(faiss_save_path)

    # Initialize the FAISS index for searching
    faiss_db = FAISS.load_local(faiss_save_path, embeddings, allow_dangerous_deserialization=True)

    return faiss_db

def save_faiss_similarity_scores(train_insight_file_path, query, search_results_with_scores, score_file_path, original_parent_strategy):
    # results = []

    output_data = {"query": query, "results": [], "original_parent_strategy": original_parent_strategy}
    for result, score in search_results_with_scores:
        context_summary = result.page_content
        # details = get_corresponding_details(data_dict, context_summary)
        # results.append(details)
        
        # Print the similarity score for each result
        # print(f"Result: {context_summary}")
        # print(f"Score: {score}")
        
        # Prepare output data for writing to the JSON file
        output_data["results"].append({
            "context": context_summary,
            "insight": get_corresponding_insight(train_insight_file_path, context_summary),
            "similary_score": score
        })
    
    # Ensure the directory for the result file exists
    os.makedirs(os.path.dirname(score_file_path), exist_ok=True)

    # Read existing content from the JSON file if it exists
    if os.path.exists(score_file_path):
        with open(score_file_path, 'r') as score_file:
            existing_data = json.load(score_file)
    else:
        existing_data = []

    # Append new data to existing_data list
    existing_data.append(output_data)
    
    # Write the updated content back to the JSON file
    with open(score_file_path, 'w') as score_file:
        json.dump(existing_data, score_file, indent=4)

    print(f"Similarity scores saved to {score_file_path}.")

def get_corresponding_insight(train_insight_file_path, context_summary):
    # Load the JSON data
    with open(train_insight_file_path, 'r') as file:
        data_dict = json.load(file)
    
    for episode, content in data_dict.items():
        for strategy in content["parent_strategies"]:
            # check if strategy or summary key exists
            if not strategy:
                continue

            summary_of_current_context = strategy.get("summary_of_current_context")
            
            if summary_of_current_context is None:
                print(f"Key 'summary_of_current_context' not found in strategy: {strategy}")
                continue 
            if strategy["summary_of_current_context"] == context_summary:
                if strategy.get("insight") is None:
                    print("NO INSIGHT:\n\n", strategy)
                    continue
                else:
                    return f"{strategy['insight']}"

def get_corresponding_original_parent_strategy(train_insight_file_path, context_summary):
    # Load the JSON data
    with open(train_insight_file_path, 'r') as file:
        data_dict = json.load(file)
    
    for episode, content in data_dict.items():
        for strategy in content["parent_strategies"]:
            # check if strategy or summary key exists
            if not strategy:
                continue

            summary_of_current_context = strategy.get("summary_of_current_context")
            
            if summary_of_current_context is None:
                print(f"Key 'summary_of_current_context' not found in strategy: {strategy}")
                continue 
            if strategy["summary_of_current_context"] == context_summary:
                return f"{strategy['parent_strategy']}"
            

def process_and_search_context_summaries(train_insight_file_path, test_insight_file_path, faiss_save_path, score_file_path, query, k):
    embeddings = OpenAIEmbeddings()
    
    print(f"Processing query: {query}\n")
    # Load or create the FAISS index
    faiss_db = load_faiss_index_from_file(train_insight_file_path, faiss_save_path, embeddings)
    
    # get top k most similar + similarity scores
    search_results_with_scores = faiss_db.similarity_search_with_relevance_scores(query, k)
    
    original_parent_strategy = get_corresponding_original_parent_strategy(test_insight_file_path, query)
    # save similarity scores to document
    save_faiss_similarity_scores(train_insight_file_path, query, search_results_with_scores, score_file_path, original_parent_strategy)

    # get corresponding insights for top k context summaries
    insights = []
    for result, score in search_results_with_scores:
        context_summary = result.page_content
        insight = get_corresponding_insight(train_insight_file_path, context_summary)
        insights.append(insight)
    
    # print(insight)
    print(f"\nRetrieving insight for context summary\n {insights}\n")
    insights_string = '\n'.join(insights)

    print(f"\nRetrieving insight for context summary\n {insights_string}\n")

    return insights_string

    # generate batch parent strategy
def generate_parent_strategy_batch_file(train_insight_file_path, test_insight_file_path, faiss_save_path, score_file_path, batch_file_path, k):
    
    # Load the JSON data
    with open(test_insight_file_path, 'r') as file:
        data_dict = json.load(file)

    # Extract context summaries -- get queries or testing
    context_summaries = []
    original_parent_strategies = []
    for episode, content in data_dict.items():
        for strategy in content["parent_strategies"]:

            # check if strategy or summary key exists
            if not strategy:
                continue

            summary_of_current_context = strategy.get("summary_of_current_context")
            
            if summary_of_current_context is None:
                print(f"Key 'summary_of_current_context' not found in strategy: {strategy}")
                continue 

            # print(strategy)
            context_summaries.append(strategy["summary_of_current_context"])
            original_parent_strategies.append(strategy["parent_strategy"])

    # Create a list of tuples with (query, original parent strategy, insight)
    info_tuple_list = []
    for i, query in enumerate(context_summaries):
        insight_string = process_and_search_context_summaries(train_insight_file_path, test_insight_file_path, faiss_save_path, score_file_path, query, k)
        original_parent_strategy = original_parent_strategies[i]
        info_tuple_list.append((query, original_parent_strategy, insight_string))

    # create the batch file -- comment out if ony need to regenerate retrieval scores folder
    generate_parent_strategy_batch(info_tuple_list, batch_file_path)
    


def generate_batch_parent_strategy(header_directory, participant, train_session, test_session):
    train_insight_file_path = f"{header_directory}/INSIGHTS/{participant}/{train_session}/{participant}_{train_session}_insights.json"
    test_insight_file_path = f"{header_directory}/INSIGHTS/{participant}/{test_session}/{participant}_{test_session}_insights.json"
    batch_file_path = f"{header_directory}/BATCH/PARENT_STRATEGY_INPUT/{participant}/{test_session}/{participant}_{test_session}_batch_parent_strategy_input.jsonl"
    faiss_save_path = f"{header_directory}/FAISS_INDEX/{participant}/{train_session}"
    score_file_path = f"{header_directory}/RETRIEVAL_SCORES/{participant}/{test_session}/{participant}_{test_session}_retrieval_scores.json"

    
    # Pre-generate output file for easier use
    output_file_path = f'{header_directory}/BATCH/PARENT_STRATEGY_OUTPUT/{participant}/{test_session}/_batch_parent_strategy_output.jsonl'
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    generate_parent_strategy_batch_file(train_insight_file_path, test_insight_file_path, faiss_save_path, score_file_path, batch_file_path, k=5)


# Example usage
header_directory = 'DATA'  # Replace with your actual header directory path
participant = 'p10'
train_session = 's2'
test_session = 's1'

generate_batch_parent_strategy(header_directory, participant, train_session, test_session)





# def get_corresponding_details(insight_file_path, context_summary):
#     # Load the JSON data
#     with open(insight_file_path, 'r') as file:
#         data_dict = json.load(file)

#     for episode, content in data_dict.items():
#         for strategy in content["parent_strategies"]:
#             if strategy["context_summary"] == context_summary:
#                 return (
#                     f"Context Summary: {strategy['context_summary']}\n\n"
#                     f"Parent Strategy: {strategy['parent_strategy']}\n\n"
#                     f"PS Analysis: {strategy['ps_analysis']}\n\n"
#                     f"Child Response: {strategy['child_response']}\n\n"
#                     f"CR Analysis: {strategy['cr_analysis']}\n\n"
#                     f"Reflection: {strategy['reflection']}\n\n"
#                     f"Insight: {strategy['insight']}"
#                 )
