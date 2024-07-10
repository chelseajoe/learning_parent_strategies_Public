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

# Load environment variables
load_dotenv()

# Retrieve OpenAI API Key
api_key = os.getenv('OPENAI_API_KEY') or getpass.getpass("Enter or paste your OpenAI API Key: ")

# Set the API key for OpenAI
os.environ["OPENAI_API_KEY"] = api_key

def create_faiss_index_from_json(json_file_path, save_path):
    with open(json_file_path, 'r') as file:
        data_dict = json.load(file)
    
    context_summaries = extract_context_summaries_and_strategies(data_dict)
    
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

def similarity_search(db, query, k=5):
    return db.similarity_search(query, k)

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

def get_retrieved_strategies(json_file_path, query, save_path, k=5):
    db = load_faiss_index_from_file(json_file_path, save_path, OpenAIEmbeddings())
    
    if not db:
        print(f"Error: Unable to load or create FAISS index at {save_path}")
        return []
    
    with open(json_file_path, 'r') as file:
        data_dict = json.load(file)
    
    search_results = similarity_search(db, query, k)
    
    results = []
    for result in search_results:
        context_summary = result.page_content
        details = get_corresponding_details(data_dict, context_summary)
        results.append(details)
    
    return results

def parse_commands(command, existing_rules):
    insights = existing_rules.copy()  # Start with a copy of existing rules

    lines = command.splitlines()

    for line in lines:
        line = line.strip()
        # Use regex to find the command and ignore any characters before it
        match = re.match(r".*?(AGREE|REMOVE|EDIT|ADD)\s+(.+)", line)
        if match:
            operation = match.group(1)
            details = match.group(2)
            
            if operation == "AGREE":
                existing_rule_number, existing_rule = details.split(":", 1)
                existing_rule_number = existing_rule_number.strip()
                existing_rule = existing_rule.strip()
                if existing_rule_number in insights:
                    insights[existing_rule_number][1] += 1
                else:
                    insights[existing_rule_number] = [existing_rule, 2]
            
            elif operation == "REMOVE":
                existing_rule_number, existing_rule = details.split(":", 1)
                existing_rule_number = existing_rule_number.strip()
                existing_rule = existing_rule.strip()
                if existing_rule_number in insights:
                    insights[existing_rule_number][1] -= 1
                    if insights[existing_rule_number][1] == 0:
                        del insights[existing_rule_number]
            
            elif operation == "EDIT":
                existing_rule_number, new_modified_rule = details.split(":", 1)
                existing_rule_number = existing_rule_number.strip()
                new_modified_rule = new_modified_rule.strip()
                if existing_rule_number in insights:
                    insights[existing_rule_number] = [new_modified_rule, insights[existing_rule_number][1] + 1]
                else:
                    insights[existing_rule_number] = [new_modified_rule, 2]
            
            elif operation == "ADD":
                new_rule_number, new_rule = details.split(":", 1)
                new_rule_number = new_rule_number.strip()
                new_rule = new_rule.strip()
                insights[new_rule_number] = [new_rule, 2]

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


def process_pairs(json_file_path, query, save_path, existing_rules, k=5):
    # Retrieve strategies based on the query
    retrieved_strategies = get_retrieved_strategies(json_file_path, query, save_path, k)
    
    # Generate all possible pairs of retrieved strategies
    strategy_pairs = combinations(retrieved_strategies, 2)
    
    final_existing_rules = existing_rules.copy()
    results = []

    # Call extract_insights on each pair
    for pair in strategy_pairs:
        history = f"Trajectory 1: {pair[0]}\n_________\nTrajectory 2: {pair[1]}"
        
        concat_rules = concatenate_original_rules(final_existing_rules)
        
        try:
            result = extract_insights(history, concat_rules)
            print("GPT OUTPUT:\n", result)
            
            # Parse the result to update the existing rules
            final_existing_rules = reorder_results(final_existing_rules)
            parsed_commands = parse_commands(result, final_existing_rules)
            
            # Update final existing rules with parsed commands
            final_existing_rules = parsed_commands
            
            results.append(result)
        
        except Exception as e:
            print(f"Error occurred in parsing or extracting insights: {e}")
            # Handle the error case here, such as regenerating extract_insights or logging
            
            # Example: Regenerate extract_insights
            result = extract_insights(history, concat_rules)
            # print("Regenerated GPT OUTPUT:\n", result)
            
            # Continue with parsing and updating rules
            final_existing_rules = reorder_results(final_existing_rules)
            parsed_commands = parse_commands(result, final_existing_rules)
            final_existing_rules = parsed_commands
            
            results.append(result)

    return final_existing_rules, results

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

