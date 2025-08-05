#!/bin/bash

# Script to setup the PostgreSQL database for the demo

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if container already exists and remove it
if podman ps -a --format "{{.Names}}" | grep -q "^postgres-demo$"; then
    log_info "Removing existing postgres-demo container..."
    podman stop postgres-demo 2>/dev/null || true
    podman rm postgres-demo 2>/dev/null || true
fi

# Create the SQL import file if it doesn't exist
if [ ! -f "./demo-source/local/import.sql" ]; then
    log_error "Database import file not found at ./demo-source/local/import.sql"
    log_info "Creating minimal database schema..."
    
    mkdir -p ./local
    cat > ./local/import.sql << 'EOF'
\c claimdb;

-- Create Accounts Table
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Create Opportunities Table
CREATE TABLE opportunities (
    id SERIAL PRIMARY KEY,
    status VARCHAR(50),
    account_id INTEGER REFERENCES accounts(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Opportunity Items Table
CREATE TABLE opportunity_items (
    id SERIAL PRIMARY KEY,
    opportunityid INTEGER REFERENCES opportunities(id),
    description TEXT,
    amount DECIMAL(10, 2),
    year INTEGER
);

-- Create Support Cases Table
CREATE TABLE support_cases (
    id SERIAL PRIMARY KEY,
    subject TEXT NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL,
    severity VARCHAR(20) CHECK (severity IN ('Low', 'Medium', 'High', 'Critical')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    account_id INTEGER NOT NULL REFERENCES accounts(id)
);

-- Insert Sample Data
INSERT INTO accounts (name) VALUES 
('Acme Corp'), 
('Globex Inc'), 
('Soylent Corp');

INSERT INTO opportunities (status, account_id) VALUES 
('active', 1),
('active', 2),
('closed', 3);

INSERT INTO opportunity_items (opportunityid, description, amount, year) VALUES 
(1, 'Subscription renewal - Tier A', 15000.00, 2025),
(1, 'Upsell - Cloud package', 5000.00, 2025),
(2, 'Enterprise license renewal', 25000.00, 2025),
(3, 'Legacy support', 8000.00, 2024);

INSERT INTO support_cases (subject, description, status, severity, account_id) VALUES
('Login failure', 'Customer unable to log in with correct credentials.', 'open', 'High', 1),
('Slow dashboard', 'Performance issues loading analytics dashboard.', 'in progress', 'Critical', 1),
('Payment not processed', 'Invoice payment failed on retry.', 'open', 'Medium', 2),
('Email delivery issue', 'Confirmation emails not reaching clients.', 'closed', 'High', 2),
('API outage', 'Integration API returns 500 error intermittently.', 'open', 'Critical', 3),
('Feature request: Dark mode', 'Request to implement dark mode UI.', 'closed', 'Low', 1);
EOF
else
    log_info "Using existing database import file"
fi

# Determine which import file to use
if [ -f "./demo-source/local/import.sql" ]; then
    IMPORT_FILE="./demo-source/local/import.sql"
else
    IMPORT_FILE="./local/import.sql"
fi

# Start PostgreSQL container
log_info "Starting PostgreSQL container..."
podman run --name postgres-demo \
  -e POSTGRES_USER=claimdb \
  -e POSTGRES_PASSWORD=claimdb \
  -e POSTGRES_DB=claimdb \
  -v "$IMPORT_FILE:/docker-entrypoint-initdb.d/import.sql:ro" \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  -d postgres:13

log_success "PostgreSQL container started"
