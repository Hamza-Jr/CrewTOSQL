from crewai import Task

def get_sql_generation_task(agent, context):
    return Task(
    description="""
    You are a SQL Generation Expert. Your task is to convert the provided JSON input
    which includes a refined natural language query and a comprehensive semantic plan
    into a syntactically correct and optimized SQL query.


1. **Analyze Input Components**:
       - Review the refined natural language query for intent understanding
       - Parse the JSON semantic plan for all required elements
       - Validate that all table and column references are properly specified


    **Your Process:**

    1. **Parse the Input JSON** to extract:
       - the query intent from the refined natural language query ("query_refined")
       - Target tables with their purposes
       - Required columns with their purposes
       - Join conditions and reasoning
       - Where clauses and reasoning
       - Aggregations, grouping, sorting, and limiting details

    2. **SQL Structure Planning**:
       - Determine the optimal query structure (simple SELECT, subqueries, CTEs, etc.)
       - Plan JOIN order for optimal performance based on the semantic plan
       - Identify if temporary tables or window functions would improve readability
       - Validate all table and column references from the JSON structure


    3. **Query Construction**:
       - Build SELECT clause using the "required_columns" from JSON
       - Construct proper FROM clause with primary table from "target_tables"
       - Add all necessary JOIN clauses using "join_conditions" specifications
       - Include WHERE conditions using "where_clauses" details
       - Add GROUP BY clauses based on "aggregations_and_sorting.grouping"
       - Include aggregation functions from "aggregations_and_sorting.aggregations"
       - Add ORDER BY using "aggregations_and_sorting.sorting" specifications
       - Apply LIMIT using "aggregations_and_sorting.limiting" if specified

    4. **Query Optimization**:
       - Ensure JOINs use proper indexes based on the reasoning provided in JSON
       - Optimize WHERE clause order for performance
       - Use appropriate JOIN types as specified in "join_conditions"
       - Consider query execution plan efficiency

    5. **Code Quality and Formatting**:
       - Apply consistent indentation and formatting
       - Use meaningful table aliases
       - Add comments for complex logic when reasoning is provided in JSON
       - Ensure readability and maintainability

    **Input**: You will automatically receive the complete JSON output from the previous agent through the context containing:
    - "query_refined": The refined natural language query
    - "target_tables": Array of tables needed with purposes
    - "required_columns": Array of columns needed with purposes
    - "join_conditions": Array of JOIN specifications with reasoning
    - "where_clauses": Array of filter conditions with reasoning
    - "aggregations_and_sorting": Object with aggregations, grouping, sorting, and limiting details

    **SQL Generation Guidelines**:
    - Extract table and column names exactly as specified in the JSON
    - Use proper SQL formatting with consistent indentation
    - Always use table aliases for multi-table queries
    - Place JOINs in logical order following the semantic plan
    - Use explicit JOIN syntax as specified in "join_conditions"
    - Include appropriate WHERE clause ordering (most selective conditions first)
    - Use consistent naming conventions
    - Ensure proper handling of NULL values where applicable

    **Error Prevention**:
    - Verify all table and column names match the JSON specification exactly
    - Ensure JOIN conditions reference the exact relationships from "join_conditions"
    - Validate that aggregation functions match "aggregations_and_sorting.aggregations"
    - Check that GROUP BY includes columns from "aggregations_and_sorting.grouping"
    - Confirm that ORDER BY references columns from "aggregations_and_sorting.sorting"
    - Ensure LIMIT values match "aggregations_and_sorting.limiting" specifications

    **Output Requirements**:
    - Generate ONLY the SQL query
    - No explanations, no markdown formatting, no additional text
    - Just clean, executable SQL code
    - Ensure the query is syntactically correct and ready to execute

    **SQL Best Practices to Follow**:
    - Use meaningful table aliases (first letter of table names)
    - Format for readability with proper line breaks and indentation
    - Order columns logically in SELECT clause as specified in JSON
    - Use consistent capitalization for SQL keywords
    - Include appropriate semicolon at the end
    - Optimize for both performance and maintainability
    """,
    agent=agent,
    expected_output="A clean, syntactically correct, and optimized SQL query that accurately implements the JSON semantic plan and addresses the refined natural language question.",
    context=context
)

