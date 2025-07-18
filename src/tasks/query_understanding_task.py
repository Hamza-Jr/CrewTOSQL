from crewai import Task

def get_query_understanding_task(agent):
    return Task(
    description="""
You are an advanced question understanding specialist. Analyze this natural language question and resolve all understanding challenges to clarify the user's true intent.

Your task is to address these Natural Language Understanding challenges:

1. **Lexical Ambiguity (Polysemy)**: Identify words with multiple meanings and resolve them using context
2. **Syntactic Ambiguity**: Resolve multiple possible sentence interpretations
3. **Semantic Ambiguity**: Clarify unclear relationships and intended metrics
4. **Context-Dependent Ambiguity**: Resolve pronouns and relative references
5. **Under-specification**: Identify missing critical information
6. **Paraphrasing Variability**: Recognize different ways to express the same intent
7. **Elliptical Queries**: Complete incomplete sentences
8. **Domain-specific Vocabulary**: Handle specialized terminology
9. **User Mistakes**: Correct errors while preserving intent

User Question: "{user_query}"

**EXECUTION APPROACH:**
1. Call the vector_tool with the EXACT user query: "{user_query}" to retrieve relevant schema information
2. Use the retrieved schema information to understand what the user is really asking for
3. Identify the user's true intent behind the question
4. Clarify any ambiguous terms or concepts using the database context
5. Resolve incomplete or unclear parts of the question
6. Correct obvious errors while preserving the original meaning
7. Rewrite as a clear, complete question that expresses the user's intent in unambiguous natural language terms

**CRITICAL CONSTRAINTS:**
- DO use the vector_tool to understand the database structure
- DO use schema information to clarify the user's intent
- PRESERVE all specific data fields and attributes mentioned by the user (e.g., "line 1 and line 2", "id", "first name", "middle name", etc.)
- DO NOT remove or simplify the user's specific data requirements
- In the final refined question, do NOT reference specific database tables, columns, or schema elements
- Do NOT generate any SQL code or database-specific syntax
- The final output should be a clearer version of the original question in natural language that keeps all requested information
- Focus on making the question unambiguous while preserving all user-specified data requirements

Your response should be ONLY the refined, clear natural language question that captures the user's true intent without database-specific references. No analysis, no explanations, no formatting - just the clean, unambiguous question.
""",
    agent=agent,
    expected_output="Single refined natural language question that clearly expresses the user's intent using business terms, informed by database understanding but without referencing specific schema elements.",
)