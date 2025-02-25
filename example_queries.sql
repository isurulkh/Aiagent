-- 1. Get all active projects with their total budget utilization
SELECT 
    p.project_name,
    p.budget as total_budget,
    SUM(COALESCE(pb.actual_amount, 0)) as total_spent,
    (p.budget - SUM(COALESCE(pb.actual_amount, 0))) as remaining_budget
FROM projects p
LEFT JOIN project_budgets pb ON p.project_id = pb.project_id
WHERE p.status = 'active'
GROUP BY p.project_id, p.project_name, p.budget;

-- 2. Find employees working on multiple projects
SELECT 
    e.first_name,
    e.last_name,
    COUNT(DISTINCT pa.project_id) as project_count,
    SUM(pa.hours_allocated) as total_hours_allocated
FROM employees e
JOIN project_assignments pa ON e.employee_id = pa.employee_id
WHERE pa.end_date IS NULL OR pa.end_date > CURRENT_DATE
GROUP BY e.employee_id, e.first_name, e.last_name
HAVING COUNT(DISTINCT pa.project_id) > 1;

-- 3. Calculate project completion percentage
SELECT 
    p.project_name,
    COUNT(t.task_id) as total_tasks,
    COUNT(t.completion_date) as completed_tasks,
    ROUND(COUNT(t.completion_date)::DECIMAL / COUNT(t.task_id) * 100, 2) as completion_percentage
FROM projects p
LEFT JOIN tasks t ON p.project_id = t.project_id
GROUP BY p.project_id, p.project_name;

-- 4. Get employee performance metrics by project
SELECT 
    e.first_name,
    e.last_name,
    p.project_name,
    ROUND(AVG(pm.productivity_score), 2) as avg_productivity,
    ROUND(AVG(pm.quality_score), 2) as avg_quality,
    ROUND(AVG(pm.communication_score), 2) as avg_communication
FROM employees e
JOIN performance_metrics pm ON e.employee_id = pm.employee_id
JOIN projects p ON pm.project_id = p.project_id
GROUP BY e.employee_id, e.first_name, e.last_name, p.project_id, p.project_name;

-- 5. Find overdue tasks and assigned employees
SELECT 
    t.task_name,
    p.project_name,
    t.due_date,
    CURRENT_DATE - t.due_date as days_overdue,
    e.first_name || ' ' || e.last_name as assigned_employee
FROM tasks t
JOIN projects p ON t.project_id = p.project_id
JOIN task_assignments ta ON t.task_id = ta.task_id
JOIN employees e ON ta.employee_id = e.employee_id
WHERE t.completion_date IS NULL 
    AND t.due_date < CURRENT_DATE
ORDER BY days_overdue DESC;

-- 6. Calculate monthly project budget variance
SELECT 
    p.project_name,
    pb.month,
    pb.planned_amount,
    pb.actual_amount,
    pb.actual_amount - pb.planned_amount as variance,
    ROUND((pb.actual_amount - pb.planned_amount) / pb.planned_amount * 100, 2) as variance_percentage
FROM project_budgets pb
JOIN projects p ON pb.project_id = p.project_id
WHERE pb.actual_amount IS NOT NULL
ORDER BY pb.month, variance_percentage DESC;

-- 7. Get employee workload distribution
SELECT 
    e.first_name || ' ' || e.last_name as employee_name,
    COUNT(DISTINCT t.task_id) as active_tasks,
    SUM(ta.hours_spent) as total_hours_spent,
    STRING_AGG(DISTINCT p.project_name, ', ') as assigned_projects
FROM employees e
LEFT JOIN task_assignments ta ON e.employee_id = ta.employee_id
LEFT JOIN tasks t ON ta.task_id = t.task_id AND t.status != 'completed'
LEFT JOIN project_assignments pa ON e.employee_id = pa.employee_id
LEFT JOIN projects p ON pa.project_id = p.project_id
GROUP BY e.employee_id, e.first_name, e.last_name;