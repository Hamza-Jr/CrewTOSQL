import sqlite3, os, json
from pydantic import BaseModel, Field
from typing import Any, Dict
from src.paths import DB_PATH
from crewai.tools import BaseTool






class SQLErrorRetrievalTool(BaseTool):
    name: str = "sql_error_retrieval_tool"
    description: str = "Retrieve relevant schema fixes from vector store based on SQL execution errors"
    vectorstore: Any = Field(description="ChromaDB vector store instance")

    class Config:
        arbitrary_types_allowed = True

    def _run(self, error_result: Dict[str, Any]) -> Dict[str, Any]:
        if error_result.get("success", True):
            return {"message": "No error to process", "relevant_info": []}

        error_message = error_result.get("error_message", "")
        query = error_result.get("query", "")
        error_type = error_result.get("error_type", "")

        search_targets = []
        filtered_docs = []

        # 1. No such column
        if "no such column" in error_message.lower():
            column = self._extract_column_name(error_message)
            search_term = column.split(".")[-1]  # Remove alias
            search_targets.append(("column", search_term))

        # 2. No such table
        elif "no such table" in error_message.lower():
            table = self._extract_table_name(error_message)
            search_targets.append(("table", table))

        # 3. Bad value in WHERE clause
        elif "where" in query.lower():
            bad_column, bad_value = self._extract_column_value_in_where(query)
            if bad_column and bad_value:
                search_targets.append(("value", bad_column))

        # Perform targeted vector search
        for target_type, target_name in search_targets:
            try:
                docs = self.vectorstore.similarity_search(target_name, k=3)
                for doc in docs:
                    table_name = doc.metadata.get("table", "").lower()

                    # Handle column errors
                    if target_type == "column":
                        matching_lines = self._extract_matching_columns(doc.page_content, target_name)
                        if matching_lines:
                            filtered_docs.append({
                                "type": "column",
                                "search": target_name,
                                "table": table_name,
                                "columns": matching_lines
                            })

                    # Handle table errors
                    elif target_type == "table":
                        if target_name in table_name:
                            filtered_docs.append({
                                "type": "table",
                                "search": target_name,
                                "table": table_name,
                                "table_info": f"Table: {table_name}"
                            })

                    # Handle value-based condition errors
                    elif target_type == "value":
                        values = self._extract_sample_values(doc.page_content, target_name)
                        if values:
                            filtered_docs.append({
                                "type": "value",
                                "search": target_name,
                                "table": table_name,
                                "sample_values": values
                            })

            except Exception as e:
                print(f"Search failed for '{target_name}': {str(e)}")

        return {
            "error_type": error_type,
            "error_message": error_message,
            "query": query,
            "relevant_info": filtered_docs,
            "search_targets": search_targets
        }

    def _extract_column_name(self, msg: str) -> str:
        return msg.split(":")[-1].strip().lower()

    def _extract_table_name(self, msg: str) -> str:
        return msg.split(":")[-1].strip().lower()

    def _extract_column_value_in_where(self, query: str) -> (str, str):
        import re
        match = re.search(r"where\s+(\w+)\s*=\s*['\"]?([\w\s]+)['\"]?", query, re.IGNORECASE)
        if match:
            return match.group(1).lower(), match.group(2).lower()
        return None, None

    def _extract_matching_columns(self, content: str, column_name: str) -> list:
        lines = content.splitlines()
        return [line.strip() for line in lines if line.strip().startswith("-") and column_name in line]

    def _extract_sample_values(self, content: str, column_name: str) -> list:
        # Try to find sample values under the column name
        section_start = content.find("Sample Data")
        if section_start == -1:
            return []

        sample_block = content[section_start:]
        lines = sample_block.splitlines()

        headers = []
        data_rows = []
        for i, line in enumerate(lines):
            if i == 1:
                headers = [h.strip() for h in line.split("|")]
            elif i > 2:
                data_rows.append([cell.strip() for cell in line.split("|")])

        if not headers:
            return []

        try:
            idx = headers.index(column_name)
            return list({row[idx] for row in data_rows if len(row) > idx})
        except ValueError:
            return []

