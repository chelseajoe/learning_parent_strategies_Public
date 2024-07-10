import json
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import os
from openai import OpenAI

# Load environment variables
load_dotenv()

# Retrieve OpenAI API Key
api_key = os.getenv('OPENAI_API_KEY') or getpass.getpass("Enter or paste your OpenAI API Key: ")

# Set the API key for OpenAI
os.environ["OPENAI_API_KEY"] = api_key

def create_faiss_index_from_json(json_file_path):
    # Load the JSON data from the file
    with open(json_file_path, 'r') as file:
        data_dict = json.load(file)
    
    # Create documents for each frame number
    documents = []
    for episode, content in data_dict.items():
        document_text = f"{episode}\nScene:\n" + "\n".join(content["scene"]) + "\nList of Insights:\n" + content["parent_strategy"]
        # print(document_text)
        documents.append(document_text)
    
    # Split these documents into chunks (if necessary)
    text_splitter = CharacterTextSplitter()
    split_docs = []
    for doc in documents:
        split_docs.extend(text_splitter.split_text(doc))
    
    # Create embeddings and store them in a FAISS index
    embeddings = OpenAIEmbeddings()
    db = FAISS.from_texts(split_docs, embeddings)
    
    return db

def similarity_search(db, query, k=3):
    # print(f"Document {i}:\n{doc.page_content}\n")
    return db.similarity_search(query, k)

# def compile_documents(docs):
#     compiled_text = "\n\n".join([doc.page_content for doc in docs])
#     return compiled_text

# def compile_insights(docs):
#     insights = []
#     for doc in docs:
#         lines = doc.page_content.split("\n")
#         for i, line in enumerate(lines):
#             if line.startswith("Parent Strategy:"):
#                 # Extract the entire parent strategy
#                 insight = line[len("Parent Strategy: "):]

#                 print("INSIHgT", insight)
#                 insights.append(insight)
#                 break  # Assuming only one "Parent Strategy:" per document
#     return "\n\n".join(insights)

def compile_insights(docs):
    insights = []
    for doc in docs:
        lines = doc.page_content.split("\n")
        strategy_lines = []
        capture = False
        for line in lines:
            if line.startswith("List of Insights:"):
                capture = True
            if capture:
                strategy_lines.append(line)
        insights.append(" ".join(strategy_lines))
    return "\n\n".join(insights)

# def compile_insights(docs):
#     insights = []
#     for doc in docs:
#         lines = doc.page_content.split("\n")
#         strategy_lines = []
#         capture = False
#         for line in lines:
#             if line.startswith("Parent Strategies:"):
#                 capture = True
#                 # strategy_lines.append(line[len("Parent Strategy: "):])
#                 strategy_lines.append(line)
#             elif capture:
#                 if line.strip() == "":
#                     break
#                 strategy_lines.append(line)
#         insights.append(" ".join(strategy_lines))
#     return "\n\n".join(insights)

def generate_parent_strategy(insights, query):
    client = OpenAI()
    # prompt = f"""
    # {insights}

    # Based on the extracted insights above, generate a parenting strategy in the form of a transcript for the following scene and explain the reasoning behind your chosen strategy:

    # {query}

    # Example Transcript:
    # Child: (turned around, not looking at the parent or the book)
    # Parent: Jamie, let's look at the book.
    # Child: (not looking at the book)
    # Parent: Okay, can you place your hands on your knees?
    # """

    prompt = f"""
    {insights}

    Based on the extracted insights above from the activity of a specific parent, generate a parenting strategy that this parent would use for the following scene and explain your reasoning behing your strategy:

    {query}

    Follow this format from this example:

    Child: (looks away from the book and parent, standing up)

    Parenting Strategy: Use the child's interest as a bridge to bring them back to the book-reading activity. Encourage an active break to expend some energy, promoting physical activity as well and then efficiently transition into further reading.

    Parent: (Noticing that the child is getting restless, smiles understandingly) "Let's play a quick game! Can you jump like a kangaroo for a minute? Then we can hop back to our story."

    Child: (Excitedly jumps around like a kangaroo)

    Reasoning: In developing this strategy, the aim is to respect the child's current need for movement while also encouraging their re-engagement with the book. By making the transition activity fun and related to the child's interests it sustains their attention and eagerness to return to reading. This approach also fosters positive associations with reading and learning, as the child sees it as part of a sequence of enjoyable activities. This strategy thus combines physical activity with cognitive development, showing the child that learning can be an engaging and dynamic process.
    """

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

# Example usage
json_file_path = 'JSON_DATA/p11_s2_multi_insights_chunk.json'
# json_file_path = 'json_data/test_strategy.json'

db = create_faiss_index_from_json(json_file_path)
print(db.index.ntotal)  # This should print the number of indexed documents

query = "Child: (cries and throws tantrum)"
docs = similarity_search(db, query, k=3)

# for i, doc in enumerate(docs, 1):
#     print(f"Document {i}:\n{doc.page_content}\n")

compiled_text = compile_insights(docs)
# print("COMPILED TEXT:", compiled_text)
analysis = generate_parent_strategy(compiled_text, query)
print(analysis)
