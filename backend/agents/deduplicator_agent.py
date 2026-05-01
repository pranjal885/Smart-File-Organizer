import hashlib
import spacy
from sqlalchemy.orm import Session

from agents.base_agent import BaseAgent
from core.config import QUEUE_DEDUPLICATE, QUEUE_ARCHIVE
from core.database import SessionLocal, FileRecord


class DeduplicatorAgent(BaseAgent):
    def __init__(self, message_bus):
        super().__init__(
            "DeduplicatorAgent",
            message_bus,
            subscribe_topic=QUEUE_DEDUPLICATE
        )

        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            self.nlp = None

    async def process(self, message):
        file_name = message.file_name
        content = message.content

        print(f"[{self.name}] Deduplicating {file_name}")

        # ❗ If no content, skip
        if content is None:
            print(f"[{self.name}] No content found.")
            message.is_duplicate = False
            await self.bus.publish(QUEUE_ARCHIVE, message)
            return

        # 🔥 Compute SHA256 hash
        file_hash = self._hash_content(content)
        message.file_hash = file_hash

        db: Session = SessionLocal()

        try:
            # 🔍 Check if same hash already exists
            existing = db.query(FileRecord).filter(
                FileRecord.file_hash == file_hash
            ).first()

            if existing:
                print(
                    f"[{self.name}] Duplicate found: "
                    f"{file_name} → {existing.file_name}"
                )

                message.is_duplicate = True
                message.duplicate_of = existing.file_id
                message.category = "Duplicates"

            else:
                # ✅ Important: explicitly mark non-duplicate
                message.is_duplicate = False

        except Exception as e:
            print(f"[{self.name}] DB error: {e}")
            message.is_duplicate = False

        finally:
            db.close()

        # ➡️ Send to next stage
        await self.bus.publish(QUEUE_ARCHIVE, message)

    def _hash_content(self, content: bytes) -> str:
        sha256_hash = hashlib.sha256()
        sha256_hash.update(content)
        return sha256_hash.hexdigest()