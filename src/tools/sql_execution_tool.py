import sqlite3, os, json
from pydantic import BaseModel, Field
from typing import Any, Dict
from src.paths import DB_PATH
from src.paths import CHROMA_DIR
from crewai.tools import BaseTool
from pathlib import Path

db_path = os.getenv("DB_PATH")  

class SQLExecutionTool(BaseTool):
    name: str = "sql_execution_tool"
    description: str = "Execute SQL queries against the database and return results or error information"
    db_path: str = Field(default=db_path, description="Path to the SQLite database file")

    class Config:
        arbitrary_types_allowed = True

    def _run(self, query: str) -> Dict[str, Any]:
        """Execute a SQL query and return results or errors in JSON format."""

        # Check if the database file exists first
        if not os.path.exists(self.db_path):
            return {
                "success": False,
                "error_type": "ConnectionError",
                "error_message": f"Database file '{self.db_path}' does not exist."
            }

        conn = None
        try:
            # Establish connection to the SQLite database
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Try to execute the query
            cursor.execute(query)
            query_type = query.strip().upper().split()[0]

            # Handling SELECT queries
            if query_type == 'SELECT':
                rows = cursor.fetchall()
                results = [dict(row) for row in rows]
                column_names = [description[0] for description in cursor.description]
                response = {
                    "success": True,
                    "query": query,
                    "query_type": query_type,
                    "row_count": len(results),
                    "columns": column_names,
                    "data": results
                }
            else:
                # For non-SELECT queries
                conn.commit()
                rows_affected = cursor.rowcount
                response = {
                    "success": True,
                    "query": query,
                    "query_type": query_type,
                    "rows_affected": rows_affected,
                    "message": f"Query executed successfully. {rows_affected} row(s) affected."
                }

            return response

        except sqlite3.Error as e:
            error_response = {
                "success": False,
                "query": query,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "error_code": getattr(e, 'sqlite_errorcode', None),
                "error_name": getattr(e, 'sqlite_errorname', None)
            }
            return error_response

        except Exception as e:
            error_response = {
                "success": False,
                "query": query,
                "error_type": type(e).__name__,
                "error_message": str(e)
            }
            return error_response

        finally:
            if conn:
                conn.close()
