from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from app.models.schemas import ThreatEvent

import logging

logger = logging.getLogger(__name__)


class EventLogger:

    def __init__(self):
        self.client = AsyncIOMotorClient(
            settings.MONGODB_URL
        )

        self.db = self.client[
            settings.DATABASE_NAME
        ]

        self.collection = self.db[
            "threat_events"
        ]

    async def initialize(self):
        await self.collection.create_index(
            [("timestamp", -1)]
        )

        logger.info(
            "MongoDB indices initialized."
        )

    async def log_threat(
        self,
        event: ThreatEvent
    ):
        await self.collection.update_one(
            {"event_id": event.event_id},
            {
                "$set": event.model_dump(
                    mode="json"
                )
            },
            upsert=True
        )

    async def update_explanation(
        self,
        event_id: str,
        explanation: str
    ):
        await self.collection.update_one(
            {"event_id": event_id},
            {
                "$set": {
                    "explanation": explanation,
                    "status": "Analyzed"
                }
            }
        )


event_logger = EventLogger()