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

# Set the API key for OpenAI
os.environ["OPENAI_API_KEY"] = api_key

def create_faiss_index_from_json(json_file_path, save_path):
    with open(json_file_path, 'r') as file:
        data_dict = json.load(file)
    
    context_summaries, parent_strategies = extract_context_summaries_and_strategies(data_dict)
    
    print(context_summaries)
    print("\n\n\n\n SAVE PATH"
    )
    print(save_path)
    embeddings = OpenAIEmbeddings()
    db = FAISS.from_texts(context_summaries, embeddings)
    
    # Save FAISS index to file
    db.save_local(save_path)
    
    return db, data_dict

def load_faiss_index_from_file(json_file_path, file_path, embeddings):
    if os.path.exists(file_path):
        # Load FAISS index from file
        new_db = FAISS.load_local(file_path, embeddings, allow_dangerous_deserialization=True)
    else:
        # If the file doesn't exist, create the FAISS index
        db, _ = create_faiss_index_from_json(json_file_path, file_path)
        new_db = db
        
    return new_db

# def similarity_search(db, query, k=5):
#     return db.similarity_search(query, k)

def similarity_search(db, query, k=5):
    return db.similarity_search_with_relevance_scores(query, k)

def get_corresponding_details(data_dict, context_summary):
    for episode, content in data_dict.items():
        for strategy in content["parent_strategies"]:
            if strategy["context_summary"] == context_summary:
                return (
                    f"Context Summary: {strategy['context_summary']}\n\n"
                    f"Parent Strategy: {strategy['parent_strategy']}\n\n"
                    f"PS Analysis: {strategy['ps_analysis']}\n\n"
                    f"Child Response: {strategy['child_response']}\n\n"
                    f"CR Analysis: {strategy['cr_analysis']}\n\n"
                    f"Reflection: {strategy['reflection']}"
                )
    return ""

# def get_retrieved_strategies(json_file_path, query, save_path, k=5):
#     db = load_faiss_index_from_file(json_file_path, save_path, OpenAIEmbeddings())
    
#     if not db:
#         print(f"Error: Unable to load or create FAISS index at {save_path}")
#         return []
    
#     with open(json_file_path, 'r') as file:
#         data_dict = json.load(file)
    
#     search_results = similarity_search(db, query, k)
    
#     results = []
#     for result in search_results:
#         context_summary = result.page_content
#         details = get_corresponding_details(data_dict, context_summary)
#         results.append(details)
    
#     return results

# def get_retrieved_strategies(json_file_path, query, save_path, result_file_path, k=5):
#     # Load the FAISS index
#     db = load_faiss_index_from_file(json_file_path, save_path, OpenAIEmbeddings())
    
#     if not db:
#         print(f"Error: Unable to load or create FAISS index at {save_path}")
#         return []
    
#     # Read the JSON data
#     with open(json_file_path, 'r') as file:
#         data_dict = json.load(file)
    
#     # Perform similarity search and get both results and their scores
#     search_results_with_scores = similarity_search(db, query, k)
    
#     results = []
#     output_data = {"query": query, "results": []}
#     for result, score in search_results_with_scores:
#         context_summary = result.page_content
#         details = get_corresponding_details(data_dict, context_summary)
#         results.append(details)
        
#         # Print the similarity score for each result
#         print(f"Result: {context_summary}")
#         print(f"Score: {score}")
        
#         # Prepare output data for writing to the JSON file
#         output_data["results"].append({
#             "context": context_summary,
#             "score": score
#         })
    
#     # Ensure the directory for the result file exists
#     os.makedirs(os.path.dirname(result_file_path), exist_ok=True)
    
#     # Write the results to the output JSON file
#     with open(result_file_path, 'w') as result_file:
#         json.dump(output_data, result_file, indent=4)
    
#     return results

