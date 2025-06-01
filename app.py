import os
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import hmac
import hashlib
import json
from datetime import datetime, timezone

load_dotenv()

app = Flask(__name__)

# Connect to MongoDB
try:
    client = MongoClient(os.getenv("MONGO_URI")) # Replace with your MongoDB URI
    db = client["webhook_db"] # Replace with your database name
    # Verify connection
    client.admin.command('ping')
    print("✅ Connected to MongoDB")
    events = db.events
    print(f"Using database: {db.name}")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    events = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/webhook', methods=['GET', 'POST'])
def handle_webhook():
    if request.method == 'GET':
        # Handle GitHub verification
        return request.args.get('hub.challenge', ''), 200

    try:
        # 1. Verify signature
        signature_header = request.headers.get('X-Hub-Signature-256', '')
        if not signature_header:
            app.logger.error("Missing X-Hub-Signature-256 header")
            return jsonify({"error": "Missing signature"}), 403
        
        # 2. Get secret
        webhook_secret = os.getenv("WEBHOOK_SECRET")
        if not webhook_secret:
            app.logger.error("WEBHOOK_SECRET not configured")
            return jsonify({"error": "Server misconfigured"}), 500
        
        # 3. Create expected signature
        body = request.get_data()
        digest = hmac.new(
            webhook_secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()
        expected_signature = f"sha256={digest}"
        
        # 4. Compare signatures
        if not hmac.compare_digest(signature_header, expected_signature):
            app.logger.error(f"Signature mismatch! Received: {signature_header}, Expected: {expected_signature}")
            return jsonify({"error": "Invalid signature"}), 403
        
        # 5. Process event
        event_type = request.headers.get('X-GitHub-Event')
        if not event_type:
            return jsonify({"error": "Missing GitHub event header"}), 400
        
        # Handle ping event
        if event_type == 'ping':
            app.logger.info("✅ Received ping event")
            return jsonify({"status": "pong"}), 200
        
        payload = request.json
        app.logger.info(f"Received {event_type} event")
        
        if event_type == 'push':
            process_push(payload)
        elif event_type == 'pull_request':
            process_pull_request(payload)
        else:
            app.logger.info(f"Ignored event type: {event_type}")
            
        return jsonify({"status": "success"}), 200
    
    except Exception as e:
        app.logger.error(f"Webhook error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Function to process push events
def process_push(payload):
    try:
        print("Processing PUSH event")
        author = payload['pusher']['name']
        branch = payload['ref'].split('/')[-1]
        timestamp = datetime.now(timezone.utc).isoformat()
        
        event_data = {
            "request_id": payload['head_commit']['id'],
            "author": author,
            "action": "PUSH",
            "from_branch": None,
            "to_branch": branch,
            "timestamp": timestamp
        }
        print(f"Inserting push event: {event_data}")
        result = events.insert_one(event_data)
        print(f"Inserted ID: {result.inserted_id}")
    except KeyError as e:
        print(f"Key error in push payload: {e}")
        print(f"Payload keys: {list(payload.keys())}")

# Function to process pull request events
def process_pull_request(payload):
    try:
        action = payload['action']
        pr = payload['pull_request']
        
        if action not in ['opened', 'closed']:
            return

        author = pr['user']['login']
        from_branch = pr['head']['ref']
        to_branch = pr['base']['ref']
        timestamp = datetime.now(timezone.utc).isoformat()

        event_type = "PULL_REQUEST"
        if action == 'closed' and pr.get('merged'):
            event_type = "MERGE"

        event_data = {
            "request_id": str(pr['id']),
            "author": author,
            "action": event_type,
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp
        }

        print(f"Inserting PR event: {event_data}")
        result = events.insert_one(event_data)
        print(f"Inserted ID: {result.inserted_id}")
    except KeyError as e:
        print(f"Key error in PR payload: {e}")

# Endpoint to retrieve latest events
@app.route('/events', methods=['GET'])
def get_events():
    try:
        latest_events = list(events.find().sort("timestamp", -1).limit(10))
        for event in latest_events:
            event["_id"] = str(event["_id"])
        return jsonify(latest_events)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)