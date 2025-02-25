-- Create tables for project management system

-- Projects table
CREATE TABLE projects (
    project_id SERIAL PRIMARY KEY,
    project_name VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    budget DECIMAL(15, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'active'
);

-- Employees table
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hire_date DATE NOT NULL,
    role VARCHAR(50) NOT NULL
);

-- Tasks table
CREATE TABLE tasks (
    task_id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(project_id),
    task_name VARCHAR(200) NOT NULL,
    description TEXT,
    start_date DATE NOT NULL,
    due_date DATE NOT NULL,
    completion_date DATE,
    status VARCHAR(20) DEFAULT 'pending',
    priority VARCHAR(20) DEFAULT 'medium'
);

-- Employee Project Assignments
CREATE TABLE project_assignments (
    assignment_id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(project_id),
    employee_id INTEGER REFERENCES employees(employee_id),
    start_date DATE NOT NULL,
    end_date DATE,
    role VARCHAR(50) NOT NULL,
    hours_allocated INTEGER NOT NULL
);

-- Task Assignments
CREATE TABLE task_assignments (
    assignment_id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(task_id),
    employee_id INTEGER REFERENCES employees(employee_id),
    assigned_date DATE NOT NULL,
    hours_spent DECIMAL(8, 2) DEFAULT 0
);

-- Performance Metrics
CREATE TABLE performance_metrics (
    metric_id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(employee_id),
    project_id INTEGER REFERENCES projects(project_id),
    evaluation_date DATE NOT NULL,
    productivity_score DECIMAL(4, 2),
    quality_score DECIMAL(4, 2),
    communication_score DECIMAL(4, 2),
    comments TEXT
);

-- Project Budgets
CREATE TABLE project_budgets (
    budget_id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(project_id),
    month DATE NOT NULL,
    planned_amount DECIMAL(15, 2) NOT NULL,
    actual_amount DECIMAL(15, 2),
    category VARCHAR(50) NOT NULL
);

-- Create indexes for better query performance
CREATE INDEX idx_project_assignments_dates ON project_assignments(start_date, end_date);
CREATE INDEX idx_task_completion ON tasks(completion_date);
CREATE INDEX idx_performance_metrics_date ON performance_metrics(evaluation_date);
CREATE INDEX idx_project_budgets_month ON project_budgets(month);