# def extract_context_summaries(data_dict):
#     context_summaries = []
#     for episode, content in data_dict.items():
#         for strategy in content["parent_strategies"]:
#             context_summaries.append(strategy["context_summary"])
#     return context_summaries

# # FOR TESTING
# def extract_all_context_summaries_limit(json_file_path, limit=2):
#     with open(json_file_path, 'r') as file:
#         data_dict = json.load(file)
    
#     context_summaries = extract_context_summaries(data_dict)
    
#     # Limit the number of context summaries to the specified limit
#     limited_context_summaries = context_summaries[:limit]
    
#     return limited_context_summaries

# def extract_all_context_summaries(json_file_path):
#     with open(json_file_path, 'r') as file:
#         data_dict = json.load(file)
    
#     context_summaries = extract_context_summaries(data_dict)
#     return context_summaries

# def process_all_context_summaries(train_json_file_path, test_json_file_path, save_path, existing_rules, k=5):
#     # Extract all context summaries
#     # context_summaries = extract_all_context_summaries(test_json_file_path)
#     context_summaries = extract_all_context_summaries_limit(test_json_file_path)
    
#     all_results = []
#     final_existing_rules = existing_rules.copy()

#     # Process each context summary
#     for query in context_summaries:
#         print(f"Processing query: {query}")
#         insights, results = process_pairs(train_json_file_path, query, save_path, final_existing_rules, k)

#         # combine insights into string
#         concat_insights = concatenate_numbered_rules(insights)
#         print("\n\n CONCAT INSIGHTS:\n\n")
#         print(concat_insights)

#         parent_strategy = generate_parent_strategy(concat_insights, query)
#         print("\n\nPARENT STRATEGY: \n\n")
#         print(parent_strategy)
#         all_results.extend(results)
    
#     return insights, all_results


def extract_context_summaries_and_strategies(data_dict):
    context_summaries = []
    parent_strategies = []
    for episode, content in data_dict.items():
        for strategy in content["parent_strategies"]:
            context_summaries.append(strategy["context_summary"])
            parent_strategies.append(strategy["parent_strategy"])
    return context_summaries, parent_strategies

# FOR TESTING
def extract_all_context_summaries_limit(json_file_path, limit=8):
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

def process_all_context_summaries(train_json_file_path, test_json_file_path, faiss_save_path, json_save_path, existing_rules, k=5):
    # Extract all context summaries and parent strategies
    # context_summaries, parent_strategies = extract_all_context_summaries(test_json_file_path)
    context_summaries, parent_strategies = extract_all_context_summaries_limit(test_json_file_path)
    
    all_results = []
    final_existing_rules = existing_rules.copy()
    # with open('output.txt', 'w') as f:
        # sys.stdout = f
    # Process each context summary
    for i, query in enumerate(context_summaries):
        

        print(f"Processing query: {query}")
        insights, results = process_pairs(train_json_file_path, query, faiss_save_path, final_existing_rules, k)

        # Combine insights into string
        concat_insights = concatenate_numbered_rules(insights)
        print("\n\nCONCAT INSIGHTS:\n\n")
        print(concat_insights)

        generation = generate_parent_strategy(concat_insights, query)
        generated_parent_strategy = re.findall(r"Parenting Strategy: ([^\n]+)", generation, re.DOTALL)[0].strip()

        print("\n\nWHOLE GENERATION:\n\n")
        print(generated_parent_strategy)

        print("\n\nPARENT STRATEGY:\n\n")
        print(generated_parent_strategy)

        # Compare with the original parent strategy
        original_parent_strategy = parent_strategies[i]
        comparison = gpt_compare_parent_strategy(query, generated_parent_strategy, original_parent_strategy)
        
        print("\n\nORIGINAL PARENT STRATEGY:\n\n")
        print(original_parent_strategy)

        print("\n\nCOMPARISON GPT OUTPUT:\n\n")
        print(comparison)

        save_comparison_results_to_json(query, generated_parent_strategy, original_parent_strategy, comparison, json_save_path)

        # Store results
        all_results.extend(results)
    
    # sys.stdout = sys.__stdout__

    return insights, all_results

