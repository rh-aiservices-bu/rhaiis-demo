#!/usr/bin/env python3
"""
Database Tools for Red Hat AI Agent Demo

This module provides database connectivity and CRM tools that replicate
the functionality from the original MCP servers.
"""

import os
import json
import psycopg2
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


class DatabaseConnection:
    """Manages PostgreSQL database connections"""
    
    def __init__(self, 
                 host: str = "localhost", 
                 port: int = 5432,
                 database: str = "claimdb", 
                 user: str = "claimdb", 
                 password: str = "claimdb"):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            return True
        except psycopg2.Error as e:
            print(f"Database connection error: {e}")
            return False
            
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute a query and return results as list of dictionaries"""
        if not self.connection:
            if not self.connect():
                return []
                
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                
                # Get column names
                columns = [desc[0] for desc in cursor.description]
                
                # Fetch all rows and convert to dictionaries
                rows = cursor.fetchall()
                results = []
                for row in rows:
                    row_dict = dict(zip(columns, row))
                    # Convert datetime objects to strings for JSON serialization
                    for key, value in row_dict.items():
                        if hasattr(value, 'isoformat'):
                            row_dict[key] = value.isoformat()
                    results.append(row_dict)
                    
                return results
                
        except psycopg2.Error as e:
            print(f"Query execution error: {e}")
            return []


class CRMTools:
    """Provides CRM-related database tools"""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
        
    def get_opportunities(self, account_id: Optional[str] = None) -> str:
        """
        Get active opportunities from the CRM system.
        
        Args:
            account_id: Optional account ID to filter by
            
        Returns:
            JSON string containing opportunity data
        """
        try:
            if account_id:
                query = """
                    SELECT 
                        opportunities.id AS opportunity_id,
                        opportunities.status,
                        opportunities.account_id,
                        accounts.name AS account_name,
                        opportunity_items.id AS item_id,
                        opportunity_items.description,
                        opportunity_items.amount,
                        opportunity_items.year
                    FROM 
                        opportunities
                    LEFT JOIN 
                        opportunity_items 
                        ON opportunities.id = opportunity_items.opportunityid
                    LEFT JOIN
                        accounts
                        ON opportunities.account_id = accounts.id
                    WHERE 
                        opportunities.status = 'active'
                        AND opportunities.account_id = %s
                    ORDER BY opportunities.id, opportunity_items.id;
                """
                results = self.db.execute_query(query, (account_id,))
            else:
                query = """
                    SELECT 
                        opportunities.id AS opportunity_id,
                        opportunities.status,
                        opportunities.account_id,
                        accounts.name AS account_name,
                        opportunity_items.id AS item_id,
                        opportunity_items.description,
                        opportunity_items.amount,
                        opportunity_items.year
                    FROM 
                        opportunities
                    LEFT JOIN 
                        opportunity_items 
                        ON opportunities.id = opportunity_items.opportunityid
                    LEFT JOIN
                        accounts
                        ON opportunities.account_id = accounts.id
                    WHERE 
                        opportunities.status = 'active'
                    ORDER BY opportunities.id, opportunity_items.id;
                """
                results = self.db.execute_query(query)
                
            if not results:
                return "No active opportunities found."
                
            # Group by opportunity
            opportunities = {}
            for row in results:
                opp_id = row['opportunity_id']
                if opp_id not in opportunities:
                    opportunities[opp_id] = {
                        'opportunity_id': opp_id,
                        'status': row['status'],
                        'account_id': row['account_id'],
                        'account_name': row['account_name'],
                        'items': []
                    }
                
                if row['item_id']:
                    opportunities[opp_id]['items'].append({
                        'item_id': row['item_id'],
                        'description': row['description'],
                        'amount': float(row['amount']) if row['amount'] else 0,
                        'year': row['year']
                    })
                    
            return json.dumps(list(opportunities.values()), indent=2)
            
        except Exception as e:
            return f"Error fetching opportunities: {str(e)}"
            
    def get_support_cases(self, account_id: str = "1") -> str:
        """
        Get support cases for an account.
        
        Args:
            account_id: Account ID to get cases for (defaults to "1")
            
        Returns:
            JSON string containing support case data
        """
        try:
            query = """
                SELECT 
                    support_cases.id AS case_id,
                    support_cases.subject,
                    support_cases.description,
                    support_cases.status,
                    support_cases.severity,
                    support_cases.created_at,
                    accounts.name AS account_name
                FROM 
                    support_cases
                LEFT JOIN 
                    accounts 
                    ON support_cases.account_id = accounts.id
                WHERE 
                    support_cases.account_id = %s
                ORDER BY 
                    support_cases.created_at DESC;
            """
            
            results = self.db.execute_query(query, (account_id,))
            
            if not results:
                return f"No support cases found for account {account_id}."
                
            return json.dumps(results, indent=2)
            
        except Exception as e:
            return f"Error fetching support cases: {str(e)}"
            
    def get_account_info(self, account_id: str = "1") -> str:
        """
        Get account information.
        
        Args:
            account_id: Account ID to get info for
            
        Returns:
            JSON string containing account information
        """
        try:
            query = """
                SELECT 
                    accounts.id,
                    accounts.name,
                    COUNT(DISTINCT opportunities.id) as total_opportunities,
                    COUNT(DISTINCT CASE WHEN opportunities.status = 'active' THEN opportunities.id END) as active_opportunities,
                    COUNT(DISTINCT support_cases.id) as total_support_cases,
                    COUNT(DISTINCT CASE WHEN support_cases.status = 'open' THEN support_cases.id END) as open_cases,
                    COUNT(DISTINCT CASE WHEN support_cases.severity = 'Critical' THEN support_cases.id END) as critical_cases
                FROM 
                    accounts
                LEFT JOIN 
                    opportunities ON accounts.id = opportunities.account_id
                LEFT JOIN 
                    support_cases ON accounts.id = support_cases.account_id
                WHERE 
                    accounts.id = %s
                GROUP BY 
                    accounts.id, accounts.name;
            """
            
            results = self.db.execute_query(query, (account_id,))
            
            if not results:
                return f"No account found with ID {account_id}."
                
            return json.dumps(results[0], indent=2)
            
        except Exception as e:
            return f"Error fetching account info: {str(e)}"
            
    def analyze_account_health(self, account_id: str = "1") -> str:
        """
        Analyze account health based on support cases and opportunities.
        
        Args:
            account_id: Account ID to analyze
            
        Returns:
            String containing account health analysis
        """
        try:
            # Get recent support cases
            recent_cases_query = """
                SELECT 
                    severity,
                    status,
                    subject,
                    created_at
                FROM 
                    support_cases
                WHERE 
                    account_id = %s
                    AND created_at >= NOW() - INTERVAL '90 days'
                ORDER BY 
                    created_at DESC;
            """
            
            recent_cases = self.db.execute_query(recent_cases_query, (account_id,))
            
            # Analyze cases
            open_critical = len([c for c in recent_cases if c['status'] == 'open' and c['severity'] == 'Critical'])
            open_high = len([c for c in recent_cases if c['status'] == 'open' and c['severity'] == 'High'])
            total_open = len([c for c in recent_cases if c['status'] == 'open'])
            total_recent = len(recent_cases)
            
            # Determine health status
            if open_critical > 0:
                health_status = "UNHAPPY - Critical issues need immediate attention"
            elif open_high > 1:
                health_status = "AT RISK - Multiple high-severity issues open"
            elif total_open > 3:
                health_status = "CONCERNING - High volume of open cases"
            elif total_recent == 0:
                health_status = "EXCELLENT - No recent support cases"
            else:
                health_status = "GOOD - Normal support activity"
                
            analysis = {
                "account_id": account_id,
                "health_status": health_status,
                "metrics": {
                    "open_critical_cases": open_critical,
                    "open_high_cases": open_high,
                    "total_open_cases": total_open,
                    "recent_cases_90_days": total_recent
                },
                "recent_cases": recent_cases[:5]  # Last 5 cases
            }
            
            return json.dumps(analysis, indent=2)
            
        except Exception as e:
            return f"Error analyzing account health: {str(e)}"


def create_crm_tools(db_connection: DatabaseConnection) -> List:
    """
    Create and return a list of CRM tools for the agent.
    
    Args:
        db_connection: Database connection instance
        
    Returns:
        List of Tool instances
    """
    from agent import Tool
    
    crm = CRMTools(db_connection)
    
    tools = [
        Tool(
            name="get_opportunities",
            description="Get active opportunities from the CRM system. Optionally filter by account_id.",
            parameters={
                "type": "object",
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "Optional account ID to filter opportunities"
                    }
                }
            },
            function=crm.get_opportunities
        ),
        
        Tool(
            name="get_support_cases",
            description="Get support cases for an account. Defaults to account ID '1'.",
            parameters={
                "type": "object",
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "Account ID to get support cases for",
                        "default": "1"
                    }
                }
            },
            function=crm.get_support_cases
        ),
        
        Tool(
            name="get_account_info",
            description="Get comprehensive account information including opportunity and case counts.",
            parameters={
                "type": "object",
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "Account ID to get information for",
                        "default": "1"
                    }
                }
            },
            function=crm.get_account_info
        ),
        
        Tool(
            name="analyze_account_health",
            description="Analyze account health status based on support case activity and severity.",
            parameters={
                "type": "object",
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "Account ID to analyze",
                        "default": "1"
                    }
                }
            },
            function=crm.analyze_account_health
        )
    ]
    
    return tools
