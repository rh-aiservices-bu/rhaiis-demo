#!/bin/bash

echo "[INFO] Setting up PostgreSQL database for CRM demo..."

# Stop any existing PostgreSQL container
sudo podman stop crm-postgres 2>/dev/null || true
sudo podman rm crm-postgres 2>/dev/null || true

# Start PostgreSQL container
echo "[INFO] Starting PostgreSQL container..."
sudo podman run -d \
  --name crm-postgres \
  -e POSTGRES_DB=crm_db \
  -e POSTGRES_USER=crm_user \
  -e POSTGRES_PASSWORD=crm_pass \
  -p 5432:5432 \
  docker.io/library/postgres:15

# Wait for PostgreSQL to be ready
echo "[INFO] Waiting for PostgreSQL to be ready..."
sleep 10

# Create sample data
echo "[INFO] Creating sample CRM data..."
sudo podman exec -i crm-postgres psql -U crm_user -d crm_db << 'EOF'
-- Create accounts table
CREATE TABLE IF NOT EXISTS accounts (
    account_id VARCHAR(50) PRIMARY KEY,
    company_name VARCHAR(200),
    industry VARCHAR(100),
    annual_revenue BIGINT,
    employee_count INTEGER,
    created_date DATE
);

-- Create opportunities table
CREATE TABLE IF NOT EXISTS opportunities (
    opportunity_id VARCHAR(50) PRIMARY KEY,
    account_id VARCHAR(50),
    opportunity_name VARCHAR(200),
    amount DECIMAL(15,2),
    stage VARCHAR(50),
    status VARCHAR(50),
    close_date DATE,
    probability INTEGER,
    created_date DATE,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);

-- Create support cases table
CREATE TABLE IF NOT EXISTS support_cases (
    case_id VARCHAR(50) PRIMARY KEY,
    account_id VARCHAR(50),
    subject VARCHAR(300),
    description TEXT,
    priority VARCHAR(20),
    status VARCHAR(50),
    created_date DATE,
    resolved_date DATE,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);

-- Create account health table
CREATE TABLE IF NOT EXISTS account_health (
    account_id VARCHAR(50) PRIMARY KEY,
    health_score INTEGER,
    churn_risk VARCHAR(20),
    satisfaction_score DECIMAL(3,2),
    last_activity DATE,
    renewal_date DATE,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);

-- Insert sample accounts
INSERT INTO accounts (account_id, company_name, industry, annual_revenue, employee_count, created_date) VALUES
('ACC001', 'TechCorp Industries', 'Technology', 50000000, 2500, '2022-01-15'),
('ACC002', 'Global Manufacturing Inc', 'Manufacturing', 120000000, 8000, '2021-06-20'),
('ACC003', 'FinanceFirst Solutions', 'Financial Services', 75000000, 1200, '2023-03-10'),
('ACC004', 'HealthcarePlus Systems', 'Healthcare', 200000000, 15000, '2020-11-05'),
('ACC005', 'RetailMax Corp', 'Retail', 90000000, 5000, '2022-08-12');

-- Insert sample opportunities
INSERT INTO opportunities (opportunity_id, account_id, opportunity_name, amount, stage, status, close_date, probability, created_date) VALUES
('OPP001', 'ACC001', 'Cloud Migration Project', 750000.00, 'Proposal', 'Open', '2025-02-28', 75, '2024-12-01'),
('OPP002', 'ACC002', 'ERP System Upgrade', 1200000.00, 'Negotiation', 'Open', '2025-03-15', 85, '2024-11-15'),
('OPP003', 'ACC003', 'Security Enhancement', 300000.00, 'Closed Won', 'Won', '2024-12-20', 100, '2024-10-01'),
('OPP004', 'ACC004', 'Data Analytics Platform', 950000.00, 'Discovery', 'Open', '2025-04-30', 40, '2025-01-10'),
('OPP005', 'ACC005', 'Mobile App Development', 450000.00, 'Qualification', 'Open', '2025-05-15', 30, '2025-01-20');

-- Insert sample support cases
INSERT INTO support_cases (case_id, account_id, subject, description, priority, status, created_date, resolved_date) VALUES
('CASE001', 'ACC001', 'Login Issues with Portal', 'Users unable to access customer portal', 'High', 'Resolved', '2025-01-15', '2025-01-16'),
('CASE002', 'ACC002', 'Performance Degradation', 'System running slowly during peak hours', 'Medium', 'In Progress', '2025-01-20', NULL),
('CASE003', 'ACC003', 'Data Export Error', 'Error when exporting financial reports', 'Low', 'Open', '2025-01-25', NULL),
('CASE004', 'ACC004', 'Integration Failure', 'Third-party API integration not working', 'Critical', 'In Progress', '2025-01-18', NULL),
('CASE005', 'ACC005', 'Feature Request', 'Request for new dashboard widgets', 'Low', 'Open', '2025-01-22', NULL);

-- Insert sample account health data
INSERT INTO account_health (account_id, health_score, churn_risk, satisfaction_score, last_activity, renewal_date) VALUES
('ACC001', 85, 'Low', 4.2, '2025-01-30', '2025-12-31'),
('ACC002', 92, 'Low', 4.7, '2025-01-29', '2025-11-15'),
('ACC003', 78, 'Medium', 3.8, '2025-01-25', '2025-09-30'),
('ACC004', 65, 'High', 3.2, '2025-01-20', '2025-08-20'),
('ACC005', 88, 'Low', 4.5, '2025-01-28', '2026-02-28');

-- Create indexes for better performance
CREATE INDEX idx_opportunities_account_id ON opportunities(account_id);
CREATE INDEX idx_support_cases_account_id ON support_cases(account_id);
CREATE INDEX idx_opportunities_status ON opportunities(status);
CREATE INDEX idx_support_cases_priority ON support_cases(priority);

EOF

echo "[SUCCESS] PostgreSQL database setup complete!"
echo "[INFO] Database connection details:"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  Database: crm_db"
echo "  Username: crm_user"
echo "  Password: crm_pass"
