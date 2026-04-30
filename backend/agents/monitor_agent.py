import asyncio
from googleapiclient.discovery import build

from core.config import QUEUE_EXTRACT


class MonitorAgent:
    def __init__(self, bus):
        self.bus = bus
        self.seen_files = set()

    async def run(self):
        print("[MonitorAgent] Started (Google Drive mode).")

        from dashboard import system_state

        while True:
            creds = system_state.get("credentials")

            if creds is None:
                await asyncio.sleep(2)
                continue

            try:
                service = build("drive", "v3", credentials=creds)

                results = service.files().list(
                    pageSize=20,
                    fields="files(id, name, mimeType)"
                ).execute()

                files = results.get("files", [])

                for file in files:
                    file_id = file.get("id")
                    file_name = file.get("name")
                    mime_type = file.get("mimeType")

                    # ✅ Safety check
                    if not file_id or not file_name or not mime_type:
                        continue

                    # 🚨 CRITICAL FIX 1: Skip folders & Google Docs
                    if mime_type.startswith("application/vnd.google-apps"):
                        continue

                    # 🚨 CRITICAL FIX 2: Avoid duplicates
                    if file_id in self.seen_files:
                        continue

                    self.seen_files.add(file_id)

                    print(f"[MonitorAgent] New Drive file: {file_name}")

                    # ✅ Send to Extractor
                    await self.bus.publish(
                        QUEUE_EXTRACT,
                        {
                            "file_id": file_id,
                            "file_name": file_name
                        }
                    )

            except Exception as e:
                print(f"[MonitorAgent] Error: {type(e).__name__}: {e}")

            await asyncio.sleep(5)