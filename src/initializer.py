from crewai import Crew, Process
from src.tools.vector_search_tool import VectorSearchTool
from src.tools.sql_execution_tool import SQLExecutionTool
from src.tools.sql_error_retrieval_tool import SQLErrorRetrievalTool
from src.agents.query_understanding_agent import get_query_understanding_agent
from src.agents.retrieval_agent import get_retrieval_agent
from src.agents.sql_generator_agent import get_sql_generator_agent
from src.agents.sql_execution_repair_agent import get_sql_execution_repair_agent
from src.tasks.query_understanding_task import get_query_understanding_task
from src.tasks.retrieval_task import get_retrieval_task
from src.tasks.sql_generation_task import get_sql_generation_task
from src.tasks.sql_execution_repair_task import get_sql_execution_repair_task
from src.vectorstore_setup import setup_vector_store
from crewai import LLM
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

db_path = os.getenv("DB_PATH")
chroma_dir = os.getenv("CHROMA_DIR")
gemini_api_key = os.getenv("GEMINI_API_KEY")

llm = LLM(model="gemini/gemini-1.5-flash", api_key=gemini_api_key,temperature=0)

vectorstore = setup_vector_store(rebuild=False)
vector_tool = VectorSearchTool(vectorstore=vectorstore) 
sql_execution_tool = SQLExecutionTool(db_path=db_path)
sql_error_retrieval_tool = SQLErrorRetrievalTool(vectorstore=vectorstore)

query_understanding_agent = get_query_understanding_agent(vector_tool, llm)
retrieval_agent = get_retrieval_agent(vector_tool, llm)
sql_generator_agent = get_sql_generator_agent(llm)
sql_execution_repair_agent = get_sql_execution_repair_agent(
    sql_execution_tool, sql_error_retrieval_tool, llm
)

query_understanding_task = get_query_understanding_task(query_understanding_agent)
retrieval_task = get_retrieval_task(retrieval_agent, context=[query_understanding_task])
sql_generation_task = get_sql_generation_task(sql_generator_agent, context=[query_understanding_task, retrieval_task])
sql_exec_repair_task = get_sql_execution_repair_task(sql_execution_repair_agent, context=[sql_generation_task])

complete_crew = Crew(
    agents=[
        query_understanding_agent,
        retrieval_agent,
        sql_generator_agent,
        sql_execution_repair_agent,
    ],
    tasks=[
        query_understanding_task,
        retrieval_task,
        sql_generation_task,
        sql_exec_repair_task,
    ],
    process=Process.sequential,
    verbose=True,
    memory=False,
    max_iter=1,
)