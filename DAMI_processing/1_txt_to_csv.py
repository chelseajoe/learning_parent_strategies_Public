import os
import csv
import re

def convert_txt_to_csv(input_file, output_file):
    # Create the output directory if it doesn't exist
    output_directory = os.path.dirname(output_file)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with open(input_file, 'r') as txt_file, open(output_file, 'w', newline='') as csv_file:
        reader = txt_file.readlines()
        writer = csv.writer(csv_file)

        # Write the header row
        writer.writerow(['Speaker', 'Timestamp', 'Transcript'])

        for line in reader:
            line = line.strip()
            if not line:
                continue

            # Extract speaker
            speaker_split = line.split(':', 1)
            if len(speaker_split) < 2:
                continue

            speaker = speaker_split[0].strip()

            # Extract timestamp and transcript
            timestamp_transcript = speaker_split[1].strip()
            match = re.match(r'(\d{2}:\d{2})\s+(.*)', timestamp_transcript)
            if not match:
                continue

            timestamp = match.group(1)
            transcript = match.group(2).strip()

            writer.writerow([speaker, timestamp, transcript])

# Usage
input_file = 'DAMI/p10/s1/p10_s1_transcription.txt'
output_file = 'CSV_FILES/p10/s1/p10_s1_output.csv'
convert_txt_to_csv(input_file, output_file)