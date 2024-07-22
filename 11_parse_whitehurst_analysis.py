import os
import json

def process_file(input_file_path, output_file_path):
    sections = [
        "Prompting the Child",
        "Evaluating the Child's Response",
        "Expanding the Child's Response",
        "Repeating the Prompt",
        "Overall Score",
        "Explanation",
        "How the Parent Can Improve"
    ]

    data = {section: {} for section in sections[:-1]}
    data[sections[-1]] = {}

    current_section = None
    current_subsection = None
    analysis_lines = []

    if not os.path.exists(os.path.dirname(output_file_path)):
        os.makedirs(os.path.dirname(output_file_path))

    with open(input_file_path, 'r') as file:
        lines = file.readlines()
    
    for line in lines:
        line = line.strip()
        if any(section in line for section in sections):
            current_section = next((section for section in sections if section in line), None)
            # print(current_section)
            
            current_subsection = None
            analysis_lines = []  # Reset analysis lines for the new section
            explanation_lines = []
            if current_section != "Overall Score" and current_section != "Explanation":
                continue

        if current_section:
            # print(current_section)
            if current_section == "Overall Score":
                # print(current_section)
                # print(line)
                data[current_section] = line[len("Overall Score:"):].strip()
                current_section = None
                continue

            if current_section == "Explanation":
                # print(current_section)
                if line.startswith('Explanation:') or line == '':
                    continue
                data[current_section] = line.strip()
                # print(line)
                # explanation_lines.append(line)

                continue

            if line == '':
                continue
            
                # print(line)
            if current_section == "How the Parent Can Improve":
                if line.startswith('- '):
                    # print(line)
                    # current_subsection = line[2:].strip()
                    data[current_section][current_subsection].append(line.lstrip('-').strip())
                else:
                    current_subsection = line
                    data[current_section][current_subsection] = []
            else:
                if "Analysis:" in line:
                    current_subsection = "Analysis"
                    analysis_lines.append(line[len("Analysis:"):].strip())
                elif line.startswith("Quotes:"):
                    if current_subsection == "Analysis":
                        data[current_section][current_subsection] = " ".join(analysis_lines).strip()
                    current_subsection = "Quotes"
                    data[current_section][current_subsection] = []
                elif line.startswith("Score:"):
                    if current_subsection == "Analysis":
                        data[current_section][current_subsection] = " ".join(analysis_lines).strip()
                    current_subsection = "Score"
                    data[current_section][current_subsection] = line[len("Score:"):].strip()
                else:
                    if current_subsection == "Analysis":
                        analysis_lines.append(line)
                    elif current_subsection == "Quotes":
                        data[current_section][current_subsection].append(line.lstrip('-').strip())

    with open(output_file_path, 'w') as output_file:
        json.dump(data, output_file, indent=4)

    print(f"Whitehurst analysis parsed for: {input_file_path}")



def parse_whitehurst_analysis(header_directory, participant, session):
    input_file_path = f'{header_directory}/GENERATED_WHITEHURST/{participant}/{session}/{participant}_{session}_whitehurst.txt'
    output_file_path = f'{header_directory}/WHITEHURST/{participant}/{session}/{participant}_{session}_whitehurst.json'
    process_file(input_file_path, output_file_path)

# Example usage:
header_directory = 'DATA'
participant = 'p10'
session = 's1'
parse_whitehurst_analysis(header_directory, participant, session)