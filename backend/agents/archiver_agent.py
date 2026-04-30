from agents.base_agent import BaseAgent
from core.config import QUEUE_ARCHIVE, QUEUE_ORCHESTRATE


class ArchiverAgent(BaseAgent):
    def __init__(self, message_bus):
        super().__init__(
            "ArchiverAgent",
            message_bus,
            subscribe_topic=QUEUE_ARCHIVE
        )

    async def process(self, message):
        # ✅ FIX: use object attributes
        file_name = message.file_name
        category = message.category
        is_duplicate = message.is_duplicate

        print(f"[{self.name}] Checking archive status for {file_name}")

        # 🚀 Drive-compatible logic
        if is_duplicate:
            message.should_archive = True
            message.category = "Archive"
            message.action_reason = "Duplicate file"

        elif category == "Flagged":
            message.should_archive = False
            message.action_reason = "Important / flagged file"

        else:
            message.should_archive = False
            message.action_reason = "Active file"

        # ✅ Send forward
        await self.bus.publish(QUEUE_ORCHESTRATE, message)