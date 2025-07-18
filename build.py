import os
from src.vectorstore_setup import setup_vector_store

if __name__ == "__main__":
    print("🧱 Setting up the project...")

    # Rebuild vector store
    vectorstore = setup_vector_store()

    print("✅ Project setup complete.")
