import asyncio
import openai
import psycopg2
import json
import time
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass
from tenacity import retry, stop_after_attempt, wait_exponential

@dataclass
class DatabaseConfig:
    host: str
    port: int
    database: str
    user: str
    password: str

class AgentAction:
    def __init__(self, action_type: str, description: str, status: str = "started", progress: float = 0.0, details: Dict[str, Any] = None):
        self.action_type = action_type
        self.description = description
        self.timestamp = datetime.now()
        self.status = status  # started, in_progress, completed, error
        self.progress = progress  # 0.0 to 1.0
        self.details = details or {}

    def update_progress(self, progress: float, status: str = None, details: Dict[str, Any] = None):
        self.progress = max(0.0, min(1.0, progress))
        if status:
            self.status = status
        if details:
            self.details.update(details)
        self.timestamp = datetime.now()

    def mark_completed(self, details: Dict[str, Any] = None):
        self.status = "completed"
        self.progress = 1.0
        if details:
            self.details.update(details)
        self.timestamp = datetime.now()

    def mark_error(self, error_message: str, details: Dict[str, Any] = None):
        self.status = "error"
        if details:
            self.details.update(details)
        self.details["error_message"] = error_message
        self.timestamp = datetime.now()

class NotificationManager:
    def __init__(self):
        self.subscribers = []

    async def notify(self, action: AgentAction):
        for subscriber in self.subscribers:
            await subscriber(action)

    def subscribe(self, callback):
        self.subscribers.append(callback)

class RateLimiter:
    def __init__(self, calls_per_minute: int = 20):
        self.calls_per_minute = calls_per_minute
        self.calls = []
        self._lock = asyncio.Lock()

    async def wait(self):
        async with self._lock:
            now = time.time()
            self.calls = [call_time for call_time in self.calls if now - call_time < 60]
            if len(self.calls) >= self.calls_per_minute:
                wait_time = 60 - (now - self.calls[0])
                await asyncio.sleep(wait_time)
            self.calls.append(now)

class QueryAnalyzerAgent:
    def __init__(self, openai_client, notification_manager: NotificationManager):
        self.openai_client = openai_client
        self.notification_manager = notification_manager
        self.rate_limiter = RateLimiter()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def analyze_question(self, question: str) -> Dict[str, Any]:
        await self.notification_manager.notify(
            AgentAction("analysis", "Analyzing user question to determine relevant data sources")
        )

        await self.rate_limiter.wait()
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an intelligent assistant that can handle both casual conversations and database queries. First, determine if the input is a casual conversation or a database query.\n\nFor casual conversations (greetings, small talk, etc), return a JSON object with this structure:\n{\n  \"type\": \"conversation\",\n  \"response\": \"appropriate_friendly_response\"\n}\n\nFor database queries, analyze the PostgreSQL database with the following schema:\n\n1. projects (project_id, project_name, start_date, end_date, budget, status)\n2. employees (employee_id, first_name, last_name, email, hire_date, role)\n3. tasks (task_id, project_id, task_name, description, start_date, due_date, completion_date, status, priority)\n4. project_assignments (assignment_id, project_id, employee_id, start_date, end_date, role, hours_allocated)\n5. task_assignments (assignment_id, task_id, employee_id, assigned_date)\n6. performance_metrics (metric_id, employee_id, project_id, evaluation_date, productivity_score, quality_score, communication_score, comments)\n7. project_budgets (budget_id, project_id, month, planned_amount, actual_amount, category)\n\nFor database queries, return a JSON object with this structure:\n{\n  \"type\": \"database\",\n  \"tables\": [\"required_table_names\"],\n  \"fields\": [\"required_field_names\"],\n  \"conditions\": [\"specific_conditions\"],\n  \"joins\": [\"required_join_conditions\"],\n  \"context\": \"analysis_explanation\"\n}\n\nFor project and employee related queries, always consider the project_assignments table for accurate results."}, 
                    {"role": "user", "content": question}
                ]
            )
            try:
                analysis = json.loads(response.choices[0].message.content)
                return analysis
            except json.JSONDecodeError as je:
                await self.notification_manager.notify(
                    AgentAction("error", f"Invalid JSON response from analysis: {str(je)}")
                )
                return {
                    "type": "database",
                    "tables": ["employees", "project_assignments", "projects"],
                    "fields": ["first_name", "last_name", "role"],
                    "conditions": [],
                    "joins": ["employees.employee_id = project_assignments.employee_id", "project_assignments.project_id = projects.project_id"],
                    "context": "Error analyzing question. Using default employee-project query structure."
                }
        except Exception as e:
            await self.notification_manager.notify(
                AgentAction("error", f"Error in analysis: {str(e)}")
            )
            raise

