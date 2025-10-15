import json
import os
import uuid
from datetime import datetime
import time
from google.cloud import storage

# --- Configuration ---
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "your-bucket-name-here")
RAW_LOGS_DIR = "temp_raw_logs"
ARCHIVE_FOLDER = "archive"
PROCESSED_FOLDER = "processed"
# -----------------------------------------------

def initialize_gcs_client():
    """Initializes and returns the GCS bucket object."""
    try:
        storage_client = storage.Client()
        return storage_client.bucket(BUCKET_NAME)
    except Exception as e:
        print("\n" + "="*70)
        print("!!! GCS CONNECTION ERROR !!!")
        print(f"Error: {e}")
        print("\nSOLUTION: Please run 'gcloud auth application-default login' in your terminal and try again.")
        print("="*70 + "\n")
        return None

def generate_and_save_raw_logs(num_logs=20):
    """Generates random logs and saves them to a local temp folder."""
    os.makedirs(RAW_LOGS_DIR, exist_ok=True)
    print(f"\n--- Generating {num_logs} raw logs locally ---")
    for i in range(num_logs):
        event = {
            'event_id': str(uuid.uuid4()),
            'user_id': f"user_{uuid.uuid4().hex[:6]}",
            'video_id': f"video_{uuid.uuid4().hex[:4]}",
            'event_type': 'play',
            'timestamp': datetime.utcnow().isoformat() + "Z"
        }
        filename = f"{RAW_LOGS_DIR}/event_{event['event_id']}.json"
        with open(filename, 'w') as f:
            json.dump(event, f)
        print(f"  {i+1}/{num_logs}: Created local log {filename}")
    return [os.path.join(RAW_LOGS_DIR, f) for f in os.listdir(RAW_LOGS_DIR)]

def process_and_upload_all(bucket_obj, log_files):
    """
    Simulates the Airflow processing step.
    1. Aggregates data. 2. Uploads summary to /processed. 3. Archives raw files to /archive.
    """
    print("\n--- Starting Data Processing and Upload ---")
    
    # 1. SIMULATE PROCESSING (Aggregation)
    video_counts = {}
    for filepath in log_files:
        with open(filepath, 'r') as f:
            data = json.load(f)
            video_id = data.get('video_id')
            if video_id:
                video_counts[video_id] = video_counts.get(video_id, 0) + 1
    
    # 2. UPLOAD PROCESSED DATA (The New File)
    processed_data_json = json.dumps(video_counts)
    summary_filename = f"{PROCESSED_FOLDER}/summary_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json"
    
    print(f"  Uploading summary to gs://{BUCKET_NAME}/{summary_filename}...")
    bucket_obj.blob(summary_filename).upload_from_string(
        data=processed_data_json,
        content_type='application/json'
    )

    # 3. ARCHIVE RAW LOGS (The Original Files)
    print(f"  Archiving {len(log_files)} raw logs to gs://{BUCKET_NAME}/{ARCHIVE_FOLDER}/...")
    for filepath in log_files:
        filename = os.path.basename(filepath)
        archive_blob_name = f"{ARCHIVE_FOLDER}/{filename}"
        bucket_obj.blob(archive_blob_name).upload_from_filename(filepath)
        os.remove(filepath) # Clean up local temp file

    os.rmdir(RAW_LOGS_DIR)
    print("--- Processing and Upload Complete. ---")

def main():
    bucket_obj = initialize_gcs_client()
    if not bucket_obj:
        return

    # FULL PIPELINE EXECUTION
    try:
        log_files = generate_and_save_raw_logs(num_logs=20)
        process_and_upload_all(bucket_obj, log_files)
        print("\nSUCCESS: Go to your GCS bucket to see the 'processed' and 'archive' folders.")
    except Exception as e:
        print(f"\nFATAL ERROR during pipeline execution: {e}")

if __name__ == "__main__":
    # Ensure google-cloud-storage is installed
    try:
        from google.cloud import storage # Import it to make sure it's available
    except ImportError:
        print("\n*** ERROR: The 'google-cloud-storage' library is not installed. ***")
        print("Please run: pip install google-cloud-storage")
        exit()
        
    main()