# AI-Powered Project Management Query System

This project is an intelligent query system that uses AI to analyze and respond to questions about project management data. It combines OpenAI's GPT models with a PostgreSQL database to provide natural language interactions for project management insights.

## Features

- Natural language processing for project management queries
- Real-time notifications through WebSocket
- Interactive web interface
- Asynchronous processing
- Detailed project analytics and insights

## Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL 12+
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd chatagentdd
```

2. Set up Python virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the frontend:
```bash
cd frontend
npm install
npm run build
cd ..
```

## Database Setup

1. Create a PostgreSQL database:
```sql
CREATE DATABASE project_management;
```

2. Initialize the database schema:
```bash
psql -d project_management -f schema.sql
```

3. (Optional) Load sample data:
```bash
psql -d project_management -f sample_data.sql
```

## Configuration

1. Create a `.env` file in the root directory with the following variables:
```env
OPENAI_API_KEY=your_openai_api_key
DB_HOST=localhost
DB_PORT=5432
DB_NAME=project_management
DB_USER=your_database_user
DB_PASSWORD=your_database_password
```

## Running the Application

1. Start the server:
```bash
python server.py
```

2. Access the application:
Open your browser and navigate to `http://localhost:5000`

## Usage Examples

The system can answer questions about projects, employees, and tasks. Example queries:

- "How many employees have worked on project A in the last month?"
- "What is the total budget for project A broken down by each month?"
- "Which employees have the highest productivity rate in project B?"
- "What is the average completion time for tasks in project C?"

## Development

For development purposes, you can run the frontend development server:

```bash
cd frontend
npm run dev
```

This will start the Vite development server with hot reload.

## Project Structure

```
├── agent_system.py     # Core AI agent system
├── server.py          # Flask server implementation
├── demo.py            # Demo script for testing
├── requirements.txt   # Python dependencies
├── schema.sql         # Database schema
├── sample_data.sql    # Sample database data
├── frontend/          # React frontend application
└── .env              # Environment configuration
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the GPT API
- Flask for the web framework
- React for the frontend framework
- PostgreSQL for the database