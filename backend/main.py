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

import uvicorn

if __name__ == "__main__":
    print("Starting Smart File Organizer...")
    uvicorn.run("dashboard:app", host="0.0.0.0", port=10000)