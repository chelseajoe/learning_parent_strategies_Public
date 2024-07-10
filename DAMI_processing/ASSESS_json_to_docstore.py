import json
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import os
from openai import OpenAI
import getpass

# Load environment variables
load_dotenv()

# Retrieve OpenAI API Key
api_key = os.getenv('OPENAI_API_KEY') or getpass.getpass("Enter or paste your OpenAI API Key: ")

# Set the API key for OpenAI
os.environ["OPENAI_API_KEY"] = api_key

def create_faiss_index_from_json(json_file_path, faiss_index_path):
    # Load the JSON data from the file
    with open(json_file_path, 'r') as file:
        data_dict = json.load(file)
    
    # Create documents for each frame number
    documents = []
    for episode, content in data_dict.items():
        document_text = f"{episode}\nScene:\n" + "\n".join(content["scene"]) + "\nList of Insights:\n" + content["parent_strategy"]
        print(document_text)
        documents.append(document_text)
    
    # Split these documents into chunks (if necessary)
    text_splitter = CharacterTextSplitter()
    split_docs = []
    for doc in documents:
        split_docs.extend(text_splitter.split_text(doc))
    
    # Create embeddings and store them in a FAISS index
    embeddings = OpenAIEmbeddings()
    db = FAISS.from_texts(split_docs, embeddings)
    
    # Save the FAISS index to disk
    db.save_local(faiss_index_path)
    
    return db

def load_faiss_index(faiss_index_path):
    # Load the FAISS index from disk
    embeddings = OpenAIEmbeddings()
    db = FAISS.load_local(faiss_index_path, embeddings, allow_dangerous_deserialization=True)
    
    return db

def ensure_faiss_index(json_file_path, faiss_index_path):
    if os.path.exists(faiss_index_path):
        print("FAISS index already exists. Loading from disk...")
        return load_faiss_index(faiss_index_path)
    else:
        print("FAISS index not found. Creating a new one...")
        return create_faiss_index_from_json(json_file_path, faiss_index_path)

def similarity_search(db, query, k=3):
    return db.similarity_search(query, k)

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

def compile_episodes(docs):
    episodes = []
    for doc in docs:
        episodes.append(doc.page_content)
    return "\n\n".join(episodes)

def generate_parent_strategy(episodes, question, explanation):
    client = OpenAI()
    prompt = f"""

    You are analyzing a parent and child scene and rating the parent based on their parenting ability from a score of 1 - 3 given the question.

    0 = 'None' - Absent; didn't see, not observed.
    1 = 'Some' - Barely there; seen sometimes.
    2 = 'Lots' - Consistently there; seen often.

    Question: {question}

    Explanation: {explanation}

    Based on the episodes and the question below:

    {episodes}

    Output your score and explain your analysis.

    Here is an example output. Follow this format from this example EXACTLY:

    I would rate the parent a [2 (Lots)] for speaking in a warm tone of voice. 

    Analysis:

    1. Tone and Expressiveness:
        - Parent Strategy: The parent uses a calm and expressive tone while narrating the story.
        - Reasoning: The use of a calm and expressive tone demonstrates warmth. The tone is not just calm but also expressive, indicating positive emotions and enthusiasm, which is highlighted as an effective strategy to keep the child engaged. 

    2. Emotional Engagement:
        - Parent Strategy: The parent builds anticipation with phrases like "until the weather took a turn for the worse. Uh-oh."
        - Reasoning: This enthusiastic approach shows an ability to convey excitement and suspense, indicative of a warm and engaging tone.

    3. Empathy and Validation:
        - Parent Strategy: The parent acknowledges the child's concern about a character's well-being with empathy ("Oh he's sick").
        - Reasoning: The parent's empathetic response indicates tenderness and care, further contributing to a warm atmosphere.

    4. Expressive Sounds and Actions:
        - Parent Strategy: Adding expressive sounds and actions to the storytelling ("BUMP! Horton landed").
        - Reasoning: These elements of sound effects demonstrate an effort to engage the child in an animated and warm manner.
    """

    print(prompt)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
    )
    return response.choices[0].message.content

# Example usage
json_file_path = 'json_data/p17_s2_multi_insights_chunk.json'
faiss_index_path = 'faiss_index/p17/p2'
questions_file_path = 'PICCOLO/piccolo_sample.json'
output_file_path = 'ASSESSMENT/p17_s2_assessment_sample_v2.txt'

os.makedirs(os.path.dirname(output_file_path), exist_ok=True)


# Ensure FAISS index exists
db = ensure_faiss_index(json_file_path, faiss_index_path)
print(db.index.ntotal)  # This should print the number of indexed documents

query = "Child: (cries and throws tantrum)"
# docs = similarity_search(db, query, k=3)

# compiled_episodes = compile_episodes(docs)

# Load questions from the JSON file
with open(questions_file_path, 'r') as file:
    questions_json = json.load(file)

with open(output_file_path, 'w') as output_file:
    for question_obj in questions_json:
        for key, value in question_obj.items():
            question = value["question"]
            explanation = value["explanation"]
            docs = similarity_search(db, question, k=3)
            compiled_episodes = compile_episodes(docs)
            analysis = generate_parent_strategy(compiled_episodes, question, explanation)
            output_file.write(f"Analysis for {key}:\n")
            output_file.write(analysis)
            output_file.write("\n\n")

print(f"Analysis has been written to {output_file_path}")
