# 🚀 Smart File Organizer (AI + Multi-Agent System)

A scalable and intelligent system that automatically organizes Google Drive files using a multi-agent architecture, SHA-256 based duplicate detection, and a real-time streaming pipeline.

---

## 1. 🌟 Features

1. Google Drive Integration using OAuth 2.0  
2. Multi-Agent Architecture for modular and scalable processing  
3. Automatic File Classification  
4. SHA-256 based Duplicate Detection  
5. Automatic File Organization into folders (e.g., Duplicates)  
6. Real-time Dashboard with live logs and statistics  
7. Streaming Processing for handling large-scale data  
8. Extensible design for future AI/ML integration  

---

## 2. 🧠 System Architecture

MonitorAgent → ExtractorAgent → ClassifierAgent → DeduplicatorAgent → ArchiverAgent → OrchestratorAgent  

---

## 3. 🔹 Agents Overview

1. MonitorAgent – Fetches files from Google Drive  
2. ExtractorAgent – Downloads file content  
3. ClassifierAgent – Categorizes files  
4. DeduplicatorAgent – Detects duplicates using SHA-256 hashing  
5. ArchiverAgent – Applies archive logic  
6. OrchestratorAgent – Moves files and stores metadata in database  

---

## 4. ⚙️ Tech Stack

1. Backend – FastAPI (Python)  
2. Database – SQLite (extendable to PostgreSQL)  
3. Frontend – HTML, CSS, JavaScript  
4. API – Google Drive API  
5. Architecture – Event-driven multi-agent system  
6. Hashing – SHA-256 (content-based duplicate detection)  

---

## 5. 🔐 How It Works

1. User logs in via Google OAuth  
2. System scans Google Drive files  
3. Files are processed using a streaming pipeline  
4. Each file flows through multiple agents  
5. Duplicate files are detected using SHA-256 hashing  
6. Duplicate files are moved to a dedicated folder  
7. Dashboard displays real-time logs and statistics  

---

## 6. 📊 Dashboard Features

1. Login status indicator  
2. Total files processed  
3. Duplicate files count  
4. Archived files count  
5. Live processing logs  

---

## 7. 🚀 Setup Instructions

### 7.1 Clone Repository
```
git clone https://github.com/your-username/smart-file-organizer.git
cd smart-file-organizer
```

### 7.2 Install Dependencies
```
pip install -r requirements.txt
```

### 7.3 Add Google Credentials

1. Create OAuth client in Google Cloud Console  
2. Download credentials JSON  
3. Place it as credentials.json OR use environment variables  

### 7.4 Run Project
```
python main.py
```

### 7.5 Open in Browser
```
http://127.0.0.1:8000/login
```

---

## 8. 🚀 Deployment

1. Deployed on Render  
2. Uses environment variables for secure credentials  
3. Connected with GitHub for auto-deployment  

---

## 9. 🔥 Key Highlights (Resume Worthy)

1. Designed a multi-agent distributed system for automated file processing  
2. Implemented SHA-256 based duplicate detection for accurate file matching  
3. Built a real-time streaming pipeline to handle large-scale file systems  
4. Integrated Google Drive API with OAuth authentication  
5. Developed a live dashboard with real-time logs and analytics  

---

## 10. 📈 Future Improvements

1. AI-based file similarity detection  
2. Data visualization using charts  
3. Background task queue (Celery / Redis)  
4. Persistent database using PostgreSQL  
5. File search and filtering system  
6. File optimization and storage suggestions  

---

## 11. 🧑‍💻 Author

Pranjal Patil  

---

## 12. ⭐ Support

If you found this project useful, consider giving it a star on GitHub  
