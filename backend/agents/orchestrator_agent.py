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
        print(f"[DEBUG] Saving file: {file_name}")

        # 🔥 GOOGLE DRIVE LOGIC
        if getattr(message, "source", "drive") == "drive":
            creds = system_state.get("credentials")

            if creds:
                try:
                    service = build("drive", "v3", credentials=creds)

                    if message.is_duplicate and message.file_id:
                        self.move_duplicate_to_folder(service, message.file_id, "Duplicates")
                        print(f"[{self.name}] Moved {file_name} to Duplicates folder")

                except Exception as e:
                    print(f"[{self.name}] Drive error: {e}")

        # 🔥 LOCAL FILE LOGIC
        elif getattr(message, "source", "drive") == "local":
            import shutil
            try:
                if message.is_duplicate and message.file_id:
                    dup_dir = OUTPUT_DIRS.get("Duplicates", "Duplicates")
                    target_path = os.path.join(dup_dir, file_name)
                    shutil.move(message.file_id, target_path)
                    print(f"[{self.name}] Moved {file_name} to local Duplicates folder")
            except Exception as e:
                print(f"[{self.name}] Local Move Error: {e}")

        # ✅ SAVE TO DATABASE (FULL FIX)
        db: Session = SessionLocal()

        try:
            record = FileRecord(
                file_id=message.file_id,
                file_name=file_name,
                file_hash=getattr(message, "file_hash", None),
                category=category,
                tags=",".join(message.tags or []),
                original_path="Google Drive",
                current_path="Duplicates" if message.is_duplicate else "Main",
                is_duplicate=bool(message.is_duplicate),  # 🔥 FORCE TRUE/FALSE
                duplicate_of=getattr(message, "duplicate_of", None),
                is_archived=False  # 🔥 FIXED
            )

            db.add(record)
            db.commit()
            total = db.query(FileRecord).count()
            print(f"[DEBUG] Total records in DB: {total}")

            print(f"[{self.name}] Saved to DB | Duplicate: {record.is_duplicate}")

        except Exception as e:
            print(f"[{self.name}] DB error: {e}")

        finally:
            db.close()

    # 🔥 MOVE FILE TO DRIVE FOLDER
    def move_duplicate_to_folder(self, service, file_id, folder_name="Duplicates"):
        try:
            results = service.files().list(
                q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                fields="files(id, name)"
            ).execute()

            folders = results.get("files", [])

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

            file = service.files().get(
                fileId=file_id,
                fields="parents"
            ).execute()

            parents = file.get("parents", [])
            previous_parents = ",".join(parents) if parents else None

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