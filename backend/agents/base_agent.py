import asyncio
from typing import Optional
from core.message_bus import MessageBus
from models.messages import AgentMessage

class BaseAgent:
    def __init__(self, name: str, message_bus: MessageBus, subscribe_topic: Optional[str] = None):
        self.name = name
        self.bus = message_bus
        self.subscribe_topic = subscribe_topic
        
    async def run(self):
        print(f"[{self.name}] Started.")
        if not self.subscribe_topic:
            await self.start_producer()
            return
            
        while True:
            message = None
            try:
                message = await self.bus.subscribe(self.subscribe_topic)
                if message is not None:
                    await self.process(message)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[{self.name}] Error processing message: {e}")
            finally:
                if message is not None:
                    try:
                        self.bus.task_done(self.subscribe_topic)
                    except ValueError:
                        pass

    async def start_producer(self):
        # Override for agents that generate initial messages rather than reacting
        pass
        
    async def process(self, message: AgentMessage):
        raise NotImplementedError("Agents must implement process(message)")