def get_retrieved_trajectories(json_file_path, score_file_path, query, save_path, result_file_path, k=5):
    # Load the FAISS index
    db = load_faiss_index_from_file(json_file_path, save_path, OpenAIEmbeddings())
    
    if not db:
        print(f"Error: Unable to load or create FAISS index at {save_path}")
        return []
    
    # Read the JSON data
    with open(json_file_path, 'r') as file:
        data_dict = json.load(file)
    
    # Perform similarity search and get both results and their scores
    search_results_with_scores = similarity_search(db, query, k)
    
    results = []
    output_data = {"query": query, "results": []}
    for result, score in search_results_with_scores:
        context_summary = result.page_content
        details = get_corresponding_details(data_dict, context_summary)
        results.append(details)
        
        # Print the similarity score for each result
        print(f"Result: {context_summary}")
        print(f"Score: {score}")
        
        # Prepare output data for writing to the JSON file
        output_data["results"].append({
            "context": context_summary,
            "score": score
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
    
    return results

# def parse_commands(command, existing_rules):
#     insights = existing_rules.copy()  # Start with a copy of existing rules

#     lines = command.splitlines()

#     for line in lines:
#         line = line.strip()
#         # Use regex to find the command and ignore any characters before it
#         match = re.match(r".*?(AGREE|REMOVE|EDIT|ADD)\s+(.+)", line)
#         if match:
#             operation = match.group(1)
#             details = match.group(2)
            
#             if operation == "AGREE":
#                 existing_rule_number, existing_rule = details.split(":", 1)
#                 existing_rule_number = existing_rule_number.strip()
#                 existing_rule = existing_rule.strip()
#                 if existing_rule_number in insights:
#                     insights[existing_rule_number][1] += 1
#                 else:
#                     insights[existing_rule_number] = [existing_rule, 2]
            
#             elif operation == "REMOVE":
#                 existing_rule_number, existing_rule = details.split(":", 1)
#                 existing_rule_number = existing_rule_number.strip()
#                 existing_rule = existing_rule.strip()
#                 if existing_rule_number in insights:
#                     insights[existing_rule_number][1] -= 1
#                     if insights[existing_rule_number][1] == 0:
#                         del insights[existing_rule_number]
            
#             elif operation == "EDIT":
#                 existing_rule_number, new_modified_rule = details.split(":", 1)
#                 existing_rule_number = existing_rule_number.strip()
#                 new_modified_rule = new_modified_rule.strip()
#                 if existing_rule_number in insights:
#                     insights[existing_rule_number] = [new_modified_rule, insights[existing_rule_number][1] + 1]
#                 else:
#                     insights[existing_rule_number] = [new_modified_rule, 2]
            
#             elif operation == "ADD":
#                 new_rule_number, new_rule = details.split(":", 1)
#                 new_rule_number = new_rule_number.strip()
#                 new_rule = new_rule.strip()
#                 insights[new_rule_number] = [new_rule, 2]

#     return insights
def process_pairs(json_file_path, score_file_path, query, save_path, existing_rules, k=5):
    # Retrieve strategies based on the query
    retrieved_strategies = get_retrieved_contexts(json_file_path, score_file_path, query, save_path, k)
    
    # Generate all possible pairs of retrieved strategies
    strategy_pairs = combinations(retrieved_strategies, 2)
    
    final_existing_rules = existing_rules.copy()
    results = []

    # Call extract_insights on each pair
    for pair in strategy_pairs:
        history = f"Trajectory 1: {pair[0]}\n_________\nTrajectory 2: {pair[1]}"
        
        concat_rules = concatenate_original_rules(final_existing_rules)
        
        while True:
            try:
                result = extract_insights(history, concat_rules)
                print("GPT OUTPUT:\n", result)
                
                # Parse the result to update the existing rules
                final_existing_rules = reorder_results(final_existing_rules)
                parsed_commands = parse_commands(result, final_existing_rules)
                
                # Update final existing rules with parsed commands
                final_existing_rules = parsed_commands
                
                results.append(result)
                break  # Exit the loop if successful
            
            except Exception as e:
                print(f"Error occurred in parsing or extracting insights: {e}")
                print(f"Problematic output: {result}")
                # Regenerate extract_insights output and retry
                continue  # Continue the loop to retry

    return final_existing_rules, results

def generate_insights(json_file_path, score_file_path, query, save_path, k=5):
    # Retrieve strategies based on the query
    retrieved_trajectories = get_retrieved_trajectories(json_file_path, score_file_path, query, save_path, k)
    
    # # Generate all possible pairs of retrieved strategies
    # strategy_pairs = combinations(retrieved_strategies, 2)
    
    # final_existing_rules = existing_rules.copy()
    # results = []
    
    client = OpenAI()

    insights = []
    

    for trajectory in retrieved_trajectories:
        prompt = f"""

        Extract an insight from the following trajectory analysis of a parent-child interaction. Analyze the parent's approach and their relative success -- do not suggest ways in which the parent can improve. Pay attention to the parent's parenting and pedagogical approaches. Your response should be 2 sentences long:

        {trajectory}
        """

        print("Prompt:")
        print(prompt)

        # Requesting completion from OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ]
        )

        print("\nGPT RESPONSE ---------\n\n")
        print(response.choices[0].message.content)
        insights.append(response.choices[0].message.content)

    # Extracting and returning the generated content
    return insights

# def parse_commands(command, existing_rules):
#     insights = existing_rules.copy()  # Start with a copy of existing rules

#     lines = command.splitlines()

#     for line in lines:
#         line = line.strip()
#         # Use regex to find the command, number, and the text after the colon
#         match = re.match(r"(AGREE|REMOVE|EDIT|ADD)\s+(\d+):\s*(.+)", line)
#         if match:
#             operation = match.group(1)
#             existing_rule_number = match.group(2).strip()
#             rule_text = match.group(3).strip()
            
#             if operation == "AGREE":
#                 if existing_rule_number in insights:
#                     insights[existing_rule_number][1] += 1
#                 else:
#                     insights[existing_rule_number] = [rule_text, 2]
            
#             elif operation == "REMOVE":
#                 if existing_rule_number in insights:
#                     insights[existing_rule_number][1] -= 1
#                     if insights[existing_rule_number][1] == 0:
#                         del insights[existing_rule_number]
            
#             elif operation == "EDIT":
#                 if existing_rule_number in insights:
#                     insights[existing_rule_number] = [rule_text, insights[existing_rule_number][1] + 1]
#                 else:
#                     insights[existing_rule_number] = [rule_text, 2]
            
#             elif operation == "ADD":
#                 insights[existing_rule_number] = [rule_text, 2]
            
#             print(f"THIS is a good line: {line}\n")
#         else:
#             print(f"No valid operation found or malformed line: {line}\n")

#     return insights

def parse_commands(command, existing_rules):
    insights = existing_rules.copy()  # Start with a copy of existing rules

    lines = command.splitlines()

    for line in lines:
        line = line.strip()
        # Use regex to find the command, number, and the text after the colon, allowing for an optional leading number
        match = re.match(r"(\d+\.\s*)?(AGREE|REMOVE|EDIT|ADD)\s+(\d+):\s*(.+)", line)
        if match:
            operation = match.group(2)
            existing_rule_number = match.group(3).strip()
            rule_text = match.group(4).strip()
            
            if operation == "AGREE":
                if existing_rule_number in insights:
                    insights[existing_rule_number][1] += 1
                else:
                    insights[existing_rule_number] = [rule_text, 2]
            
            elif operation == "REMOVE":
                if existing_rule_number in insights:
                    insights[existing_rule_number][1] -= 1
                    if insights[existing_rule_number][1] == 0:
                        del insights[existing_rule_number]
            
            elif operation == "EDIT":
                if existing_rule_number in insights:
                    insights[existing_rule_number] = [rule_text, insights[existing_rule_number][1] + 1]
                else:
                    insights[existing_rule_number] = [rule_text, 2]
            
            elif operation == "ADD":
                insights[existing_rule_number] = [rule_text, 2]

            print(f"THIS is a good line: {line}\n")
        else:
            print(f"No valid operation found or malformed line: {line}\n")

    return insights

def extract_insights(history, existing_rules):
    client = OpenAI()

    instruction = "You are an advanced reasoning agent that can add, edit, or remove rules from your existing rule set, based on forming new critiques of past task trajectories. You will be given two previous task trials."
    CRITIQUE_SUMMARY_SUFFIX = dict(full = """Focus on REMOVE rules first, and stop ADD rule unless the new rule is VERY insightful and different from EXISTING RULES. Below are the operations you do to the above list of EXISTING RULES:
    """, not_full = """Below are the operations you do to the above list of EXISTING RULES:
    """)

    # Check the number of existing rules
    if len(existing_rules) >= 6:
        critique_summary_suffix = CRITIQUE_SUMMARY_SUFFIX['full']
    else:
        critique_summary_suffix = CRITIQUE_SUMMARY_SUFFIX['not_full']


    # Your prompt content goes here, formatted as needed
    rule_formatting = f""" <OPERATION> <RULE NUMBER>: <RULE>

    The available operations are: AGREE (if the existing rule is strongly relevant for the task), REMOVE (if one existing rule is contradictory or similar/duplicated to other existing rules), EDIT (if any existing rule is not general enough or can be enhanced, rewrite and improve it), ADD (add new rules that are very different from existing rules and relevant for other tasks). Each needs to CLOSELY follow their corresponding formatting below (any existing rule not edited, not agreed, nor removed is considered copied):

    AGREE <EXISTING RULE NUMBER>: <EXISTING RULE>
    REMOVE <EXISTING RULE NUMBER>: <EXISTING RULE>
    EDIT <EXISTING RULE NUMBER>: <NEW MODIFIED RULE>
    ADD <NEW RULE NUMBER>: <NEW RULE>

    Do not mention the trials in the rules because all the rules should be GENERALLY APPLICABLE. Each rule should be concise and easy to follow. Any operation can be used MULTIPLE times. Do at most 4 operations and each existing rule can only get a maximum of 1 operation. """


    human_critique_existing_rules_all_success_template = f"""{instruction}
    Here are the trials:
    {history}

    Here are the EXISTING RULES:
    {existing_rules}

    {critique_summary_suffix}

    By examining the successful trials, and the list of existing rules, you can perform the following operations: add, edit, remove, or agree. The aim is to create a set of general, high-level insights based on your parenting experiences. These insights will serve as practical tips for various parent-child interactions in the future. The goal is to encapsulate your personal parenting strategies into general principles that can be applied to a wide range of scenarios, helping to guide new encounters with your child effectively and consistently.
    {rule_formatting}
    
    """

    
    prompt = human_critique_existing_rules_all_success_template
    # print("Prompt:")
    # print(prompt)

    # Requesting completion from OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
    )

    # Extracting and returning the generated content
    return response.choices[0].message.content