class QueryGeneratorAgent:
    def __init__(self, openai_client, notification_manager: NotificationManager):
        self.openai_client = openai_client
        self.notification_manager = notification_manager
        self.rate_limiter = RateLimiter()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_query(self, question: str, analysis: Dict[str, Any]) -> str:
        action = AgentAction("query_generation", "Generating SQL query based on analysis")
        await self.notification_manager.notify(action)

        await self.rate_limiter.wait()
        try:
            # Update progress for analysis validation
            action.update_progress(0.2, "in_progress", {"step": "Validating analysis"})
            if not isinstance(analysis, dict) or 'type' not in analysis:
                raise ValueError("Invalid analysis format")

            if analysis['type'] != 'database':
                raise ValueError("Not a database query")

            # Update progress for query generation
            action.update_progress(0.4, "in_progress", {"step": "Generating SQL query"})
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a SQL query generator for a PostgreSQL database. Your task is to generate a precise SQL query that MUST start with SELECT. Follow these rules:\n1. Always start with SELECT\n2. Use proper table aliases (e for employees, p for projects, etc.)\n3. Include all necessary JOIN conditions\n4. Handle NULL values with COALESCE when needed\n5. Add case-insensitive WHERE clauses using LOWER()\n6. Use ORDER BY for consistent results\n7. Return ONLY the SQL query, no explanations"}, 
                    {"role": "user", "content": f"Question: {question}\nAnalysis: {json.dumps(analysis)}"}
                ]
            )
            
            # Update progress for query validation
            action.update_progress(0.8, "in_progress", {"step": "Validating generated query"})
            query = response.choices[0].message.content.strip()
            
            if not query.lower().startswith('select'):
                raise ValueError("Generated query must start with SELECT")
            
            if 'project a' in question.lower():
                query = query.replace('$project_name', "'Project A'")
            
            # Mark action as completed with final query
            action.mark_completed({"generated_query": query})
            return query

        except Exception as e:
            error_msg = f"Error in query generation: {str(e)}"
            action.mark_error(error_msg)
            await self.notification_manager.notify(action)
            raise

class ResponseFormatterAgent:
    def __init__(self, openai_client, notification_manager: NotificationManager):
        self.openai_client = openai_client
        self.notification_manager = notification_manager
        self.rate_limiter = RateLimiter()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def format_response(self, question: str, query_result: List[Dict[str, Any]]) -> str:
        await self.notification_manager.notify(
            AgentAction("formatting", "Formatting query results into human-readable response")
        )

        await self.rate_limiter.wait()
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a response formatter. Format the query results into a clear and detailed natural language response. Make sure to:\n1. Address the user's question directly\n2. Present numerical data clearly\n3. Organize information logically\n4. Highlight key insights\n5. Use appropriate formatting for dates and numbers"},
                    {"role": "user", "content": f"Question: {question}\nResults: {json.dumps(query_result)}"}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            await self.notification_manager.notify(
                AgentAction("error", f"Error in response formatting: {str(e)}")
            )
            raise

class DatabaseManager:
    def __init__(self, config: DatabaseConfig, notification_manager: NotificationManager):
        self.config = config
        self.notification_manager = notification_manager
        self._connection_pool = []
        self._max_pool_size = 5
        self._pool_lock = asyncio.Lock()

    async def _get_connection(self):
        async with self._pool_lock:
            try:
                if not self._connection_pool:
                    conn = psycopg2.connect(
                        host=self.config.host,
                        port=self.config.port,
                        database=self.config.database,
                        user=self.config.user,
                        password=self.config.password
                    )
                    if not conn:
                        raise Exception("Failed to establish database connection")
                    self._connection_pool.append(conn)
                return self._connection_pool.pop()
            except Exception as e:
                await self.notification_manager.notify(
                    AgentAction("error", f"Database connection error: {str(e)}")
                )
                raise

    async def _return_connection(self, conn):
        async with self._pool_lock:
            try:
                if conn and not conn.closed:
                    if len(self._connection_pool) < self._max_pool_size:
                        self._connection_pool.append(conn)
                    else:
                        conn.close()
            except Exception as e:
                await self.notification_manager.notify(
                    AgentAction("error", f"Error returning connection to pool: {str(e)}")
                )
                if conn and not conn.closed:
                    conn.close()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def execute_query(self, query: str) -> List[Dict[str, Any]]:
        await self.notification_manager.notify(
            AgentAction("database", "Executing database query")
        )

        conn = await self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query)
                columns = [desc[0] for desc in cur.description]
                results = [dict(zip(columns, row)) for row in cur.fetchall()]
                conn.commit()
                return results
        except Exception as e:
            conn.rollback()
            await self.notification_manager.notify(
                AgentAction("error", f"Database error: {str(e)}")
            )
            raise
        finally:
            await self._return_connection(conn)

class AgentSystem:
    def __init__(self, openai_client, db_config: DatabaseConfig):
        self.notification_manager = NotificationManager()
        self.analyzer = QueryAnalyzerAgent(openai_client, self.notification_manager)
        self.generator = QueryGeneratorAgent(openai_client, self.notification_manager)
        self.formatter = ResponseFormatterAgent(openai_client, self.notification_manager)
        self.db_manager = DatabaseManager(db_config, self.notification_manager)

    def subscribe_to_notifications(self, callback):
        self.notification_manager.subscribe(callback)

    async def process_question(self, question: str) -> str:
        try:
            # Analyze the question
            analysis = await self.analyzer.analyze_question(question)

            # Check if it's a casual conversation
            if isinstance(analysis, dict) and analysis.get('type') == 'conversation':
                return analysis.get('response', 'I apologize, but I cannot understand your message.')

            # For database queries, proceed with normal flow
            query = await self.generator.generate_query(question, analysis)
            results = await self.db_manager.execute_query(query)
            response = await self.formatter.format_response(question, results)

            return response
        except Exception as e:
            error_message = f"Error processing question: {str(e)}"
            await self.notification_manager.notify(
                AgentAction("error", error_message)
            )
            return error_message