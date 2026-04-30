import asyncio
from datetime import datetime
from sqlalchemy.orm import Session

from agents.base_agent import BaseAgent
from core.config import QUEUE_ORCHESTRATE, OUTPUT_DIRS
from core.database import SessionLocal, FileRecord

import os
from googleapiclient.discovery import build
from core.state import system_state


class OrchestratorAgent(BaseAgent):
    def __init__(self, message_bus):
        super().__init__(
            "OrchestratorAgent",
            message_bus,
            subscribe_topic=QUEUE_ORCHESTRATE
        )

        self.report_interval = 7 * 24 * 3600  # 7 days

    async def start_producer(self):
        asyncio.create_task(self.weekly_report_loop())

    async def process(self, message):
        file_name = message.file_name
        category = message.category

        print(f"[{self.name}] Finalizing {file_name} -> {category}")

        if getattr(message, "source", "drive") == "drive":
            # 🔥 GOOGLE DRIVE LOGIC
            creds = system_state.get("credentials")

            if creds:
                try:
                    service = build("drive", "v3", credentials=creds)

                    # ✅ FIXED CONDITION
                    if message.is_duplicate and message.file_id:
                        self.move_duplicate_to_folder(service, message.file_id, "Duplicates")
                        print(f"[{self.name}] Moved {file_name} to Duplicates folder")

                except Exception as e:
                    print(f"[{self.name}] Drive error: {e}")
        elif getattr(message, "source", "drive") == "local":
            import shutil
            try:
                if message.is_duplicate and message.file_id:
                    dup_dir = OUTPUT_DIRS.get("Duplicates", "Duplicates")
                    # If duplicate file with same name exists, it will overwrite it which is fine
                    target_path = os.path.join(dup_dir, file_name)
                    shutil.move(message.file_id, target_path)
                    print(f"[{self.name}] Moved {file_name} to local Duplicates folder: {target_path}")
            except Exception as e:
                print(f"[{self.name}] Local Move Error: {e}")

        # ✅ SAVE TO DATABASE (DO NOT TOUCH)
        db: Session = SessionLocal()

        try:
            record = FileRecord(
                file_id=message.file_id,
                file_name=file_name,
                file_hash=message.file_hash,
                category=category,
                tags=",".join(message.tags or []),
                original_path="Google Drive",
                current_path="Cloud",
                is_duplicate=message.is_duplicate,
                duplicate_of=message.duplicate_of,
                is_archived=message.should_archive
            )

            db.add(record)
            db.commit()

        except Exception as e:
            print(f"[{self.name}] DB error: {e}")

        finally:
            db.close()

    # 🔥 MOVE FILE TO DRIVE FOLDER
    def move_duplicate_to_folder(self, service, file_id, folder_name="Duplicates"):
        try:
            # 1️⃣ Check if folder exists
            results = service.files().list(
                q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                fields="files(id, name)"
            ).execute()

            folders = results.get("files", [])

            # 2️⃣ Create if not exists
            if folders:
                folder_id = folders[0]["id"]
            else:
                folder_metadata = {
                    "name": folder_name,
                    "mimeType": "application/vnd.google-apps.folder"
                }

                folder = service.files().create(
                    body=folder_metadata,
                    fields="id"
                ).execute()

                folder_id = folder["id"]

            # 3️⃣ Get current parents
            file = service.files().get(
                fileId=file_id,
                fields="parents"
            ).execute()

            parents = file.get("parents", [])
            previous_parents = ",".join(parents) if parents else None

            # 4️⃣ Move file
            service.files().update(
                fileId=file_id,
                addParents=folder_id,
                removeParents=previous_parents,
                fields="id, parents"
            ).execute()

        except Exception as e:
            print("[Drive Move Error]", e)

    async def weekly_report_loop(self):
        while True:
            await asyncio.sleep(self.report_interval)
            print(f"[{self.name}] Generating weekly report...")
            self.generate_report()

    def generate_report(self):
        db: Session = SessionLocal()

        try:
            total_files = db.query(FileRecord).count()
            duplicates = db.query(FileRecord).filter(FileRecord.is_duplicate == True).count()
            archived = db.query(FileRecord).filter(FileRecord.is_archived == True).count()

            report_text = f"Weekly Report - {datetime.now().strftime('%Y-%m-%d')}\n"
            report_text += f"Total files processed: {total_files}\n"
            report_text += f"Duplicates found: {duplicates}\n"
            report_text += f"Files archived: {archived}\n"

            report_filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            report_path = os.path.join(OUTPUT_DIRS["Reports"], report_filename)

            with open(report_path, "w") as f:
                f.write(report_text)

            print(f"[{self.name}] Report saved to {report_path}")

        finally:
            db.close()