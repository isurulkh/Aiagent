-- Sample data for project management system

-- Insert sample projects
INSERT INTO projects (project_name, start_date, end_date, budget, status) VALUES
('Project A', '2023-01-01', '2023-12-31', 500000.00, 'active'),
('Project B', '2023-03-15', '2024-03-14', 750000.00, 'active'),
('Project C', '2023-06-01', '2024-05-31', 300000.00, 'active'),
('Project D', '2023-02-01', '2023-11-30', 250000.00, 'completed');

-- Insert sample employees
INSERT INTO employees (first_name, last_name, email, hire_date, role) VALUES
('John', 'Smith', 'john.smith@company.com', '2022-01-15', 'Senior Developer'),
('Emma', 'Johnson', 'emma.johnson@company.com', '2022-03-01', 'Project Manager'),
('Michael', 'Brown', 'michael.brown@company.com', '2022-02-15', 'Business Analyst'),
('Sarah', 'Davis', 'sarah.davis@company.com', '2022-04-01', 'Developer'),
('James', 'Wilson', 'james.wilson@company.com', '2022-05-15', 'Designer'),
('Lisa', 'Anderson', 'lisa.anderson@company.com', '2022-06-01', 'Developer'),
('David', 'Martinez', 'david.martinez@company.com', '2022-07-15', 'QA Engineer'),
('Emily', 'Taylor', 'emily.taylor@company.com', '2022-08-01', 'Business Analyst');

-- Insert sample tasks
INSERT INTO tasks (project_id, task_name, description, start_date, due_date, completion_date, status, priority) VALUES
(1, 'Requirements Analysis', 'Gather and analyze project requirements', '2023-01-05', '2023-01-20', '2023-01-19', 'completed', 'high'),
(1, 'Database Design', 'Design database schema and relationships', '2023-01-21', '2023-02-05', '2023-02-03', 'completed', 'high'),
(1, 'Frontend Development', 'Develop user interface components', '2023-02-06', '2023-03-15', '2023-03-10', 'completed', 'medium'),
(2, 'Market Research', 'Conduct market analysis and competitor research', '2023-03-20', '2023-04-10', '2023-04-08', 'completed', 'high'),
(2, 'Product Design', 'Create product design specifications', '2023-04-11', '2023-05-15', null, 'in_progress', 'high'),
(3, 'System Architecture', 'Design system architecture and components', '2023-06-05', '2023-06-30', null, 'in_progress', 'high'),
(3, 'API Development', 'Develop and document APIs', '2023-07-01', '2023-08-15', null, 'pending', 'medium');

-- Insert sample project assignments
INSERT INTO project_assignments (project_id, employee_id, start_date, end_date, role, hours_allocated) VALUES
(1, 1, '2023-01-05', '2023-12-31', 'Lead Developer', 160),
(1, 4, '2023-01-05', '2023-12-31', 'Developer', 160),
(1, 6, '2023-02-01', '2023-12-31', 'Developer', 120),
(2, 2, '2023-03-15', '2024-03-14', 'Project Manager', 160),
(2, 3, '2023-03-15', '2024-03-14', 'Business Analyst', 120),
(2, 5, '2023-04-01', '2024-03-14', 'Designer', 140),
(3, 7, '2023-06-01', '2024-05-31', 'QA Lead', 160),
(3, 8, '2023-06-01', '2024-05-31', 'Business Analyst', 120);

-- Insert sample task assignments
INSERT INTO task_assignments (task_id, employee_id, assigned_date) VALUES
(1, 3, '2023-01-05'),
(2, 1, '2023-01-21'),
(3, 4, '2023-02-06'),
(3, 6, '2023-02-06'),
(4, 3, '2023-03-20'),
(5, 5, '2023-04-11'),
(6, 1, '2023-06-05'),
(7, 4, '2023-07-01');