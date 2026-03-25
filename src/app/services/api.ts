/**
 * 만성질환 예측 서비스 API
 * FastAPI 백엔드와 연동
 */

const API_BASE_URL = "/api/v1";
const API_TIMEOUT = 60000; // 60초 (동기식 예측 대기)

// 📊 타입 정의
export interface SurveyData {
  [key: string]: string | number;
}

export interface PredictionResult {
  predictions: {
    DJ8_pre: number;
    DI1_pre: number;
    DI2_pre: number;
    DE1_pre: number;
  };
  guidelines: any | null;
  surveyData: Record<string, string>;
}

export interface AuthResponse {
  access_token: string;
  user_info: {
    user_id: string;
    email: string;
    name: string;
    provider: string;
    profile_image?: string;
  };
}

// 🔐 토큰 관리
let authToken: string | null = localStorage.getItem("access_token");

export const setAuthToken = (token: string | null) => {
  authToken = token;
  if (token) {
    localStorage.setItem("access_token", token);
  } else {
    localStorage.removeItem("access_token");
  }
};

export const getAuthToken = () => authToken;

// 🌐 HTTP 클라이언트
const apiClient = async (endpoint: string, options: RequestInit = {}) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(authToken && { Authorization: `Bearer ${authToken}` }),
        ...options.headers,
      },
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail || `HTTP ${response.status}: ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error: any) {
    clearTimeout(timeoutId);
    if (error.name === "AbortError") {
      throw new Error("요청 시간이 초과되었습니다. 다시 시도해 주세요.");
    }
    throw error;
  }
};

// 🔐 OAuth 인증
export const getOAuthUrls = async () => {
  return await apiClient("/auth/oauth/urls");
};

export const oauthLogin = async (
  provider: string,
  code: string,
  redirectUri: string
): Promise<AuthResponse> => {
  return await apiClient("/auth/oauth/login", {
    method: "POST",
    body: JSON.stringify({ provider, code, redirect_uri: redirectUri }),
  });
};

export const getUserProfile = async () => {
  return await apiClient("/auth/me");
};

export const logout = async () => {
  try {
    await apiClient("/auth/logout", { method: "POST" });
  } catch {
    // 로그아웃 실패해도 로컬 토큰 삭제
  }
  setAuthToken(null);
};

// 📤 만성질환 예측 (동기식 - 서버에서 결과 대기 후 반환)
export const submitSurvey = async (
  surveyData: SurveyData
): Promise<PredictionResult> => {
  const processedData: Record<string, number> = {};
  Object.entries(surveyData).forEach(([key, value]) => {
    const numValue = Number(value);
    processedData[key] = isNaN(numValue) ? 0 : numValue;
  });

  return await apiClient("/chronic/predict", {
    method: "POST",
    body: JSON.stringify(processedData),
  });
};

// 🏥 서비스 정보
export const getServiceInfo = async () => {
  return await apiClient("/chronic/");
};

export const getHealthCheck = async () => {
  return await apiClient("/health/");
};
