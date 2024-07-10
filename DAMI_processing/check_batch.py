from dotenv import load_dotenv
import os
from openai import OpenAI
import getpass

# Load environment variables
load_dotenv()

# Retrieve OpenAI API Key
api_key = os.getenv('OPENAI_API_KEY') or getpass.getpass("Enter or paste your OpenAI API Key: ")

client = OpenAI()

content = client.batches.retrieve("batch_d2ruhaC18zUwDfuVJpvdkDDo")

print(content)

all_batches = client.batches.list(limit=10)
print(all_batches)

# Batch(id='batch_d2ruhaC18zUwDfuVJpvdkDDo', completion_window='24h', created_at=1719689696, endpoint='/v1/chat/completions', input_file_id='file-hbokgxB9outa2Fg7i80JkVqc', object='batch', status='failed', cancelled_at=None, cancelling_at=None, completed_at=None, error_file_id=None, errors=Errors(data=[BatchError(code='missing_required_parameter', line=1, message="Missing required parameter: 'custom_id'.", param='custom_id')], object='list'), expired_at=None, expires_at=1719776096, failed_at=1719689697, finalizing_at=None, in_progress_at=None, metadata={'description': 'Chunking transcripts'}, output_file_id=None, request_counts=BatchRequestCounts(completed=0, failed=0, total=0))