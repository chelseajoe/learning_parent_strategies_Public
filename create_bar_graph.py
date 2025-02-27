import matplotlib.pyplot as plt
import pandas as pd
import re

def read_data(file_path):
    with open(file_path, 'r') as file:
        lines = file.read()
        
    # Use regex to parse the data, accommodating potential newlines and spaces
    pattern = re.compile(r'^(p\d+_s\d+)\s*Overall Average Precision@K Score across all queries:\s*([\d.]+)\s*Overall Average Insight Retrieval Score across all contexts:\s*([\d.]+)', re.MULTILINE)

    data = []
    for match in pattern.finditer(lines):
        participant = match.group(1)
        precision_score = float(match.group(2))
        insight_score = float(match.group(3))

        data.append((participant, precision_score, insight_score))

    return pd.DataFrame(data, columns=['Participant', 'Precision@K Score', 'Insight Retrieval Score'])

def plot_data(df):
    # Plot the data
    fig, ax = plt.subplots(figsize=(12, 5))  # Adjust the figure size

    # Create the bar positions
    index = range(len(df))
    
    # Adjust bar width here to make it thinner
    bar_width = 0.25  # Set to 0.25 for thinner bars

    # Plot the Precision@K Scores
    bar1 = ax.bar(index, df['Precision@K Score'], bar_width, label='Precision@K Score', color=(0.647, 0.69, 0.749))  # Use RGB values (0-1) gray

    # Plot the Insight Retrieval Scores
    bar2 = ax.bar([i + bar_width for i in index], df['Insight Retrieval Score'], bar_width, label='Insight Retrieval Score', color=(1, 0.271, 0.435))  # Use RGB values (0-1)
    # bar2 = ax.bar([i + bar_width for i in index], df['Insight Retrieval Score'], bar_width, label='Insight Retrieval Score', color=(1, 0.392, 0.529))  # Use RGB values (0-1)

    # Set the labels
    ax.set_xlabel('Participants')
    ax.set_ylabel('Scores')
    # ax.set_title('Average Scores per Parent')
    ax.set_xticks([i + bar_width / 2 for i in index])
    ax.set_xticklabels(df['Participant'], rotation=45, ha='right')

    # Move the legend outside the plot
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.05), fontsize=10)  # Adjust location and size of the legend

    # Set the y-axis limits from 0.0 to 1.0
    ax.set_ylim(0.0, 1.0)

    # Add a horizontal dotted line at y = 0.8
    # ax.axhline(y=0.8, color='gray', linestyle='--', linewidth=1, label='Threshold (0.8)')
    ax.axhline(y=0.8, color='black', linestyle='--', linewidth=1, label='Threshold (0.8)')
     # Add a horizontal dotted line at y = 0.8
    # ax.axhline(y=0.9, color='gray', linestyle='--', linewidth=1, label='Threshold (0.9)')

    # Annotate the bar values (Removed this part)
    # for bar in bar1 + bar2:
    #     yval = bar.get_height()
    #     ax.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.2f}', ha='center', va='bottom')

    plt.tight_layout()
    plt.show()

def main(file_path):
    df = read_data(file_path)
    plot_data(df)

# # Usage example
# file_path = 'final_averages.txt'  # Replace this with the actual path to your data file
# main(file_path)

# Usage example
file_path = 'DATA/FINAL_SCORES/final_averages.txt'  # Replace this with the actual path to your data file
main(file_path)
