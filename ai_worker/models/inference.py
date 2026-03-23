import json
import os

import joblib
import numpy as np
import pandas as pd
import torch
import torch.nn as nn


# ==========================================
# 모델 아키텍처
# ==========================================
class SEBlock(nn.Module):
    def __init__(self, dim, reduction=4):
        super().__init__()
        bottleneck_dim = max(16, dim // reduction)
        self.fc = nn.Sequential(
            nn.Linear(dim, bottleneck_dim, bias=False),
            nn.SiLU(),
            nn.Linear(bottleneck_dim, dim, bias=False),
            nn.Sigmoid(),
        )

    def forward(self, x):
        return x * self.fc(x)


class AdvancedResidualBlock(nn.Module):
    def __init__(self, dim, dropout_rate):
        super().__init__()
        self.norm1 = nn.BatchNorm1d(dim)
        self.activation = nn.SiLU()
        self.linear1 = nn.Linear(dim, dim)
        self.norm2 = nn.BatchNorm1d(dim)
        self.linear2 = nn.Linear(dim, dim)
        self.se = SEBlock(dim)
        self.dropout = nn.Dropout(dropout_rate)

    def forward(self, x):
        residual = x
        out = self.norm1(x)
        out = self.activation(out)
        out = self.linear1(out)
        out = self.dropout(out)
        out = self.norm2(out)
        out = self.activation(out)
        out = self.linear2(out)
        out = self.se(out)
        return residual + out


class Predictor(nn.Module):
    def __init__(self, input_dim, fixed_feat=7, num_blocks=3, dropout_rate=0.4, feature_drop_rate=0.04):
        super().__init__()
        self.fixed_cols = fixed_feat
        self.feature_dropout = nn.Dropout1d(p=feature_drop_rate)
        self.input_norm = nn.BatchNorm1d(input_dim)

        hidden_dim = input_dim * 2
        self.stem = nn.Sequential(nn.Linear(input_dim, hidden_dim), nn.SiLU())

        self.stage1 = nn.ModuleList([AdvancedResidualBlock(hidden_dim, dropout_rate) for _ in range(num_blocks)])

        mid_dim = max(hidden_dim // 6, 64)
        self.transition = nn.Sequential(nn.Linear(hidden_dim, mid_dim), nn.BatchNorm1d(mid_dim), nn.SiLU())

        self.stage2 = nn.ModuleList([AdvancedResidualBlock(mid_dim, dropout_rate / 2) for _ in range(num_blocks - 1)])

        self.classifier = nn.Sequential(
            nn.Linear(mid_dim, mid_dim // 2), nn.SiLU(), nn.Dropout(dropout_rate / 4), nn.Linear(mid_dim // 2, 4)
        )

        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_normal_(m.weight, mode="fan_out", nonlinearity="relu")
            elif isinstance(m, nn.BatchNorm1d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)

    def forward(self, x):
        x = self.input_norm(x)
        x = self.stem(x)
        for block in self.stage1:
            x = block(x)
        x = self.transition(x)
        for block in self.stage2:
            x = block(x)
        return self.classifier(x)


# ==========================================
# 추론 파이프라인
# ==========================================
DISEASE_NAMES = ["DJ8_dg", "DI1_dg", "DE1_dg", "DI2_dg"]
MODEL_SAVE_PATH = "./checkpoints/"
INPUT_DIM = 127
N_SPLITS = 7


def load_preprocessing_artifacts(base_path=MODEL_SAVE_PATH):
    """학습 시 저장한 전처리 객체들을 로드"""
    scaler = joblib.load(os.path.join(base_path, "scaler.pkl"))
    encoder = joblib.load(os.path.join(base_path, "encoder.joblib"))

    with open(os.path.join(base_path, "feature_columns.json"), encoding="utf-8") as f:
        feature_cols = json.load(f)

    with open(os.path.join(base_path, "encoding_cols.json"), encoding="utf-8") as f:
        encoding_cols = json.load(f)

    return scaler, encoder, feature_cols, encoding_cols


def preprocess_input(raw_df, scaler, encoder, feature_cols, encoding_cols):
    """
    원본 DataFrame을 모델 입력 형태로 전처리.
    raw_df: 원본 피처가 담긴 DataFrame (결측치 제거 및 이진 변환 완료 상태)
    """
    # 1. 이진 컬럼 변환 (1→0, 2→1)
    binary_cols = [col for col in raw_df.columns if set(raw_df[col].dropna().unique()) <= {1, 2}]
    for col in binary_cols:
        raw_df[col] = raw_df[col].replace({1: 0, 2: 1})

    # 2. 원핫 인코딩 (학습된 encoder 사용)
    ohe_target_cols = encoding_cols
    raw_df[ohe_target_cols] = raw_df[ohe_target_cols].astype(str)
    encoded_array = encoder.transform(raw_df[ohe_target_cols])
    encoded_col_names = encoder.get_feature_names_out(ohe_target_cols)
    encoded_df = pd.DataFrame(encoded_array, columns=encoded_col_names, index=raw_df.index)
    raw_df = pd.concat([raw_df.drop(columns=ohe_target_cols), encoded_df], axis=1)

    # 3. 피처 순서 정렬
    x = raw_df[feature_cols]

    # 4. 스케일링
    x_scaled = scaler.transform(x).astype(np.float32)

    return x_scaled


def inference(x_scaled, model_save_path=MODEL_SAVE_PATH, input_dim=INPUT_DIM, n_splits=N_SPLITS, temperature=0.44):
    """
    가중 앙상블 추론 (Weighted Blending)
    X_scaled: 전처리 완료된 numpy array (n_samples, 127)
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    x_tensor = torch.from_numpy(x_scaled).float()
    if x_tensor.ndim == 1:
        x_tensor = x_tensor.unsqueeze(0)
    x_tensor = x_tensor.to(device)

    # 아티팩트 로드
    valid_folds, f2_scores = [], []
    for fold in range(1, n_splits + 1):
        path = os.path.join(model_save_path, f"fold{fold}_artifact.pth")
        if not os.path.exists(path):
            continue
        # weights_only=True로 설정하여 메타데이터만 빠르게 로드 시도
        cp_meta = torch.load(path, map_location=device, weights_only=False)
        f2_scores.append(cp_meta["val_f2"])
        valid_folds.append(fold)
        del cp_meta  # 메타데이터 즉시 삭제

    if not f2_scores:
        raise ValueError("사용 가능한 폴드 아티팩트가 없습니다.")

    # 가중치 계산
    f2_tensor = torch.tensor(f2_scores)
    weights = torch.nn.functional.softmax(f2_tensor / temperature, dim=0).numpy()

    # 앙상블 추론
    total_probs = np.zeros((x_tensor.size(0), 4))
    collected_thresholds = []

    model = Predictor(input_dim).to(device)
    model.eval()

    with torch.no_grad():
        for idx, fold_num in enumerate(valid_folds):
            path = os.path.join(model_save_path, f"fold{fold_num}_artifact.pth")

            # [핵심] 해당 폴드의 가중치만 로드
            checkpoint = torch.load(path, map_location=device, weights_only=False)
            model.load_state_dict(checkpoint["state_dict"])

            # 추론 및 가중치 적용
            probs = torch.sigmoid(model(x_tensor)).cpu().numpy()
            total_probs += probs * weights[idx]

            # [수정] 임계값 리스트 곱셈 에러 방지 (np.array 변환)
            # collected_thresholds.append(checkpoint['thresholds'] * weights[idx])
            current_thresholds = np.array(checkpoint["thresholds"])
            collected_thresholds.append(current_thresholds * weights[idx])

            # [핵심] 사용이 끝난 체크포인트 명시적 삭제로 메모리 확보
            del checkpoint

    final_thresholds = np.sum(collected_thresholds, axis=0)
    final_preds = (total_probs >= final_thresholds).astype(int)

    return {
        "predictions": final_preds,
        "probabilities": total_probs,
        "thresholds_used": final_thresholds,
        "disease_names": DISEASE_NAMES,
        "weights_applied": weights,
    }


# ==========================================
# 실행 예시
# ==========================================
if __name__ == "__main__":
    # 1. 전처리 객체 로드
    scaler, encoder, feature_cols, encoding_cols = load_preprocessing_artifacts()

    # 2. 입력 데이터 준비 (예시: 이미 스케일링된 랜덤 데이터)
    # 실제 사용 시에는 preprocess_input()을 통해 원본 DataFrame을 전처리하세요.
    sample_input = np.random.randn(1, INPUT_DIM).astype(np.float32)

    # 3. 추론
    result = inference(sample_input)

    # 4. 결과 출력
    print("=== 만성질환 예측 결과 ===")
    for i, name in enumerate(DISEASE_NAMES):
        pred = "위험" if result["predictions"][0][i] == 1 else "정상"
        prob = result["probabilities"][0][i]
        print(f"  {name}: {pred} (확률: {prob:.4f})")
    print(f"\n사용된 임계값: {result['thresholds_used']}")
    print(f"폴드 가중치: {np.round(result['weights_applied'], 4)}")
