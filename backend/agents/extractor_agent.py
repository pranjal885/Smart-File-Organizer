import asyncio
import io

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from core.config import QUEUE_EXTRACT, QUEUE_CLASSIFY
from models.messages import AgentMessage


class ExtractorAgent:
    def __init__(self, bus):
        self.bus = bus

    async def run(self):
        print("[ExtractorAgent] Started.")

        from dashboard import system_state

        while True:
            message = await self.bus.subscribe(QUEUE_EXTRACT)

            if not message:
                await asyncio.sleep(1)
                continue

            file_id = message.get("file_id")
            file_name = message.get("file_name")

            if not file_id or not file_name:
                continue

            print(f"[ExtractorAgent] Processing: {file_name}")

            creds = system_state.get("credentials")

            if creds is None:
                print("[ExtractorAgent] No credentials yet.")
                continue

            try:
                service = build("drive", "v3", credentials=creds)

                file_data = await asyncio.to_thread(
                    self.download_file, service, file_id
                )

                content = file_data.read()

                # 🔥 CRITICAL FIX (THIS WAS MISSING)
                msg = AgentMessage(
                    file_id=file_id,          # ✅ THIS LINE FIXES EVERYTHING
                    file_name=file_name,
                    content=content
                )

                await self.bus.publish(QUEUE_CLASSIFY, msg)

            except Exception as e:
                print(f"[ExtractorAgent] Error: {type(e).__name__}: {e}")

    def download_file(self, service, file_id):
        request = service.files().get_media(fileId=file_id)

        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()

        file.seek(0)
        return file