from pathlib import Path
import sqlite3, shutil
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma

from .paths import DB_PATH, SCHEMA_PATH, CHROMA_DIR
from langchain.schema import Document


# For embeddings
from langchain_huggingface import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# For vector store
from langchain_chroma import Chroma


def build_sqlite_db():
    """Run schema.sql to (re)create the SQLite database."""
    print("📦 (Re)creating SQLite database...")
    if DB_PATH.exists():
        DB_PATH.unlink()   # start fresh
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

def create_schema_documents() -> list:
    """Extract table, column & sample rows into langchain Documents."""
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    docs   = []

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    for (table_name,) in cursor.fetchall():
        cursor.execute(f"PRAGMA table_info({table_name});")
        cols   = cursor.fetchall()
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
        sample = cursor.fetchall()
        cursor.execute(f"PRAGMA foreign_key_list({table_name});")
        fks    = cursor.fetchall()

        content = [f"Table: {table_name}", "\nColumns:"]
        for col_id, col_name, col_type, notnull, dflt, pk in cols:
            flags = []
            if pk:       flags.append("PRIMARY KEY")
            if notnull:  flags.append("NOT NULL")
            if dflt:     flags.append(f"DEFAULT {dflt}")
            flag_txt = f" [{' '.join(flags)}]" if flags else ""
            content.append(f"- {col_name} ({col_type}){flag_txt}")

        if fks:
            content.append("\nForeign Keys:")
            for fk in fks:
                content.append(f"- {fk[3]} references {fk[2]}({fk[4]})")

        if sample:
            content.append("\nSample Data:")
            heads = [c[1] for c in cols]
            content.append(" | ".join(heads))
            content.append("-" * (len(" | ".join(heads))))
            for row in sample:
                content.append(" | ".join(str(v) if v is not None else "NULL" for v in row))

        docs.append(
            Document(
                page_content="\n".join(content),
                metadata={"table": table_name, "type": "schema"}
            )
        )
    conn.close()
    return docs

def setup_vector_store(rebuild=False):
    """Build or load the Chroma store."""
    if CHROMA_DIR.exists() and not rebuild:
        print("🔄 Reusing existing Chroma store")
        return Chroma(persist_directory=str(CHROMA_DIR), embedding_function=embeddings)

    # Start clean
    if CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)

    build_sqlite_db()
    docs = create_schema_documents()

    # add generic SQL patterns
    docs.extend([
        Document("SELECT columns FROM table WHERE condition - Basic selection pattern",
                 metadata={"type": "sql_pattern"}),
        Document("SELECT t1.*, t2.* FROM table1 t1 JOIN table2 t2 ON t1.id=t2.fk - Join pattern",
                 metadata={"type": "sql_pattern"}),
    ])

    print("⚙️  Building Chroma store …")
    store = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR)
    )
    print("✅ Vector store ready")
    return store

if __name__ == "__main__":
    setup_vector_store(rebuild=True)


'''

pip install -U langchain-huggingface



from langchain_huggingface import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")




'''