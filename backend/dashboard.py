import os
import json
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

import asyncio
import sys
import collections

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from google_auth_oauthlib.flow import Flow

from core.database import SessionLocal, FileRecord
from core.config import init_directories
from core.database import init_db
from core.message_bus import MessageBus

from agents.monitor_agent import MonitorAgent
from agents.extractor_agent import ExtractorAgent
from agents.classifier_agent import ClassifierAgent
from agents.deduplicator_agent import DeduplicatorAgent
from agents.archiver_agent import ArchiverAgent
from agents.orchestrator_agent import OrchestratorAgent

from core.state import system_state


# =======================
# OAUTH CONFIG
# =======================
SCOPES = ["https://www.googleapis.com/auth/drive"]

BASE_URL = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8000")
REDIRECT_URI = f"{BASE_URL}/auth/callback"

oauth_flow = None


# =======================
# LOG CATCHER
# =======================
class LogCatcher:
    def __init__(self):
        self.logs = collections.deque(maxlen=300)
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        sys.stdout = self
        sys.stderr = self
        
    def write(self, message):
        self.original_stdout.write(message)
        msg_str = message.strip()
        if msg_str:
            self.logs.append(msg_str)
            
    def flush(self):
        self.original_stdout.flush()

log_catcher = LogCatcher()


# =======================
# APP INIT
# =======================
app = FastAPI(title="Smart File Organizer Dashboard")

# 🔥 FINAL CORRECT TEMPLATE PATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(
    directory=os.path.join(BASE_DIR, "backend", "templates")
)


# =======================
# STARTUP
# =======================
@app.on_event("startup")
async def startup_event():
    init_directories()
    init_db()
    print("[System] Dashboard started successfully.")


# =======================
# HOME
# =======================
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


# =======================
# LOGIN
# =======================
@app.get("/login")
def login():
    global oauth_flow

    creds_json = os.getenv("GOOGLE_CREDENTIALS")

    if not creds_json:
        return {"error": "GOOGLE_CREDENTIALS not set"}

    creds_dict = json.loads(creds_json)

    oauth_flow = Flow.from_client_config(
        creds_dict,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    auth_url, state = oauth_flow.authorization_url(
        prompt="consent",
        access_type="offline"
    )

    system_state["oauth_state"] = state

    return RedirectResponse(auth_url)


# =======================
# CALLBACK
# =======================
@app.get("/auth/callback")
def callback(request: Request):
    global oauth_flow

    incoming_state = request.query_params.get("state")

    if incoming_state != system_state.get("oauth_state"):
        return {"error": "State mismatch. Please login again."}

    oauth_flow.fetch_token(
        authorization_response=str(request.url)
    )

    system_state["credentials"] = oauth_flow.credentials

    print("[OAuth] Login successful!")

    return RedirectResponse("/")


# =======================
# STATUS
# =======================
@app.get("/api/status")
async def status():
    return {
        "running": system_state.get("running", False),
        "logged_in": system_state.get("credentials") is not None
    }


# =======================
# START SYSTEM
# =======================
@app.post("/api/start")
async def start_system(request: Request):
    if system_state.get("running"):
        return {"status": "already running"}

    if system_state.get("credentials") is None:
        return {"error": "Login required before starting Drive mode"}

    bus = MessageBus()

    classifier = ClassifierAgent(bus)
    deduplicator = DeduplicatorAgent(bus)
    archiver = ArchiverAgent(bus)
    orchestrator = OrchestratorAgent(bus)

    monitor = MonitorAgent(bus)
    extractor = ExtractorAgent(bus)

    tasks = [
        asyncio.create_task(monitor.run()),
        asyncio.create_task(extractor.run()),
        asyncio.create_task(classifier.run()),
        asyncio.create_task(deduplicator.run()),
        asyncio.create_task(archiver.run()),
        asyncio.create_task(orchestrator.run()),
        asyncio.create_task(orchestrator.start_producer())
    ]

    system_state["tasks"] = tasks
    system_state["running"] = True

    print("[System] Background agents started.")
    return {"status": "started"}


# =======================
# STOP SYSTEM
# =======================
@app.post("/api/stop")
async def stop_system():
    if not system_state.get("running"):
        return {"status": "already stopped"}

    for task in system_state["tasks"]:
        task.cancel()

    system_state["tasks"] = []
    system_state["running"] = False

    print("[System] Background agents stopped.")
    return {"status": "stopped"}


# =======================
# LOGS
# =======================
@app.get("/api/logs")
async def get_logs():
    return {"logs": list(log_catcher.logs)}


# =======================
# STATS
# =======================
@app.get("/api/stats")
async def get_stats():
    db = SessionLocal()
    try:
        return {
            "total": db.query(FileRecord).count(),
            "duplicates": db.query(FileRecord).filter(FileRecord.is_duplicate == True).count(),
            "archived": db.query(FileRecord).filter(FileRecord.is_archived == True).count()
        }
    finally:
        db.close()


# =======================
# FILES
# =======================
@app.get("/api/files")
async def get_files():
    db = SessionLocal()
    try:
        records = db.query(FileRecord).all()
        return [
            {
                "name": r.file_name,
                "category": r.category,
                "duplicate": r.is_duplicate,
                "archived": r.is_archived
            }
            for r in records
        ]
    finally:
        db.close()