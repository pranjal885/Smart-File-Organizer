import asyncio
from typing import Dict
from core.config import (
    QUEUE_EXTRACT, QUEUE_CLASSIFY, 
    QUEUE_DEDUPLICATE, QUEUE_ARCHIVE, QUEUE_ORCHESTRATE
)

class MessageBus:
    def __init__(self):
        self.queues: Dict[str, asyncio.Queue] = {
            QUEUE_EXTRACT: asyncio.Queue(),
            QUEUE_CLASSIFY: asyncio.Queue(),
            QUEUE_DEDUPLICATE: asyncio.Queue(),
            QUEUE_ARCHIVE: asyncio.Queue(),
            QUEUE_ORCHESTRATE: asyncio.Queue()
        }
        
    async def publish(self, topic: str, message: any):
        if topic in self.queues:
            await self.queues[topic].put(message)
        else:
            print(f"Warning: Topic {topic} not found.")
            
    async def subscribe(self, topic: str):
        if topic in self.queues:
            return await self.queues[topic].get()
        return None
        
    def task_done(self, topic: str):
        if topic in self.queues:
            self.queues[topic].task_done()
