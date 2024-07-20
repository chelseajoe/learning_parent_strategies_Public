import os

def rename_files_in_subdirectories(directory_path, new_name):
    for participant_dir in os.listdir(directory_path):
        participant_path = os.path.join(directory_path, participant_dir)
        if os.path.isdir(participant_path):
            for session_dir in os.listdir(participant_path):
                session_path = os.path.join(participant_path, session_dir)
                if os.path.isdir(session_path):
                    participant = participant_dir
                    session = session_dir
                    print(f"Processing Participant: {participant}, Session: {session}")
                    
                    for file_name in os.listdir(session_path):
                        file_path = os.path.join(session_path, file_name)
                        if os.path.isfile(file_path):
                            filename = (f"{participant}_{session}_{new_name}")
                            new_file_path = os.path.join(session_path, filename)
                            os.rename(file_path, new_file_path)
                            print(f"Renamed {file_path} to {new_file_path}")

# Example usage
directory_path = 'DATA/BATCH/INSIGHT_OUTPUT'
new_name = 'batch_insight_output.jsonl'
rename_files_in_subdirectories(directory_path, new_name)