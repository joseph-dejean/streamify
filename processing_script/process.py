import os
import json
from datetime import datetime
from google.cloud import storage

# Config
RAW_LOG_DIR = "/data/raw_logs"
PROCESSED_DIR = "/data/processed"
BUCKET_NAME = os.environ.get("GCS_BUCKET")

def main():
    print(f"Starting data processing for bucket: {BUCKET_NAME}")
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    
    # 1. Process Logs
    # This is a simple aggregation: count events per video.
    video_counts = {}
    log_files = [f for f in os.listdir(RAW_LOG_DIR) if f.endswith('.json')]
    
    if not log_files:
        print("No new log files to process.")
        return

    for filename in log_files:
        filepath = os.path.join(RAW_LOG_DIR, filename)
        with open(filepath, 'r') as f:
            try:
                data = json.load(f)
                video_id = data.get('video_id')
                if video_id:
                    video_counts[video_id] = video_counts.get(video_id, 0) + 1
            except json.JSONDecodeError:
                print(f"Warning: Could not decode JSON from {filename}")

    # 2. Save processed data to a local file
    processed_filename = f"processed_summary_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json"
    processed_filepath = os.path.join(PROCESSED_DIR, processed_filename)
    with open(processed_filepath, 'w') as f:
        json.dump(video_counts, f)
    
    print(f"Processed data saved to {processed_filepath}")

    # 3. Upload processed data to GCS
    processed_blob_name = f"processed/{processed_filename}"
    blob = bucket.blob(processed_blob_name)
    blob.upload_from_filename(processed_filepath)
    print(f"Uploaded {processed_filepath} to gs://{BUCKET_NAME}/{processed_blob_name}")
    
    # 4. Move raw files to an archive folder in GCS
    for filename in log_files:
        local_path = os.path.join(RAW_LOG_DIR, filename)
        archive_blob_name = f"archive/raw_logs/{filename}"
        blob = bucket.blob(archive_blob_name)
        blob.upload_from_filename(local_path)
        os.remove(local_path) # Delete after archiving
    
    print(f"Archived and removed {len(log_files)} raw log files.")

if __name__ == "__main__":
    main()