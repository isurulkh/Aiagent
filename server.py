from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import asyncio
import os
import httpx
from datetime import datetime
from openai import AsyncOpenAI
from agent_system import AgentSystem, DatabaseConfig, AgentAction

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Load environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', '5432'))
DB_NAME = os.getenv('DB_NAME', 'project_management')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Initialize OpenAI client
openai_client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    http_client=httpx.AsyncClient()
)

# Configure database connection
db_config = DatabaseConfig(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

# Initialize agent system
agent_system = AgentSystem(openai_client, db_config)

# Notification callback for WebSocket
async def notification_callback(action: AgentAction):
    timestamp = action.timestamp.strftime('%H:%M:%S')
    socketio.emit('notification', {
        'timestamp': timestamp,
        'type': action.action_type,
        'description': action.description,
        'status': action.status,
        'progress': action.progress,
        'details': action.details
    })

# Subscribe to notifications
agent_system.subscribe_to_notifications(notification_callback)

@app.route('/api/ask', methods=['POST'])
async def ask_question():
    try:
        data = request.get_json()
        question = data.get('question')
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
            
        response = await agent_system.process_question(question)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def serve_frontend():
    return send_from_directory('frontend/dist', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    try:
        return send_from_directory('frontend/dist', path)
    except:
        return send_from_directory('frontend/dist', 'index.html')

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)