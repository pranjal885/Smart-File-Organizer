import sys
import webbrowser
import threading
import uvicorn
import time

def open_browser():
    # Wait for the uvicorn server to start before opening browser
    time.sleep(2)
    print("Opening browser at http://127.0.0.1:8000 ...")
    webbrowser.open("http://127.0.0.1:8000/login")

if __name__ == "__main__":
    print("Initializing Smart File Organizer Dashboard Launcher...")
    # Start browser launcher in background
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run the FastAPI app via Uvicorn
    # reload=False is required because we are keeping state in memory
    uvicorn.run("dashboard:app", host="127.0.0.1", port=8000, reload=False)
