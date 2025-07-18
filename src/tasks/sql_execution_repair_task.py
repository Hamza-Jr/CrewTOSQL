from crewai import Task

def get_sql_execution_repair_task(agent, context):
    return Task(
    description="""
    Execute the provided SQL query and handle any errors through systematic repair attempts:

    **Primary Execution Process:**
    1. Execute the SQL query using SQLExecutionTool1
    2. If successful (success=True), clean the query formatting and return the results to the user
    3. If failed (success=False), begin automatic repair process

    **3-Attempt Repair Strategy:**

    **ATTEMPT 1 - Schema Correction:**
    - Use SQLErrorRetrievalTool to retrieve similar table/column names via vector search
    - Focus on "no such table" and "no such column" errors
    - Apply best matches from relevant_info (exact name corrections)
    - Re-execute with corrected schema names

    **ATTEMPT 2 - Syntax & Logic Fixes:**
    - Fix common SQL syntax issues (missing quotes, incorrect operators)
    - Resolve ambiguous column references by adding table aliases/qualifiers
    - Correct JOIN syntax and WHERE clause logic
    - Handle data type mismatches and format issues
    - Re-execute with syntax corrections

    **ATTEMPT 3 - Query Restructuring:**
    - Simplify complex operations (break down nested queries)
    - Convert JOINs to subqueries or vice versa
    - Use alternative SQL approaches for the same logical intent
    - Remove problematic clauses and rebuild step by step
    - Re-execute with restructured query

    **If All Repairs Fail:**
    Provide a friendly, non-technical explanation such as:
    "I apologize, but I wasn't able to retrieve the information you requested. The query encountered some technical issues that I couldn't automatically resolve. Could you please rephrase your question or provide more details about what specific information you're looking for?"

    **Important Notes:**
    - Track attempt number and previous errors to avoid repeated mistakes
    - Use vector search results intelligently - prioritize exact matches and high-relevance suggestions
    - Maintain the original query intent while making corrections
    - Always re-execute after each repair attempt
    - Keep repair explanations internal - only show friendly messages to users when repairs fail
    - **Clean the final output**: Remove newlines (\n) and extra whitespace from the query string in successful results
    - Format the query as a single clean line for better readability
    """,
    agent=agent,
    context=context,  # Takes SQL query from agent 3
    expected_output="""
    Either:
    1. **Successful Results**: JSON format with query results including row_count, columns, and data array
    2. **Friendly Error Message**: User-friendly explanation when all 3 repair attempts fail, without technical details

    Format for successful results:
    {
        "success": True,
        "query": ""corrected_query_if_modified or the orginal if not modified",
        "row_count": X,
        "columns": ["col1", "col2", ...],
        "data": [{"col1": "value1", "col2": "value2"}, ...]
    }

    Format for friendly error:
    "I apologize, but I wasn't able to retrieve the information you requested. [Helpful suggestion for user]"
    """
)