def reorder_results(results):
    unique_results = {}
    
    # Iterate over the items in results
    for key, value in results.items():
        # Strip any non-numeric characters from the key
        cleaned_key = ''.join(filter(str.isdigit, key))
        
        # Convert the cleaned key to an integer
        try:
            int_key = int(cleaned_key)
        except ValueError:
            continue  # Skip if conversion fails
        
        # Store the value with the cleaned integer key in unique_results
        unique_results[int_key] = value
    
    # Sort the dictionary items based on the score (second element in the value list) in descending order
    sorted_results = sorted(unique_results.items(), key=lambda item: item[1][1], reverse=True)
    
    # Convert sorted results back into a dictionary
    reordered_results = {str(key): value for key, value in sorted_results}
    
    return reordered_results

def concatenate_original_rules(result_dict):
    # Sort the dictionary items based on the numeric keys in ascending order
    sorted_results = sorted(result_dict.items(), key=lambda item: int(re.search(r'\d+', item[0]).group()) if re.search(r'\d+', item[0]) else float('inf'))
    
    # Concatenate all rules into a formatted string
    concatenated_rules = "\n".join([f"{re.search(r'\d+', rule[0]).group()}. {rule[1][0]}" for rule in sorted_results if re.search(r'\d+', rule[0])])
    
    return concatenated_rules

