# src/paths.py
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent   # one level up from src/
DATA_DIR      = PROJECT_ROOT / "data"
DB_PATH       = DATA_DIR / "student_transcripts_tracking.sqlite"
SCHEMA_PATH   = DATA_DIR / "schema.sql"
CHROMA_DIR    = PROJECT_ROOT / "chroma_data1"


