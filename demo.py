import asyncio
import os
from datetime import datetime
from openai import AsyncOpenAI
from agent_system import AgentSystem, DatabaseConfig

# Load environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', '5432'))
DB_NAME = os.getenv('DB_NAME', 'your_database')
DB_USER = os.getenv('DB_USER', 'your_username')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'your_password')

# Callback function for real-time notifications
async def notification_callback(action):
    timestamp = action.timestamp.strftime('%H:%M:%S')
    if action.action_type == 'error':
        print(f"\033[91m[{timestamp}] ERROR: {action.description}\033[0m")
    else:
        print(f"[{timestamp}] {action.action_type}: {action.description}")

async def process_questions(agent_system, questions):
    try:
        tasks = [agent_system.process_question(question) for question in questions]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for question, response in zip(questions, responses):
            print(f"\nQuestion: {question}")
            if isinstance(response, Exception):
                print(f"Error: {str(response)}")
            else:
                print(f"Answer: {response}")
    except Exception as e:
        print(f"Error processing questions: {str(e)}")

async def main():
    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY environment variable is not set")
        return

    try:
        # Initialize OpenAI client
        openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

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

        # Subscribe to notifications
        agent_system.subscribe_to_notifications(notification_callback)

        # Example questions with more complex scenarios
        questions = [
            "How many employees have worked on project A in the last month?",
            "What is the total budget for project A broken down by each month?",
            "Which employees have the highest productivity rate in project B?",
            "What is the average completion time for tasks in project C?"
        ]

        # Process questions with improved error handling
        await process_questions(agent_system, questions)

    except Exception as e:
        print(f"System error: {str(e)}")

if __name__ == '__main__':
    asyncio.run(main())