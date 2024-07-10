import csv
import json
import re
import os
import pandas as pd

def extract_interaction_chunks(txt_file_path, csv_file_path, output_json_path):
    chunks = []

    # Step 1: Read the txt file and identify the interaction chunks
    # with open(txt_file_path, 'r') as file:
    #     content = file.read()
    #     # Pattern to match the content between "Interaction Chunk" markers
    #     chunk_pattern = re.compile(r'(Interaction Chunk \d+:\n\n.*?\n\n)(?=(Interaction Chunk \d+:|$))', re.DOTALL)
    #     chunk_matches = chunk_pattern.findall(content)
    #     print(chunk_matches)
    #     # print(content)
    # with open(txt_file_path, 'r') as file:
    #     content = file.read()
    #     # Pattern to match the content between "Interaction Chunk" markers, including the last one
    #     chunk_pattern = re.compile(r'(Interaction Chunk \d+:\n\n.*?\n\n)(?=(Interaction Chunk \d+:|\Z))', re.DOTALL)
    #     chunk_matches = chunk_pattern.findall(content)
    #     if chunk_matches:
    #         # Extract the last interaction chunk marker directly
    #         last_interaction_chunk_marker = re.search(r'Interaction Chunk \d+:', chunk_matches[-1])
    #         print(last_interaction_chunk_marker)
    #         if last_interaction_chunk_marker:
    #             last_chunk_marker = last_interaction_chunk_marker.group(0)
    #             # print(last_chunk_marker)

    # Step 1: Read the txt file and identify the interaction chunks
    with open(txt_file_path, 'r') as file:
        content = file.read()
        # Pattern to match the content between "Interaction Chunk" markers, including the last one
        chunk_pattern = re.compile(r'(Interaction Chunk \d+:\n\n.*?\n\n)(?=(Interaction Chunk \d+:|$))', re.DOTALL)
        chunk_matches = chunk_pattern.findall(content)

        # Extract the last interaction chunk marker directly from chunk_matches[-1]
        last_chunk_marker = chunk_matches[-1][1]  # Accessing the second element of the tuple

        # Find the index where the last chunk ends
        last_chunk_end_index = content.find(last_chunk_marker) + len(last_chunk_marker)
        # chunk_matches.pop()

        # Append the text after the last chunk marker to chunk_matches
        if last_chunk_end_index < len(content):
            remaining_text = content[last_chunk_end_index:]
            chunk_matches.append((last_chunk_marker+remaining_text, "LAST CHUNK"))

    # Now chunk_matches contains all chunks including the last one with its marker and text
    print(chunk_matches)
        
    # Step 2: For each chunk, extract the first and last line numbers
    for chunk in chunk_matches:
        first_line_match = re.search(r'\(first\) Line \[(\d+)\]:', chunk[0])
        last_line_match = re.search(r'\(last\) Line \[(\d+)\]:', chunk[0])

        # print(first_line_match)
        print(last_line_match)
        if first_line_match and last_line_match:
            first_line =  int(re.search(r'\[(\d+)\]', first_line_match.group(0)).group(1))
            last_line = int(re.search(r'\[(\d+)\]', last_line_match.group(0)).group(1))
            # print(first_line)
            # print(last_line)
            chunks.append((first_line, last_line))

    # Step 3: Read the CSV file and extract data corresponding to the line numbers using pandas
    df = pd.read_csv(csv_file_path)

    data = []
    for first_line, last_line in chunks:
        chunk_data = df.iloc[first_line:last_line + 1].to_dict(orient='records')
        data.append(chunk_data)

    # Step 4: Structure the data into JSON format
    json_output = []
    for i, chunk_data in enumerate(data):
        chunk_dict = {
            "Interaction Chunk": i,
            "Lines": chunk_data
        }
        json_output.append(chunk_dict)

    # Step 5: Save the JSON data to a file
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)

    with open(output_json_path, 'w') as jsonfile:
        json.dump(json_output, jsonfile, indent=4)

# Example usage:
extract_interaction_chunks('CHUNK_TXT/p10/s1/p10_s1_chunking.txt', 'CSV_FILES/p10/s1/p10_s1_output.csv', 'CHUNK_DATA/p10/s1/p10_s1_chunk_data.json')
    