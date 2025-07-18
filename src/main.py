from dotenv import load_dotenv
load_dotenv()

from src.initializer import complete_crew

user_query = "what are all the addresses including line 1 and line 2?"

result = complete_crew.kickoff(inputs={"user_query": user_query})

print("\n📌 FINAL RESULT:\n")
print(result)
