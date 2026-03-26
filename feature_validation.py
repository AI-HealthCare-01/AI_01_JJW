#!/usr/bin/env python3
"""
80개 피처 순서 검증 스크립트
사용자 제공 순서와 스키마 순서가 일치하는지 확인
"""

import os
import sys

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from schemas import ChronicDiseaseSurveyRequest

USER_ORDER = [
    "sex", "age", "cfam", "genertn", "house", "live_t", "marri_1", "fam_rela",
    "tins", "npins", "D_1_1", "D_2_1", "M_2_yr", "BH9_11", "BH1", "BH2_61",
    "LQ4_00", "LQ1_sb", "LQ2_ab", "AC1_yr", "MH1_yr", "MO1_wk", "educ", "EC1_1",
    "EC_lgw_2", "BO1", "BO1_1", "BO2_1", "BD1_11", "BD2_1", "BD2_31",
    "BD7_4", "BD7_5", "BA2_12", "BA2_13", "BA2_14", "BP1", "BP7", "BS1_1",
    "BS12_37", "BS12_1", "BS8_2", "BS9_2", "BS13", "BE3_71", "BE3_81", "BE3_91",
    "BE3_75", "BE3_85", "BE8_1", "BE3_31", "BE5_1", "HE_fh", "HE_ht", "HE_wt",
    "HE_wc", "OR1", "O_pain", "O_ortho", "BM1_0", "BM7", "BM8", "OR1_2",
    "MO4_00", "BM14", "E_Q_EX", "L_BR_FQ", "L_LN_FQ", "L_DN_FQ", "L_OUT_FQ",
    "LS_VEG1", "LS_VEG2", "LS_FRUIT", "LS_1YR", "LK_EDU", "LK_LB_CO", "N_DIET",
    "N_DUSUAL", "N_WAT_C", "LF_SAFE",
]


def _print_mismatch(schema_fields: list, user_order: list) -> None:
    print("\n불일치 항목:")
    print("-" * 40)

    if len(schema_fields) != len(user_order):
        print(f"WARNING: 피처 개수 불일치: 스키마({len(schema_fields)}) vs 사용자({len(user_order)})")

        schema_set = set(schema_fields)
        user_set = set(user_order)

        missing_in_schema = user_set - schema_set
        extra_in_schema = schema_set - user_set

        if missing_in_schema:
            print(f"스키마에서 누락: {missing_in_schema}")
        if extra_in_schema:
            print(f"스키마에 추가: {extra_in_schema}")

    max_len = max(len(schema_fields), len(user_order))
    for i in range(max_len):
        schema_field = schema_fields[i] if i < len(schema_fields) else "N/A"
        user_field = user_order[i] if i < len(user_order) else "N/A"

        if schema_field != user_field:
            print(f"{i + 1:2d}. 스키마: {schema_field:12} | 사용자: {user_field}")


def _validate_ai_worker(schema_fields: list) -> None:
    try:
        from ai_worker.models.chronic_predictor import ChronicDiseasePredictor

        predictor = ChronicDiseasePredictor()
        ai_worker_order = predictor.feature_order

        print("AI Worker 피처 순서 검증:")
        print(f"AI Worker 피처 개수: {len(ai_worker_order)}")
        print(f"스키마와 일치 여부: {'OK 일치' if schema_fields == ai_worker_order else 'NG 불일치'}")

        if schema_fields != ai_worker_order:
            print("WARNING: AI Worker와 스키마 간 순서 불일치 발견!")
            for i, (schema_field, ai_field) in enumerate(zip(schema_fields, ai_worker_order, strict=False)):
                if schema_field != ai_field:
                    print(f"{i + 1:2d}. 스키마: {schema_field:12} | AI Worker: {ai_field}")

    except Exception as e:
        print(f"WARNING: AI Worker 검증 실패: {e}")


def main():
    schema_fields = list(ChronicDiseaseSurveyRequest.model_fields.keys())

    print("=" * 60)
    print("80개 피처 순서 검증 결과")
    print("=" * 60)

    print(f"스키마 피처 개수: {len(schema_fields)}")
    print(f"사용자 제공 피처 개수: {len(USER_ORDER)}")
    print(f"순서 일치 여부: {'OK 일치' if schema_fields == USER_ORDER else 'NG 불일치'}")

    if schema_fields != USER_ORDER:
        _print_mismatch(schema_fields, USER_ORDER)
    else:
        print("OK 모든 피처가 정확한 순서로 정의되었습니다!")
        print("\n피처 목록:")
        print("-" * 40)
        for i, field in enumerate(schema_fields, 1):
            print(f"{i:2d}. {field}")

    print("\n" + "=" * 60)

    _validate_ai_worker(schema_fields)

    print("=" * 60)


if __name__ == "__main__":
    main()
