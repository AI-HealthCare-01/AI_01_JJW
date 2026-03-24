import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import ORJSONResponse

from app.db.databases import get_redis
from schemas import HealthSurveyRequest, TaskRequest, TaskResponse, TaskStatus
from app.core.config import config

health_router = APIRouter()


@health_router.post("/predict", response_model=TaskResponse)
async def predict_health_risk(survey: HealthSurveyRequest):
    """건강 위험도 예측 요청"""
    try:
        redis_client = await get_redis()
        
        # 고유 Task ID 생성
        task_id = str(uuid.uuid4())
        
        # Task 요청 생성
        task_request = TaskRequest(
            task_type="health_prediction",
            data=survey.dict()
        )
        
        # Task 상태 초기화
        task_response = TaskResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,
            created_at=datetime.now().isoformat()
        )
        
        # Redis에 Task 저장
        await redis_client.hset(
            f"task:{task_id}",
            mapping=task_response.dict()
        )
        await redis_client.expire(f"task:{task_id}", config.TASK_RESULT_TTL)
        
        # AI Worker 큐에 작업 추가
        await redis_client.lpush("health_prediction_queue", task_id)
        
        return ORJSONResponse(
            content=task_response.dict(),
            status_code=status.HTTP_202_ACCEPTED
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"작업 생성 실패: {str(e)}"
        )


@health_router.get("/task/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: str):
    """Task 상태 조회"""
    try:
        redis_client = await get_redis()
        
        # Redis에서 Task 조회
        task_data = await redis_client.hgetall(f"task:{task_id}")
        
        if not task_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task를 찾을 수 없습니다"
            )
        
        return ORJSONResponse(content=task_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Task 조회 실패: {str(e)}"
        )