def concatenate_numbered_rules(result_dict):
    # Sort the dictionary items based on the score (second element in the value list) in descending order
    sorted_results = sorted(result_dict.items(), key=lambda item: item[1][1], reverse=True)
    
    # Concatenate all rules into a formatted string
    concatenated_rules = "\n".join([f"{index + 1}. {rule[1][0]}" for index, rule in enumerate(sorted_results)])
    
    return concatenated_rules


def extract_context_summaries_and_strategies(data_dict):
    context_summaries = []
    parent_strategies = []
    for episode, content in data_dict.items():
        for strategy in content["parent_strategies"]:
            context_summaries.append(strategy["context_summary"])
            parent_strategies.append(strategy["parent_strategy"])
    return context_summaries, parent_strategies

# FOR TESTING
def extract_all_context_summaries_limit(json_file_path, limit):
    with open(json_file_path, 'r') as file:
        data_dict = json.load(file)
    
    context_summaries, parent_strategies = extract_context_summaries_and_strategies(data_dict)
    
    # Limit the number of context summaries and corresponding parent strategies to the specified limit
    limited_context_summaries = context_summaries[:limit]
    limited_parent_strategies = parent_strategies[:limit]
    
    return limited_context_summaries, limited_parent_strategies

def extract_all_context_summaries(json_file_path):
    with open(json_file_path, 'r') as file:
        data_dict = json.load(file)
    
    context_summaries, parent_strategies = extract_context_summaries_and_strategies(data_dict)
    return context_summaries, parent_strategies

