import json
import os
import uuid
from datetime import datetime
from flask import Flask, jsonify

app = Flask(__name__)
LOG_DIR = "/data/raw_logs"

# Ensure the log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

@app.route('/log', methods=['POST'])
def log_activity():
    """Simulates receiving and logging a user activity event."""
    event = {
        'event_id': str(uuid.uuid4()),
        'user_id': f"user_{uuid.uuid4().hex[:6]}",
        'video_id': f"video_{uuid.uuid4().hex[:4]}",
        'event_type': 'play',
        'timestamp': datetime.utcnow().isoformat() + "Z"
    }
    
    filename = os.path.join(LOG_DIR, f"event_{event['event_id']}.json")
    with open(filename, 'w') as f:
        json.dump(event, f)
        
    return jsonify({"status": "success", "event_id": event['event_id']}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)