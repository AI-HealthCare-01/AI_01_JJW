import pytest
from pydantic import ValidationError

from schemas import (
    AuthResponse,
    ChronicDiseaseSurveyRequest,
    OAuthProvider,
    OAuthRequest,
    TaskStatus,
    UserInfo,
)


def test_task_status_values():
    assert TaskStatus.PENDING == "pending"
    assert TaskStatus.COMPLETED == "completed"
    assert TaskStatus.FAILED == "failed"


def test_oauth_provider_values():
    assert OAuthProvider.KAKAO == "kakao"
    assert OAuthProvider.NAVER == "naver"


def test_user_info_defaults():
    user = UserInfo(user_id="u1", provider=OAuthProvider.KAKAO)
    assert user.user_id == "u1"
    assert user.provider == OAuthProvider.KAKAO


def test_oauth_request_invalid_provider():
    with pytest.raises(ValidationError):
        OAuthRequest(provider="google", code="abc", redirect_uri="http://localhost/")


def test_auth_response():
    user = UserInfo(user_id="u1", provider=OAuthProvider.NAVER)
    resp = AuthResponse(access_token="token123", user_info=user)
    assert resp.access_token == "token123"


def _make_survey_data(**overrides) -> dict:
    base = {f: 1 for f in ChronicDiseaseSurveyRequest.model_fields}
    # float 필드 기본값 조정
    for f in ["BO1_1", "BO2_1", "BD7_4", "BD7_5", "BA2_12", "BA2_13", "BA2_14", "HE_ht", "HE_wt", "HE_wc"]:
        base[f] = 1.0
    base["age"] = 30
    base.update(overrides)
    return base


def test_chronic_survey_valid():
    data = _make_survey_data()
    survey = ChronicDiseaseSurveyRequest(**data)
    assert survey.age == 30


def test_chronic_survey_age_out_of_range():
    with pytest.raises(ValidationError):
        ChronicDiseaseSurveyRequest(**_make_survey_data(age=0))


def test_chronic_survey_sex_out_of_range():
    with pytest.raises(ValidationError):
        ChronicDiseaseSurveyRequest(**_make_survey_data(sex=5))


def test_chronic_survey_field_count():
    assert len(ChronicDiseaseSurveyRequest.model_fields) == 80
