import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any

import redis.asyncio as redis
from ai_worker.core.config import config
from ai_worker.models.inference import HealthPredictor
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas import TaskResponse, TaskStatus, HealthPredictionResult

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIWorker:
    def __init__(self):
        self.redis_client = None
        self.health_predictor = HealthPredictor()
        
    async def connect_redis(self):
        """Redis 연결"""
        self.redis_client = redis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=config.REDIS_DB,
            decode_responses=True
        )
        
    async def process_health_prediction(self, task_id: str, data: Dict[str, Any]):
        """건강 예측 작업 처리"""
        try:
            logger.info(f"Processing health prediction task: {task_id}")
            
            # Task 상태를 PROCESSING으로 업데이트
            await self.redis_client.hset(
                f"task:{task_id}",
                "status", TaskStatus.PROCESSING
            )
            
            # AI 모델 추론 실행
            prediction_result = await self.health_predictor.predict(data)
            
            # 기존 task 데이터 조회
            existing_task = await self.redis_client.hgetall(f"task:{task_id}")
            
            # 결과를 TaskResponse 형태로 구성
            task_response = {
                "task_id": task_id,
                "status": TaskStatus.COMPLETED,
                "result": prediction_result.dict(),
                "error": None,
                "created_at": existing_task.get("created_at"),
                "completed_at": datetime.now().isoformat()
            }
            
            # Redis에 결과 저장
            await self.redis_client.hset(
                f"task:{task_id}",
                mapping=task_response
            )
            
            logger.info(f"Completed health prediction task: {task_id}")
            
        except Exception as e:
            logger.error(f"Error processing task {task_id}: {str(e)}")
            
            # 기존 task 데이터 조회
            existing_task = await self.redis_client.hgetall(f"task:{task_id}")
            
            # 오류 상태로 업데이트
            error_response = {
                "task_id": task_id,
                "status": TaskStatus.FAILED,
                "result": None,
                "error": str(e),
                "created_at": existing_task.get("created_at"),
                "completed_at": datetime.now().isoformat()
            }
            
            await self.redis_client.hset(
                f"task:{task_id}",
                mapping=error_response
            )
    
    async def run(self):
        """Worker 메인 루프"""
        await self.connect_redis()
        logger.info("AI Worker started")
        
        while True:
            try:
                # 큐에서 작업 대기 (블로킹, 5초 타임아웃)
                result = await self.redis_client.brpop("health_prediction_queue", timeout=5)
                
                if result:
                    queue_name, task_id = result
                    logger.info(f"Received task: {task_id}")
                    
                    # Task 데이터 조회
                    task_data = await self.redis_client.hgetall(f"task:{task_id}")
                    if task_data and task_data.get("data"):
                        # JSON 문자열을 파싱하여 딕셔너리로 변환
                        try:
                            data = json.loads(task_data["data"]) if isinstance(task_data["data"], str) else task_data["data"]
                        except json.JSONDecodeError:
                            data = task_data["data"]
                        
                        # 작업 처리
                        await self.process_health_prediction(task_id, data)
                    
            except Exception as e:
                logger.error(f"Worker error: {str(e)}")
                await asyncio.sleep(1)


async def main():
    worker = AIWorker()
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())