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

                all_files = []
                page_token = None

                # 🔥 FETCH ALL FILES (PAGINATION)
                while True:
                    response = service.files().list(
                        pageSize=100,
                        fields="nextPageToken, files(id, name, mimeType)",
                        pageToken=page_token
                    ).execute()

                    files = response.get("files", [])
                    all_files.extend(files)

                    page_token = response.get("nextPageToken")

                    if not page_token:
                        break

                print(f"[MonitorAgent] Total files fetched: {len(all_files)}")

                for file in all_files:
                    file_id = file.get("id")
                    file_name = file.get("name")
                    mime_type = file.get("mimeType")

                    # ✅ Safety check
                    if not file_id or not file_name or not mime_type:
                        continue

                    # 🚨 Skip folders & Google Docs
                    if mime_type.startswith("application/vnd.google-apps"):
                        continue

                    # 🚨 Avoid re-processing same file
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