def parse_generation(generation_text, query, generation_save_path):
    # Ensure generation_save_path directory exists
    generation_save_dir = os.path.dirname(generation_save_path)
    if not os.path.exists(generation_save_dir):
        os.makedirs(generation_save_dir)

    # Extract sections using regex
    sections = re.split(r'\n(?:\[INPUT\)|Parenting Strategy:|Child Response:|Parent:|Child:|Reasoning:)', generation_text)
    sections = [section.strip() for section in sections if section.strip()]

    if len(sections) < 6:
        return False  # Incomplete sections

    # Prepare data for JSON with query and results
    parsed_generation = {
        "query": query,
        "results": {
            "input": sections[0].strip(),
            "parenting_strategy": sections[1].strip(),
            "child_response": sections[2].strip(),
            "parent": sections[3].strip(),
            "child": sections[4].strip(),
            "reasoning": sections[5].strip()
        }
    }

    # Append to the JSON file if it exists, otherwise create a new file
    if os.path.exists(generation_save_path):
        with open(generation_save_path, 'r') as f:
            existing_data = json.load(f)
    else:
        existing_data = []

    existing_data.append(parsed_generation)

    with open(generation_save_path, 'w') as f:
        json.dump(existing_data, f, indent=4)

    return True

def organize_numbered_insights(insights):
    # Initialize an empty string to store the numbered insights
    numbered_insights = ""
    
    # Loop through the insights, numbering each one and adding it to the string
    for i, insight in enumerate(insights):
        numbered_insights += f"{i + 1}. {insight}\n"
    
    return numbered_insights

def process_all_context_summaries(train_json_file_path, test_json_file_path, faiss_save_path, score_file_path, insight_save_path, command_save_path, generation_save_path, existing_rules, k=5):
    # Extract all context summaries and parent strategies
    # LIMITED
    # context_summaries, parent_strategies = extract_all_context_summaries_limit(test_json_file_path, 8)
    # ALL
    context_summaries, parent_strategies = extract_all_context_summaries(test_json_file_path)
    
    # all_results = []
    # final_existing_rules = existing_rules.copy()
    
    # Ensure insight_save_path directory exists
    insight_save_dir = os.path.dirname(insight_save_path)
    if not os.path.exists(insight_save_dir):
        os.makedirs(insight_save_dir)
    
    # Ensure command_save_path directory exists
    command_save_dir = os.path.dirname(command_save_path)
    if not os.path.exists(command_save_dir):
        os.makedirs(command_save_dir)
    
    insights_results = []

    for i, query in enumerate(context_summaries):
        print(f"Processing query: {query}")

        # insights, results = process_pairs(train_json_file_path, score_file_path, query, faiss_save_path, final_existing_rules, k)
        insights = generate_insights(train_json_file_path, score_file_path, query, faiss_save_path, k)
        # Combine insights into string
        concat_insights = organize_numbered_insights(insights)
        print("\n\nCONCAT INSIGHTS:\n\n")
        print(concat_insights)

      
        while True:
            generation = generate_parent_strategy(concat_insights, query)
            print("\n\nGENERATION:\n\n")
            print(generation)
            try:
                parse_success = parse_generation(generation, query, generation_save_path)
                if parse_success:
                    print(f"Generation example parsed and saved for query: {query}")
                    generated_parent_strategy = re.findall(r"Parenting Strategy: ([^\n]+)", generation, re.DOTALL)[0].strip()
                    break
                else:
                    print(f"Failed to parse generation example for query: {query}. Incomplete sections. Retrying...\n")
            except Exception as e:
                print(f"Error parsing generation example for query: {query}. Error: {str(e)} Retrying...\n")


        print("\n\nPARENT STRATEGY:\n\n")
        print(generated_parent_strategy)

        # Split the concatenated insights into a list
        list_insights = [insight.strip() for insight in re.split(r'\d+\.\s', concat_insights) if insight.strip()]

        insights_results.append({
            "query": query,
            "results": [
                {
                    "insights": list_insights,
                    "original_parent_strategy": parent_strategies[i],
                    "generated_parent_strategy": generated_parent_strategy
                }
            ]
        })

        # # Read existing data if file exists
        # if os.path.exists(insight_save_path):
        #     with open(insight_save_path, 'r') as f:
        #         existing_data = json.load(f)
        # else:
        #     existing_data = []
        # existing_data = []

        # # Append new results to existing data
        # existing_data.extend(insights_results)

        # Save the updated data to the JSON file
        with open(insight_save_path, 'w') as f:
            json.dump(insights_results, f, indent=4)

        # # Store results
        # all_results.extend(results)

        # Append the query, original and generated parent strategies, and results to the command save path
        # with open(command_save_path, 'a') as command_file:
        #     command_file.write(f"Query: {query}\n")
        #     command_file.write(f"Original Parent Strategy: {parent_strategies[i]}\n")
        #     command_file.write(f"Generated Parent Strategy: {generated_parent_strategy}\n")
        #     command_file.write(f"Insights: {insights}\n")
        #     command_file.write("----------------\n\n")

    # # Read existing data if file exists
    # if os.path.exists(insight_save_path):
    #     with open(insight_save_path, 'r') as f:
    #         existing_data = json.load(f)
    # else:
    #     existing_data = []

    # # Append new results to existing data
    # existing_data.extend(insights_results)

    # # Save the updated data to the JSON file
    # with open(insight_save_path, 'w') as f:
    #     json.dump(existing_data, f, indent=4)

    return insights