def generate_parent_strategy(insights, query):
    client = OpenAI()

    # prompt = f"""
    # {insights}

    # Based on the extracted insights above from the activity of a specific parent, generate a parenting strategy that this parent would use for the following scene and explain your reasoning behing your strategy:

    # {query}

    # Follow this format from this example:

    # Child: (looks away from the book and parent, standing up)

    # Parenting Strategy: Use the child's interest as a bridge to bring them back to the book-reading activity. Encourage an active break to expend some energy, promoting physical activity as well and then efficiently transition into further reading.

    # Parent: (Noticing that the child is getting restless, smiles understandingly) "Let's play a quick game! Can you jump like a kangaroo for a minute? Then we can hop back to our story."

    # Child: (Excitedly jumps around like a kangaroo)

    # Reasoning: In developing this strategy, the aim is to respect the child's current need for movement while also encouraging their re-engagement with the book. By making the transition activity fun and related to the child's interests it sustains their attention and eagerness to return to reading. This approach also fosters positive associations with reading and learning, as the child sees it as part of a sequence of enjoyable activities. This strategy thus combines physical activity with cognitive development, showing the child that learning can be an engaging and dynamic process.
    # """

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


def gpt_compare_parent_strategy(context_summary, generated_parent_strategy, original_parent_strategy):
    client = OpenAI()

    # prompt = f"""

    # A parent strategy has been generated for a parent-child interaction given this context:
    # {context_summary}

    # Compare how similar the [GENERATED PARENTING STRATEGY]:

    # {generated_parent_strategy}

    # is to the [ACTUAL PARENTING STRATEGY]:

    # {original_parent_strategy}

    # On a scale from 1 - 5 with 1 being the lowest similarity and 5 being the highest similarity score, rate how similar the parenting strategies are, and explain your reasoning.

    # On a scale from 1 - 5 with 1 being the lowest effectiveness and 5 being the highest effectiveness score, rate how effective the [GENERATED PARENTING STRATEGY] and the [ACTUAL PARENTING STRATEGY] is.

    # Also, output whch strategy you think is more effective, the GENERATED PARENTING STRATEGY or ACTUAL PARENTING STRATEGY

    
    # Follow this format from this example EXACTLY:

    # SIMILARITY RATING: I would rate the similarity between the parenting strategies as a [3].

    # SIMILARITY REASONING: While both strategies involve engaging the child by asking questions and making choices about the storybook, the approaches differ in their specific techniques. The [GENERATED PARENTING STRATEGY] focuses heavily on imaginative storytelling and the use of vivid descriptions to stimulate critical thinking and creativity. In contrast, the [ACTUAL PARENTING STRATEGY] emphasizes providing choices and verbalizing the child's selection, along with physical contact for reassurance and involvement. Both strategies aim to engage the child and maintain their excitement, but the methods used reflect different facets of engagement and interaction.

    # GENERATED RATING: I would rate the effectiveness of the [GENERATED PARENTING STRATEGY] a [5].

    # GENERATED REASONING: The [GENERATED PARENTING STRATEGY] effectively utilizes the child's excitement and promotes deeper engagement through imagination and open-ended questions, which can significantly enhance comprehension skills and a love for storytelling. It validates the child's ideas, fosters a collaborative atmosphere, and primes the child's imagination, making the reading activity more interactive and enjoyable.

    # ACTUAL RATING: I would rate the effectiveness of the [ACTUAL PARENTING STRATEGY] a [4].

    # ACTUAL REASONING: The [ACTUAL PARENTING STRATEGY] is also effective as it engages the child by providing choices about the storybook, ensuring the child remains involved, and using physical touch to show support and involvement. This approach maintains the child's excitement and provides a sense of security and validation of their choices. However, it may not stimulate the child's critical thinking and creativity to the same extent as the generated strategy.
    
    # BEST STRATEGY: The [GENERATED PARENT STRATEGY] is more effective.

    # BEST REASONING: The generated strategy offers a more comprehensive approach to nurturing the child's imagination and critical thinking skills, making the reading activity more engaging and educational. By fostering a collaborative storytelling process and encouraging the child's creativity, this strategy not only makes the activity enjoyable but also promotes essential cognitive skills and a lifelong positive attitude towards reading.

    # """

    prompt = f"""

    A parent strategy has been generated for a parent-child interaction given this context:
    {context_summary}

    Compare how similar the [GENERATED PARENTING STRATEGY]:

    {generated_parent_strategy}

    is to the [ACTUAL PARENTING STRATEGY]:

    {original_parent_strategy}

    On a scale from 1 - 5 with 1 being the lowest similarity and 5 being the highest similarity score, rate how similar the parenting strategies are, and explain your reasoning.

    On a scale from 1 - 5 with 1 being the lowest effectiveness and 5 being the highest effectiveness score, rate how effective the [GENERATED PARENTING STRATEGY] and the [ACTUAL PARENTING STRATEGY] is.

    Also, output whch strategy you think is more effective, the GENERATED PARENTING STRATEGY or ACTUAL PARENTING STRATEGY

    
    Follow this format from this example EXACTLY:

    SIMILARITY RATING: <RATING HERE>

    SIMILARITY REASONING: <REASONING HERE>

    GENERATED RATING: <RATING HERE>

    GENERATED REASONING: <REASONING HERE>

    ACTUAL RATING: <RATING HERE>

    ACTUAL REASONING: <REASONING HERE>
    
    BEST STRATEGY: <STRATEGY HERE>

    BEST REASONING: <REASONING HERE>

    """
    print("\n\nPROMPT FOR PARENT COMPARISON\n:")
    print(prompt)
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
def parse_gpt_output(gpt_output):

    result = {}

    similarity_rating_match = re.search(r"SIMILARITY RATING: (\d)", gpt_output)
    similarity_reasoning_match = re.search(r"SIMILARITY REASONING: (.*?)\n\n", gpt_output, re.DOTALL)
    generated_rating_match = re.search(r"GENERATED RATING: (\d)", gpt_output)
    generated_reasoning_match = re.search(r"GENERATED REASONING: (.*?)\n\n", gpt_output, re.DOTALL)
    actual_rating_match = re.search(r"ACTUAL RATING: (\d)", gpt_output)
    actual_reasoning_match = re.search(r"ACTUAL REASONING: (.*?)\n\n", gpt_output, re.DOTALL)
    best_strategy_match = re.search(r"BEST STRATEGY: (.*?)\n\n", gpt_output, re.DOTALL)

    best_reasoning_match = re.search(r"BEST REASONING: (.*?)(?=\n\n|\Z)", gpt_output, re.DOTALL)


    if similarity_rating_match:
        result["similarity_rating"] = int(similarity_rating_match.group(1))
    if similarity_reasoning_match:
        result["similarity_reasoning"] = similarity_reasoning_match.group(1).strip()
    if generated_rating_match:
        result["generated_rating"] = int(generated_rating_match.group(1))
    if generated_reasoning_match:
        result["generated_reasoning"] = generated_reasoning_match.group(1).strip()
    if actual_rating_match:
        result["actual_rating"] = int(actual_rating_match.group(1))
    if actual_reasoning_match:
        result["actual_reasoning"] = actual_reasoning_match.group(1).strip()
    if best_strategy_match:
        result["best_strategy"] = best_strategy_match.group(1).strip()
    if best_reasoning_match:
        result["best_reasoning"] = best_reasoning_match.group(1).strip()

    # print("BEST REASONING CHECK ----------")
    # print(best_reasoning_match)
    return result

