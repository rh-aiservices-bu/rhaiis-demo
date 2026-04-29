import psycopg2
from typing import List, Dict, Any

class DatabaseTools:
    def __init__(self):
        # Connection details would ideally be loaded from environment variables or configuration files
        self.conn = psycopg2.connect(
            dbname='crm_db',
            user='crm_user',
            password='crm_pass',
            host='localhost',
            port=5432
        )

    def _execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        with self.conn.cursor() as cursor:
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return results

    def get_opportunities(self, account_id: str = None, status: str = None) -> str:
        query = "SELECT * FROM opportunities WHERE 1=1"
        params = []
        if account_id:
            query += " AND account_id = %s"
            params.append(account_id)
        if status:
            query += " AND status = %s"
            params.append(status)
        opportunities = self._execute_query(query, tuple(params))
        return str(opportunities)

    def get_support_cases(self, account_id: str = None, priority: str = None) -> str:
        query = "SELECT * FROM support_cases WHERE 1=1"
        params = []
        if account_id:
            query += " AND account_id = %s"
            params.append(account_id)
        if priority:
            query += " AND priority = %s"
            params.append(priority)
        cases = self._execute_query(query, tuple(params))
        return str(cases)

    def get_accounts(self, account_id: str = None) -> str:
        query = "SELECT * FROM accounts WHERE 1=1"
        params = []
        if account_id:
            query += " AND account_id = %s"
            params.append(account_id)
        accounts = self._execute_query(query, tuple(params))
        return str(accounts)

    def analyze_account_health(self, account_id: str) -> str:
        # Simple mock implementation - a real implementation would use complex logic
        query = "SELECT * FROM account_health WHERE account_id = %s"
        health = self._execute_query(query, (account_id,))
        return str(health)
