/**
 * 만성질환 예측 서비스 API
 * 
 * ✅ 현재 상태: Mock 서버 모드 (개발/테스트용)
 * 
 * 📝 실제 서버 연동 시 설정 방법:
 * 1. USE_MOCK_SERVER를 false로 변경
 * 2. API_BASE_URL을 실제 백엔드 서버 URL로 변경
 * 3. submitSurvey 함수의 실제 fetch 구현 주석 해제
 * 4. 필요 시 인증 토큰 등 추가 헤더 설정
 * 
 * 📤 서버로 전송되는 데이터 형식:
 * {
 *   "age": "45",
 *   "sex": "1",
 *   "HE_ht": "170",
 *   "HE_wt": "68",
 *   ... (80개 변수)
 * }
 * 
 * 📥 서버로부터 받아야 하는 응답 형식:
 * {
 *   "predictions": {
 *     "DJ8_pre": 0 or 1,  // 알레르기비염 (0: 음성, 1: 양성)
 *     "DI1_pre": 0 or 1,  // 고혈압 (0: 음성, 1: 양성)
 *     "DI2_pre": 0 or 1,  // 이상지질혈증 (0: 음성, 1: 양성)
 *     "DE1_pre": 0 or 1   // 당뇨병 (0: 음성, 1: 양성)
 *   },
 *   "guidelines": { ... } or null  // openAPI 가이드라인 (선택)
 * }
 */

// ⚙️ 설정
const USE_MOCK_SERVER = true; // 🔴 실제 서버 연동 시 false로 변경
const API_BASE_URL = 'https://your-api-server.com/api'; // 🔴 실제 서버 URL로 변경
const API_TIMEOUT = 30000; // 30초 타임아웃

// 📊 타입 정의
export interface SurveyData {
  [key: string]: string;
}

export interface PredictionResult {
  predictions: {
    DJ8_pre: number; // 알레르기비염 (0: 음성, 1: 양성)
    DI1_pre: number; // 고혈압 (0: 음성, 1: 양성)
    DI2_pre: number; // 이상지질혈증 (0: 음성, 1: 양성)
    DE1_pre: number; // 당뇨병 (0: 음성, 1: 양성)
  };
  guidelines: any | null; // openAPI 건강 가이드라인 (없을 수도 있음)
  surveyData: SurveyData; // 제출된 설문 데이터
}

/**
 * 📤 설문 데이터를 서버로 전송하고 질환 예측 결과를 받아옴
 * 
 * @param surveyData - 80개 변수의 설문 응답 데이터
 * @returns 예측 결과 (DJ8_pre, DI1_pre, DI2_pre, DE1_pre) - 0 또는 1
 * @throws Error - 서버 통신 실패 시
 */
export const submitSurvey = async (surveyData: SurveyData): Promise<PredictionResult> => {
  console.log('📤 [API] 서버 전송 데이터:', surveyData);
  console.log('📊 [API] 변수 개수:', Object.keys(surveyData).length, '/ 80');

  // Mock 서버 모드
  if (USE_MOCK_SERVER) {
    console.log('🔧 [API] Mock 서버 모드로 실행 중');
    return mockServerResponse(surveyData);
  }

  // ===== 실제 서버 통신 (실제 서버 연동 시 아래 주석 해제) =====
  /*
  console.log('🌐 [API] 실제 서버로 요청 전송:', API_BASE_URL);
  
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);

    const response = await fetch(`${API_BASE_URL}/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // 필요 시 인증 토큰 추가
        // 'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(surveyData),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        `서버 오류 (${response.status}): ${errorData.message || response.statusText}`
      );
    }

    const result = await response.json();
    
    // 응답 검증
    if (!result.predictions) {
      throw new Error('서버 응답에 predictions 데이터가 없습니다.');
    }

    console.log('✅ [API] 서버 응답 수신:', result);
    
    return {
      predictions: result.predictions,
      guidelines: result.guidelines || null,
      surveyData,
    };
  } catch (error) {
    if (error.name === 'AbortError') {
      console.error('❌ [API] 서버 응답 시간 초과');
      throw new Error('서버 응답 시간이 초과되었습니다. 다시 시도해 주세요.');
    }
    
    console.error('❌ [API] 서버 통신 오류:', error);
    throw new Error(
      error instanceof Error 
        ? error.message 
        : '서버와의 통신에 실패했습니다. 잠시 후 다시 시도해 주세요.'
    );
  }
  */

  return mockServerResponse(surveyData);
};

/**
 * 🧪 Mock 서버 응답 생성 (개발/테스트용)
 * 
 * 실제 ML 모델의 동작을 시뮬레이션합니다.
 * 모델은 0(음성) 또는 1(양성)의 이진 분류 결과를 반환합니다.
 */
const mockServerResponse = async (surveyData: SurveyData): Promise<PredictionResult> => {
  console.log('⏳ [Mock] 서버 응답 시뮬레이션 시작 (2초 지연)');
  
  // 실제 서버 응답 시뮬레이션 (2초 지연)
  await new Promise(resolve => setTimeout(resolve, 2000));

  // 주요 변수 추출하여 간단한 시뮬레이션
  const age = parseInt(surveyData.age || '40');
  const smokingStatus = parseInt(surveyData.BS1_1 || '1');
  const drinkingFreq = parseInt(surveyData.BD1_11 || '0');

  // 0 또는 1의 이진 분류 결과 시뮬레이션
  const result: PredictionResult = {
    predictions: {
      DJ8_pre: Math.random() > 0.6 ? 1 : 0, // 알레르기비염
      DI1_pre: age > 50 || Math.random() > 0.7 ? 1 : 0, // 고혈압
      DI2_pre: drinkingFreq > 3 || Math.random() > 0.65 ? 1 : 0, // 이상지질혈증
      DE1_pre: smokingStatus === 3 || Math.random() > 0.7 ? 1 : 0, // 당뇨병
    },
    guidelines: null,
    surveyData,
  };

  console.log('✅ [Mock] 서버 응답 생성 완료:', {
    DJ8_pre: result.predictions.DJ8_pre === 1 ? '양성' : '음성',
    DI1_pre: result.predictions.DI1_pre === 1 ? '양성' : '음성',
    DI2_pre: result.predictions.DI2_pre === 1 ? '양성' : '음성',
    DE1_pre: result.predictions.DE1_pre === 1 ? '양성' : '음성',
  });

  return result;
};

/**
 * 🌐 건강 가이드라인 조회 (openAPI 연동)
 */
export const fetchHealthGuidelines = async (
  predictions: PredictionResult['predictions']
): Promise<any | null> => {
  console.log('ℹ️ [API] 가이드라인 조회 기능은 아직 구현되지 않았습니다.');
  return null;
};

/**
 * 🔐 인증 토큰 설정 (필요 시 사용)
 */
export const setAuthToken = (token: string) => {
  console.log('🔐 [API] 인증 토큰 설정:', token ? '토큰 있음' : '토큰 없음');
};