def save_comparison_results_to_json(context_summary, generated_parent_strategy, original_parent_strategy, gpt_output, json_file_path):
    directory = os.path.dirname(json_file_path)
    
    if not os.path.exists(directory) and directory != '':
        os.makedirs(directory)
        print(f"Directory {directory} created.")
    
    parsed_results = parse_gpt_output(gpt_output)

    # Check if the file exists and is not empty
    data = {}
    interaction_number = 1
    if os.path.exists(json_file_path):
        if os.path.getsize(json_file_path) > 0:
            with open(json_file_path, 'r') as json_file:
                try:
                    data = json.load(json_file)
                    interaction_number = len(data) + 1
                except json.JSONDecodeError:
                    print(f"Warning: The file {json_file_path} contains invalid JSON. Proceeding with an empty list.")
                
    
    comparison_result = {
        # "interaction": f"Interaction [{interaction_number}]",
        "context_summary": context_summary,
        "generated_parent_strategy": generated_parent_strategy,
        "original_parent_strategy": original_parent_strategy,
    }
    comparison_result.update(parsed_results)

    full_result = {f"Interaction {interaction_number}" : comparison_result}


    data.update(full_result)

    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"The file has been updated and saved to {json_file_path}.")


# def save_comparison_results_to_json(context_summary, generated_parent_strategy, original_parent_strategy, gpt_output, json_file_path):