def generate_parent_strategy(insights, query):
    client = OpenAI()

    prompt = f"""
    {insights}

    Based on the extracted insights above from the activity of a specific parent, generate a parenting strategy that this parent would use for the following scene and explain your reasoning behing your strategy:

    {query}

    Follow this format from this example:

    [INPUT] Child: (looks intently at the tablet, scrolling through the storybook options, smiles and occasionally points to different titles)
    
    Parenting Strategy: Utilize the child's evident interest and engagement to introduce a collaborative decision-making process about the storybook. Employ descriptive commentary and open-ended questions to deepen the child's thinking and involvement.

    Child Response: The child considers the question thoughtfully, their eyes lighting up with excitement. The child displays increased enthusiasm, eagerly suggesting that they read the book together immediately. Their engaged and enthusiastic response demonstrates a high level of interest and anticipation.
    
    Parent: (Sitting close to the child, glancing at the tablet screen) "I see you're excited about choosing a book! What do you think this story might be about?" (points to one of the book covers)

    Child: (Thoughtfully) "It looks like it's about a cat. Maybe the cat goes on adventures?"

    Reasoning: This strategy makes use of the child's enthusiasm and focuses on their interests by involving them in the process of selecting a story. Asking open-ended questions encourages the child to think critically and voice their thoughts, which further engages them in the activity. The parent's responsive commentary and inquisitiveness help validate the child's engagement, fostering a supportive learning environment. This approach keeps the reading activity dynamic and interactive, and by collaboratively deciding on the book, the child feels a sense of ownership and excitement about the reading process. The parent's supportive attitude and expressive interaction methodically enhance the child's literacy development and lifelong love for reading.
    """

    # print(prompt)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
    )
    # print(response.choices[0].message.content)
    # print("\n")
    return response.choices[0].message.content


# train_json_file_path = 'ANALYSIS/p10/s2/p10_s2_analysisTEST.json'
# test_json_file_path = 'ANALYSIS/p10/s1/p10_s1_analysisTEST.json'

train_json_file_path = 'ANALYSIS/p10/s2/p10_s2_analysis.json'
test_json_file_path = 'ANALYSIS/p10/s1/p10_s1_analysis.json'

faiss_save_path = "FAISS_INDEX/p10/s2"
# json_save_path="COMPARISON/p10/s1/p10_s1_test_comparison.json"
score_save_path = "SCORES/p10/s1/p10_s1_test_scoresNEW.json"
insight_save_path = "INSIGHTS/p10/s1/p10_s1_insightsNEW.json"
command_save_path = "COMMANDS/p10/s1/p10_s1_commandsNEW.txt"
generation_save_path = "GENERATION/p10/s1/p10_s1_generationNEW.json"
# query = "The child is excited"

existing_rules = {}

all_actions = process_all_context_summaries(train_json_file_path, test_json_file_path, faiss_save_path, score_save_path, insight_save_path, command_save_path, generation_save_path, existing_rules, k=5)
