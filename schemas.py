from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TaskStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ChronicDiseaseSurveyRequest(BaseModel):
    # 기본 인구학적 정보
    sex: int = Field(..., ge=0, le=2, description="성별 (0: 남성, 1: 여성)")
    age: int = Field(..., ge=1, le=120, description="나이")
    cfam: int = Field(..., description="가족 구성원 수")
    genertn: int = Field(..., description="세대 구성")
    house: int = Field(..., description="주택 소유 여부")
    live_t: int = Field(..., description="주택 형태")
    marri_1: int = Field(..., description="혼인 여부")
    fam_rela: int = Field(..., description="가구주와의 관계")

    # 보험 정보
    tins: int = Field(..., description="건강보험 종류")
    npins: int = Field(..., description="민간보험 가입 여부")

    # 건강 상태
    D_1_1: int = Field(..., description="주관적 건강상태")
    D_2_1: int = Field(..., description="우울감 경험")
    M_2_yr: int = Field(..., description="미충족 의료")

    # 예방접종 및 건강검진
    BH9_11: int = Field(..., description="인플루엔자 예방접종")
    BH1: int = Field(..., description="건강검진 수검")
    BH2_61: int = Field(..., description="암검진 수검")

    # 활동제한 및 삶의 질
    LQ4_00: int = Field(..., description="활동제한")
    LQ1_sb: int = Field(..., description="와병 경험")
    LQ2_ab: int = Field(..., description="결근/결석 경험")

    # 손상 및 의료이용
    AC1_yr: int = Field(..., description="사고/중독 경험")
    MH1_yr: int = Field(..., description="입원 경험")
    MO1_wk: int = Field(..., description="외래 진료")

    # 교육 및 경제
    educ: int = Field(..., description="교육 수준")
    EC1_1: int = Field(..., description="경제활동 상태")
    EC_lgw_2: int = Field(..., description="직업 분류")

    # 비만 및 체중조절
    BO1: int = Field(..., description="체형 인식")
    BO1_1: float = Field(..., description="체중 변화")
    BO2_1: float = Field(..., description="체중 조절 노력")

    # 음주
    BD1_11: int = Field(..., description="음주 빈도")
    BD2_1: int = Field(..., description="음주량")
    BD2_31: int = Field(..., description="폭음 빈도")
    BD7_4: float = Field(..., description="음주 권유")
    BD7_5: float = Field(..., description="음주 상담")

    # 안전의식
    BA2_12: float = Field(..., description="운전석 안전벨트")
    BA2_13: float = Field(..., description="앞좌석 안전벨트")
    BA2_14: float = Field(..., description="뒷좌석 안전벨트")

    # 정신건강
    BP1: int = Field(..., description="스트레스 인지")
    BP7: int = Field(..., description="정신건강 상담")

    # 흡연
    BS1_1: int = Field(..., description="흡연 상태")
    BS12_37: int = Field(..., description="궐련형 전자담배")
    BS12_1: int = Field(..., description="액상형 전자담배")
    BS8_2: int = Field(..., description="직장 간접흡연")
    BS9_2: int = Field(..., description="가정 간접흡연")
    BS13: int = Field(..., description="공공장소 간접흡연")

    # 신체활동
    BE3_71: int = Field(..., description="고강도 신체활동 일수")
    BE3_81: int = Field(..., description="중강도 신체활동 일수")
    BE3_91: int = Field(..., description="이동 걷기/자전거 일수")
    BE3_75: int = Field(..., description="여가 고강도 활동 일수")
    BE3_85: int = Field(..., description="여가 중강도 활동 일수")
    BE8_1: int = Field(..., description="앉아서 보내는 시간")
    BE3_31: int = Field(..., description="걷기 일수")
    BE5_1: int = Field(..., description="근력운동 일수")

    # 검진조사
    HE_fh: int = Field(..., description="가족력")

    # 신체계측
    HE_ht: float = Field(..., description="신장 (cm)")
    HE_wt: float = Field(..., description="체중 (kg)")
    HE_wc: float = Field(..., description="허리둘레 (cm)")

    # 구강건강
    OR1: int = Field(..., description="구강건강 인식")
    O_pain: int = Field(..., description="치통 경험")
    O_ortho: int = Field(..., description="교정치료 경험")
    BM1_0: int = Field(..., description="칫솔질 여부")
    BM7: int = Field(..., description="씹기 불편감")
    BM8: int = Field(..., description="말하기 불편감")
    OR1_2: int = Field(..., description="구강검진")
    MO4_00: int = Field(..., description="치과 이용")
    BM14: int = Field(..., description="치과 미충족")

    # 안검사
    E_Q_EX: int = Field(..., description="안과 검사 시기")

    # 식생활
    L_BR_FQ: int = Field(..., description="아침식사 빈도")
    L_LN_FQ: int = Field(..., description="점심식사 빈도")
    L_DN_FQ: int = Field(..., description="저녁식사 빈도")
    L_OUT_FQ: int = Field(..., description="외식 빈도")
    LS_VEG1: int = Field(..., description="채소 섭취(김치 포함)")
    LS_VEG2: int = Field(..., description="채소 섭취(김치 제외)")
    LS_FRUIT: int = Field(..., description="과일 섭취")
    LS_1YR: int = Field(..., description="보충제 복용")
    LK_EDU: int = Field(..., description="영양교육")
    LK_LB_CO: int = Field(..., description="영양표시 확인")

    # 식품섭취
    N_DIET: int = Field(..., description="식사요법")
    N_DUSUAL: int = Field(..., description="식사량 비교")
    N_WAT_C: int = Field(..., description="물 섭취량")

    # 식품안전
    LF_SAFE: int = Field(..., description="식생활 형편")


class PredictionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    predictions: dict[str, int] = Field(..., description="질환별 예측 결과 (0 또는 1)")
    guidelines: Any | None = Field(None, description="건강 개선 가이드라인")
    survey_data: dict[str, str] = Field(..., alias="surveyData", description="원본 설문 데이터")


class TaskRequest(BaseModel):
    task_type: str = Field(..., description="작업 유형")
    data: dict[str, Any] = Field(..., description="작업 데이터")


class TaskResponse(BaseModel):
    task_id: str = Field(..., description="작업 ID")
    status: TaskStatus = Field(..., description="작업 상태")
    result: dict[str, Any] | None = Field(None, description="작업 결과")
    error: str | None = Field(None, description="오류 메시지")
    created_at: str = Field(..., description="생성 시간")
    completed_at: str | None = Field(None, description="완료 시간")


class OAuthProvider(StrEnum):
    KAKAO = "kakao"
    NAVER = "naver"


class OAuthRequest(BaseModel):
    provider: OAuthProvider = Field(..., description="OAuth 제공자")
    code: str = Field(..., description="인증 코드")
    redirect_uri: str = Field(..., description="리다이렉트 URI")


class UserInfo(BaseModel):
    user_id: str = Field(..., description="사용자 ID")
    email: str = Field("", description="이메일 (선택 동의)")
    name: str = Field("", description="이름 (선택 동의)")
    provider: OAuthProvider = Field(..., description="OAuth 제공자")
    profile_image: str | None = Field(None, description="프로필 이미지 URL")


class AuthResponse(BaseModel):
    access_token: str = Field(..., description="액세스 토큰")
    user_info: UserInfo = Field(..., description="사용자 정보")