#     parsed_results = parse_gpt_output(gpt_output)
    
#     comparison_result = {
#         "context_summary": context_summary,
#         "generated_parent_strategy": generated_parent_strategy,
#         "original_parent_strategy": original_parent_strategy,
#     }
#     comparison_result.update(parsed_results)

#     with open(json_file_path, 'w') as json_file:
#         json.dump(comparison_result, json_file, indent=4)

train_json_file_path = 'ANALYSIS/p10/s2/p10_s2_analysisTEST.json'
test_json_file_path = 'ANALYSIS/p10/s1/p10_s1_analysisTEST.json'

faiss_save_path="FAISS_INDEX/p10/s2"
json_save_path="COMPARISON/p10/s1/p10_s1_test_comparison.json"
# query = "The child is excited"

existing_rules = {}

insights, all_actions = process_all_context_summaries(train_json_file_path, test_json_file_path, faiss_save_path, json_save_path, existing_rules, k=5)

# print("FINAL INSIGHTS:\n\n")
# print(insights)

# print("\n\nFINAL CONCAT INSIGHTS:\n\n")
# concat_insights = concatenate_numbered_rules(insights)
# print(concat_insights)

# print("\n\nALL ACTIONS:\n\n")
# print(all_actions)


# # Store in a text file
# output_file = "INSIGHTS/p11/s2/p10_s1_insightsTEST.txt"
# output_directory = os.path.dirname(output_file)

# # Ensure the directory exists
# if not os.path.exists(output_directory):
#     os.makedirs(output_directory)

# try:
#     with open(output_file, 'w') as file:
#         file.write(concat_rules)
#     print(f"\nResults stored in {output_file}")
# except IOError as e:
#     print(f"Error writing to file: {e}")

# # Example usage:

# existing_rules = {}
# results = process_pairs(json_file_path, query, save_path, existing_rules, k=5)

# # Concatenate numbered rules
# concat_results = concatenate_numbered_rules(results)

# # Print and store in a text file
# print("\nConcatenated Results:\n")
# print(concat_results)


# # reordered_results = reorder_results(results)
# # print(reordered_results)