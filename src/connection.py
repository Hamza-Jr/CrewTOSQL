from pathlib import Path
import sqlite3

# Define project root and DB path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "student_transcripts_tracking.sqlite"

def get_connection():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database file not found at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    return conn
