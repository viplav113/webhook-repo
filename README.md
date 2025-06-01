# webhook-repo
# 🚀 GitHub Webhook Listener with Flask and MongoDB

This project is a Flask-based server that listens to GitHub Webhook events (like `push` and `pull_request`) and stores them in MongoDB. It also verifies GitHub webhook signatures and displays the latest events in JSON format.

---

## 📦 Features

- ✅ Verifies GitHub Webhook secret
- ✅ Handles GitHub `push`, `pull_request`, and `ping` events
- ✅ Stores event data into MongoDB
- ✅ Shows the 10 latest events in JSON
- ✅ ngrok support for local development

---

## 🛠 Requirements

- Python 3.10+
- MongoDB instance (local or cloud like MongoDB Atlas)
- ngrok (for exposing your local server to GitHub)
- GitHub repository

---

---

## ⚙️ Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/your-username/webhook-repo.git
cd webhook-repo
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
#requirements.txt should contain:
```bash
Flask
python-dotenv
pymongo
```

### 4. Configure Environment Variables
#Create a .env file in the root directory:
```bash
MONGO_URI=mongodb+srv://<username>:<password>@<cluster-url>/webhook_db?retryWrites=true&w=majority
WEBHOOK_SECRET=your_github_webhook_secret
```

### 5. Run the Flask App
```bash
python app.py
```

### 6.Expose Local Server to GitHub with ngrok
- Install ngrok
- Start ngrok
  ```bash
  ngrok http 5000
  ```
-You'll get a URL like:
  ```bash
  https://a4d3-xxxxxx.ngrok-free.app
  ```

### 7.Configure GitHub Webhook

### API Endpoints
| Endpoint   | Method | Description                          |
| ---------- | ------ | ------------------------------------ |
| `/`        | GET    | Renders a basic home HTML page       |
| `/webhook` | POST   | Receives and processes GitHub events |
| `/events`  | GET    | Returns latest 10 events in JSON     |

### Sample Output
```bash
[
  {
    "_id": "66575548feacb86748b0db7d",
    "request_id": "123abc",
    "author": "johndoe",
    "action": "PUSH",
    "from_branch": null,
    "to_branch": "main",
    "timestamp": "2025-06-01T14:25:31Z"
  }
]
```
![image](https://github.com/user-attachments/assets/c3282051-53ea-47ca-8b5d-3cd1f61a759e)




