import spacy
from typing import Any, ClassVar
from crewai.tools import BaseTool

from src.paths import CHROMA_DIR




nlp = spacy.load("en_core_web_sm")

class VectorSearchTool(BaseTool):
    name: str = "vector_search_tool"
    description: str = "Search for relevant information from vector store using vector similarity"
    vectorstore: Any

    return_direct: bool = True
    handle_tool_error: bool = True

    skip_words: ClassVar[set] = {"table", "sum", "great", "column", "row"}

    def _run(self, query: str) -> str:
        try:
            doc = nlp(query)
            keywords = set(
                token.lemma_.lower()
                for token in doc
                if token.pos_ in {"NOUN", "PROPN", "ADJ"}
                and token.dep_ not in {"aux", "det", "punct"}
                and not token.is_stop
                and len(token.lemma_) > 2
                and token.lemma_.lower() not in self.skip_words
            )
            docs = self.vectorstore.similarity_search(query, k=10)
            if not docs:
                return "❌ No documents found."
            relevant_snippets = []
            for doc in docs:
                lines = doc.page_content.split('\n')
                matching_lines = [line for line in lines if any(word in line.lower() for word in keywords)]
                if matching_lines:
                    snippet = f"🔹 Table: {doc.metadata.get('table', 'Unknown')}\n" + "\n".join(matching_lines)
                    relevant_snippets.append(snippet)
            if not relevant_snippets:
                return "ℹ️ Documents found, but no lines matched your query keywords."
            return "\n\n".join(relevant_snippets)
        except Exception as e:
            return f"❌ Error during vector search: {str(e)}"