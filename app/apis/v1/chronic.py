import asyncio
import json
import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import ORJSONResponse

from app.core.config import config
from app.db.databases import get_redis
from app.dependencies.auth import get_current_user
from schemas import (
    ChronicDiseaseSurveyRequest,
    PredictionResponse,
    TaskResponse,
    TaskStatus,
    UserInfo,
)

chronic_router = APIRouter()


@chronic_router.post("/predict", response_model=PredictionResponse)
async def predict_chronic_disease(
    survey: ChronicDiseaseSurveyRequest,
):
    try:
        redis_client = await get_redis()
        task_id = str(uuid.uuid4())
        survey_data = survey.model_dump()

        # Redis에 Task 저장
        task_data = {
            "task_id": task_id,
            "status": TaskStatus.PENDING,
            "data": json.dumps(survey_data),
            "created_at": datetime.now().isoformat(),
        }
        await redis_client.hset(f"task:{task_id}", mapping=task_data)
        await redis_client.expire(f"task:{task_id}", config.TASK_RESULT_TTL)

        # AI Worker 큐에 작업 추가
        await redis_client.lpush("chronic_disease_prediction_queue", task_id)

        # 폴링으로 결과 대기 (최대 30초)
        for _ in range(60):
            await asyncio.sleep(0.5)
            task_result = await redis_client.hgetall(f"task:{task_id}")
            if task_result.get("status") == TaskStatus.COMPLETED:
                result_data = task_result.get("result", "{}")
                if isinstance(result_data, str):
                    try:
                        result_data = json.loads(result_data)
                    except json.JSONDecodeError:
                        result_data = {}

                predictions = {
                    "DJ8_pre": result_data.get("DJ8_pre", 0),
                    "DI1_pre": result_data.get("DI1_pre", 0),
                    "DI2_pre": result_data.get("DI2_pre", 0),
                    "DE1_pre": result_data.get("DE1_pre", 0),
                }

                # 원본 설문 데이터를 문자열로 변환
                survey_str = {k: str(v) for k, v in survey_data.items()}

                return ORJSONResponse(
                    content={
                        "predictions": predictions,
                        "guidelines": result_data.get("guidelines"),
                        "surveyData": survey_str,
                    }
                )

            if task_result.get("status") == TaskStatus.FAILED:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=task_result.get("error", "예측 처리 실패"),
                )

        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="예측 처리 시간이 초과되었습니다",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"예측 요청 실패: {e!s}",
        ) from e


@chronic_router.post("/predict/async", response_model=TaskResponse)
async def predict_chronic_disease_async(
    survey: ChronicDiseaseSurveyRequest,
    current_user: Annotated[UserInfo, Depends(get_current_user)],
):
    try:
        redis_client = await get_redis()
        task_id = str(uuid.uuid4())

        task_response = {
            "task_id": task_id,
            "status": TaskStatus.PENDING,
            "result": None,
            "error": None,
            "created_at": datetime.now().isoformat(),
            "completed_at": None,
        }

        survey_data = survey.model_dump()
        survey_data["user_id"] = current_user.user_id

        task_data = task_response.copy()
        task_data["data"] = json.dumps(survey_data)

        await redis_client.hset(f"task:{task_id}", mapping=task_data)
        await redis_client.expire(f"task:{task_id}", config.TASK_RESULT_TTL)
        await redis_client.lpush("chronic_disease_prediction_queue", task_id)

        return ORJSONResponse(content=task_response, status_code=status.HTTP_202_ACCEPTED)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"예측 요청 생성 실패: {e!s}",
        ) from e


@chronic_router.get("/task/{task_id}", response_model=TaskResponse)
async def get_prediction_task_status(task_id: str):
    try:
        redis_client = await get_redis()
        task_data = await redis_client.hgetall(f"task:{task_id}")

        if not task_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="예측 작업을 찾을 수 없습니다",
            )

        response_data = {k: v for k, v in task_data.items() if k != "data"}

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
            detail=f"작업 상태 조회 실패: {e!s}",
        ) from e


@chronic_router.get("/")
async def chronic_disease_info():
    return ORJSONResponse(
        content={
            "service": "만성질환 예측 서비스",
            "diseases": [
                {"code": "DJ8_pre", "name": "알레르기비염"},
                {"code": "DI1_pre", "name": "고혈압"},
                {"code": "DE1_pre", "name": "당뇨병"},
                {"code": "DI2_pre", "name": "이상지질혈증"},
            ],
            "features": 80,
            "description": "80개 피처를 기반으로 4가지 만성질환 위험도를 예측합니다",
        }
    )
