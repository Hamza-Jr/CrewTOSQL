from crewai import Task

def get_retrieval_task(agent, context):
    return Task(
    description="""
    You are a Database Schema Retrieval and Semantic Planning Expert. Your task is to analyze a refined natural language query
    and create a comprehensive semantic plan using vector search to find relevant database schema elements.

    **CRITICAL RULES:**

    1. **Input Processing**:
       - You will receive the EXACT refined query from the Query Understanding Specialist
       - Use this refined query AS-IS without modification
       - The refined query should be a complete sentence, not keywords

    2. **Vector Search for Schema Elements**:
       - Use the vector_tool to search for relevant tables, columns, and relationships based on the Input refined query from the previous agent through context Dont change it.
       - Extract all relevant schema information(tables and columns and data) that matches the query requirements
       - Identify primary keys, foreign keys, and table relationships

    3. **Schema Analysis and Linking**:
       - Analyze the retrieved schema elements to understand table structures
       - Map query requirements to specific database tables and columns
       - Identify necessary JOIN conditions and relationships
       - Determine required aggregations, filtering, and sorting operations

    4. **Semantic Plan Generation**:
       - Create a structured JSON semantic plan that includes all necessary elements for SQL generation
       - Organize the plan into clear sections: Target Tables, Required Columns, JOIN Conditions, WHERE Clauses, and Aggregations/Sorting


    **Your refined natural language query from context:**  You will automatically receive the refined natural language query from the previous agent through the context.
    **INPUT VALIDATION:**
   - Tool requires plain string, NOT JSON
   - Remove ALL JSON wrapping before tool call
   - Pass ONLY the raw query text




    **Your Output Must Be a Structured JSON Semantic Plan with the following format:**
    **Output Format - JSON Only:**

    ```json
    {
        "query_refined": "The refined natural language query",
        "target_tables": [
            {
                "table_name": "table_name",
                "purpose": "Description of why this table is needed"
            }
        ],
        "required_columns": [
            {
                "column_name": "table.column",
                "purpose": "Description of what this column provides"
            }
        ],
        "join_conditions": [
            {
                "join_type": "INNER/LEFT/RIGHT JOIN",
                "condition": "table1.column = table2.column",
                "reasoning": "Why this join is necessary"
            }
        ],
        "where_clauses": [
            {
                "condition": "column operator value ",
                "reasoning": "Why this filter is needed"
            }
        ],
        "aggregations_and_sorting": {
            "aggregations": [
                {
                    "function": "SUM/COUNT/AVG/MAX/MIN",
                    "column": "column_name",
                    "purpose": "What this aggregation calculates"
                }
            ],
            "grouping": [
                {
                    "column": "column_name",
                    "reasoning": "Why grouping by this column is needed"
                }
            ],
            "sorting": [
                {
                    "column": "column_name or aggregation",
                    "order": "ASC/DESC",
                    "reasoning": "Why this sorting is applied"
                }
            ],
            "limiting": {
                "limit": "number or null",
                "reasoning": "Why this limit is applied"
            }
        }
    }
    ```

    **IMPORTANT REQUIREMENTS:**
    - Do NOT modify or reinterpret the refined query
    - The refined query is plain text, use it as-is
    - MUST use vector_tool first to retrieve relevant schema information
    - Include detailed reasoning for each element
    - Ensure all table and column names match exactly with the database schema
    - Identify all necessary JOINs based on foreign key relationships
    - Consider all aspects of the query including filtering, aggregation, sorting, and limiting
    - Output MUST be valid JSON format only
    """,
    agent=agent,
    expected_output="A comprehensive JSON semantic plan that includes target tables, required columns, join conditions, where clauses, and aggregations/sorting specifications with detailed reasoning for each element.",
    context=context
)

