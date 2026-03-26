import asyncio
import json
import logging
import os
import sys
from datetime import datetime

import redis.asyncio as redis

from ai_worker.core.config import config
from ai_worker.models.chronic_predictor import ChronicDiseasePredictor

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIWorker:
    def __init__(self):
        self.redis_client = None
        self.chronic_predictor = ChronicDiseasePredictor()

    async def connect_redis(self):
        self.redis_client = redis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=config.REDIS_DB,
            decode_responses=True,
        )

    async def process_chronic_disease_prediction(self, task_id: str, data: dict):
        try:
            logger.info(f"Processing task: {task_id}")

            await self.redis_client.hset(f"task:{task_id}", "status", "processing")

            prediction_result = await self.chronic_predictor.predict(data)

            existing_task = await self.redis_client.hgetall(f"task:{task_id}")

            await self.redis_client.hset(
                f"task:{task_id}",
                mapping={
                    "task_id": task_id,
                    "status": "completed",
                    "result": json.dumps(prediction_result),
                    "error": "",
                    "created_at": existing_task.get("created_at", ""),
                    "completed_at": datetime.now().isoformat(),
                },
            )

            logger.info(f"Completed task: {task_id}")

        except Exception as e:
            logger.error(f"Error processing task {task_id}: {str(e)}")
            existing_task = await self.redis_client.hgetall(f"task:{task_id}")

            await self.redis_client.hset(
                f"task:{task_id}",
                mapping={
                    "task_id": task_id,
                    "status": "failed",
                    "result": "",
                    "error": str(e),
                    "created_at": existing_task.get("created_at", ""),
                    "completed_at": datetime.now().isoformat(),
                },
            )

    async def run(self):
        await self.connect_redis()
        logger.info("AI Worker started - Chronic Disease Prediction Service")

        while True:
            try:
                result = await self.redis_client.brpop("chronic_disease_prediction_queue", timeout=5)

                if result:
                    _, task_id = result
                    logger.info(f"Received task: {task_id}")

                    task_data = await self.redis_client.hgetall(f"task:{task_id}")
                    if task_data and task_data.get("data"):
                        try:
                            data = (
                                json.loads(task_data["data"])
                                if isinstance(task_data["data"], str)
                                else task_data["data"]
                            )
                        except json.JSONDecodeError:
                            data = task_data["data"]

                        await self.process_chronic_disease_prediction(task_id, data)

            except Exception as e:
                logger.error(f"Worker error: {str(e)}")
                await asyncio.sleep(1)


async def main():
    worker = AIWorker()
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
