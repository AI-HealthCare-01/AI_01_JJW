from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator
from enum import StrEnum


class TaskStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class HealthSurveyRequest(BaseModel):
    """건강 설문 요청 스키마"""
    age: int = Field(..., ge=1, le=120, description="나이 (1-120)")
    gender: str = Field(..., regex="^(male|female)$", description="성별 (male/female)")
    height: float = Field(..., ge=50.0, le=250.0, description="키 (cm, 50-250)")
    weight: float = Field(..., ge=10.0, le=300.0, description="몸무게 (kg, 10-300)")
    systolic_bp: int = Field(..., ge=70, le=250, description="수축기 혈압 (70-250)")
    diastolic_bp: int = Field(..., ge=40, le=150, description="이완기 혈압 (40-150)")
    cholesterol: float = Field(..., ge=100.0, le=500.0, description="콜레스테롤 (mg/dL, 100-500)")
    glucose: float = Field(..., ge=50.0, le=400.0, description="혈당 (mg/dL, 50-400)")
    smoking: bool = Field(..., description="흡연 여부")
    alcohol: bool = Field(..., description="음주 여부")
    exercise: int = Field(..., ge=0, le=7, description="주간 운동 일수 (0-7)")
    
    @validator('diastolic_bp')
    def validate_blood_pressure(cls, v, values):
        if 'systolic_bp' in values and v >= values['systolic_bp']:
            raise ValueError('이완기 혈압은 수축기 혈압보다 낮아야 합니다')
        return v


class TaskRequest(BaseModel):
    """AI 작업 요청 스키마"""
    task_type: str = Field(..., description="작업 유형")
    data: Dict[str, Any] = Field(..., description="작업 데이터")


class TaskResponse(BaseModel):
    """AI 작업 응답 스키마"""
    task_id: str = Field(..., description="작업 ID")
    status: TaskStatus = Field(..., description="작업 상태")
    result: Optional[Dict[str, Any]] = Field(None, description="작업 결과")
    error: Optional[str] = Field(None, description="오류 메시지")
    created_at: str = Field(..., description="생성 시간")
    completed_at: Optional[str] = Field(None, description="완료 시간")


class HealthPredictionResult(BaseModel):
    """건강 예측 결과 스키마"""
    risk_score: float = Field(..., ge=0.0, le=1.0, description="위험도 점수 (0-1)")
    risk_level: str = Field(..., description="위험도 등급")
    recommendations: List[str] = Field(..., description="건강 권장사항")
    confidence: float = Field(..., ge=0.0, le=1.0, description="예측 신뢰도")