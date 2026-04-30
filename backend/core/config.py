import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Output Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAGING_DIR = os.path.join(BASE_DIR, "Staging")
OUTPUT_DIRS = {
    "Documents": os.path.join(BASE_DIR, "Documents"),
    "Images": os.path.join(BASE_DIR, "Images"),
    "Videos": os.path.join(BASE_DIR, "Videos"),
    "Spreadsheets": os.path.join(BASE_DIR, "Spreadsheets"),
    "Code": os.path.join(BASE_DIR, "Code"),
    "Archive": os.path.join(BASE_DIR, "Archive"),
    "Duplicates": os.path.join(BASE_DIR, "Duplicates"),
    "Flagged": os.path.join(BASE_DIR, "Flagged"),
    "Reports": os.path.join(BASE_DIR, "Reports"),
}

# Queue Names
QUEUE_EXTRACT = "queue_extract"
QUEUE_CLASSIFY = "queue_classify"
QUEUE_DEDUPLICATE = "queue_deduplicate"
QUEUE_ARCHIVE = "queue_archive"
QUEUE_ORCHESTRATE = "queue_orchestrate"

def init_directories():
    os.makedirs(STAGING_DIR, exist_ok=True)
    for path in OUTPUT_DIRS.values():
        os.makedirs(path, exist_ok=True)
