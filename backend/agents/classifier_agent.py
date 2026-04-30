import asyncio

from agents.base_agent import BaseAgent
from core.config import QUEUE_CLASSIFY, QUEUE_DEDUPLICATE


class ClassifierAgent(BaseAgent):
    def __init__(self, message_bus):
        super().__init__(
            "ClassifierAgent",
            message_bus,
            subscribe_topic=QUEUE_CLASSIFY
        )

        # 🚀 DISABLE GEMINI (no quota)
        self.client = None

    async def process(self, message):
        file_name = message.file_name
        content = message.content

        print(f"[{self.name}] Classifying {file_name}")

        category = "Flagged"
        tags = []

        # ✅ Simple extension-based classification (FAST + RELIABLE)
        ext = file_name.split('.')[-1].lower()

        if ext in ['jpg', 'jpeg', 'png', 'gif']:
            category = "Images"
        elif ext in ['pdf', 'doc', 'docx', 'txt']:
            category = "Documents"
        elif ext in ['mp4', 'mkv', 'avi']:
            category = "Videos"
        elif ext in ['xls', 'xlsx', 'csv']:
            category = "Spreadsheets"
        elif ext in ['py', 'js', 'html', 'css', 'json']:
            category = "Code"

        # ✅ Assign results
        message.category = category
        message.tags = tags

        # ✅ Send to next agent
        await self.bus.publish(QUEUE_DEDUPLICATE, message)