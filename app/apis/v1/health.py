import uuid
import json
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
        
        # Task 응답 생성
        task_response = {
            "task_id": task_id,
            "status": TaskStatus.PENDING,
            "result": None,
            "error": None,
            "created_at": datetime.now().isoformat(),
            "completed_at": None
        }
        
        # Redis에 Task 저장 (JSON 문자열로 data 저장)
        task_data = task_response.copy()
        task_data["data"] = json.dumps(survey.dict())
        
        await redis_client.hset(
            f"task:{task_id}",
            mapping=task_data
        )
        await redis_client.expire(f"task:{task_id}", config.TASK_RESULT_TTL)
        
        # AI Worker 큐에 작업 추가
        await redis_client.lpush("health_prediction_queue", task_id)
        
        return ORJSONResponse(
            content=task_response,
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
        
        # data 필드 제거 (응답에 불필요)
        response_data = {k: v for k, v in task_data.items() if k != "data"}
        
        # result가 JSON 문자열인 경우 파싱
        if response_data.get("result") and isinstance(response_data["result"], str):
            try:
                response_data["result"] = json.loads(response_data["result"])
            except json.JSONDecodeError:
                pass
        
        return ORJSONResponse(content=response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Task 조회 실패: {str(e)}"
        )


@health_router.get("/")
async def health_check():
    """Health Check 엔드포인트"""
    return {"status": "healthy", "service": "AI Healthcare API"}