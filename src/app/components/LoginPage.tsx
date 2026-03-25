import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Activity, Heart, Loader2 } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const { login, isLoading } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (provider: 'kakao' | 'naver') => {
    try {
      await login(provider);
      // OAuth 리다이렉트가 발생하므로 navigate는 실행되지 않음
    } catch (error) {
      console.error('로그인 실패:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 flex items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
          <p className="text-gray-600">로그인 처리 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-full mb-4">
            <Activity className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-3xl text-gray-900 mb-2">만성질환 예측 서비스</h1>
          <p className="text-gray-600">AI 기반 건강 위험도 분석 및 개선 서비스</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-center">로그인 / 회원가입</CardTitle>
            <CardDescription className="text-center">
              소셜 계정으로 간편하게 시작하세요
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button
              onClick={() => handleLogin('kakao')}
              className="w-full bg-[#FEE500] hover:bg-[#FDD835] text-gray-900"
              size="lg"
              disabled={isLoading}
            >
              <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 3C6.477 3 2 6.477 2 10.667c0 2.815 1.892 5.292 4.738 6.679-.197.728-.642 2.416-.736 2.795-.113.456.167.45.352.328.139-.092 2.148-1.437 3.146-2.103.507.072 1.027.111 1.5.111 5.523 0 10-3.477 10-7.81C22 6.477 17.523 3 12 3z" />
              </svg>
              카카오로 시작하기
            </Button>

            <Button
              onClick={() => handleLogin('naver')}
              className="w-full bg-[#03C75A] hover:bg-[#02B350] text-white"
              size="lg"
              disabled={isLoading}
            >
              <span className="mr-2 font-bold">N</span>
              네이버로 시작하기
            </Button>

            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-200"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">서비스 소개</span>
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-start space-x-3">
                <Heart className="h-5 w-5 text-red-500 mt-0.5 flex-shrink-0" />
                <div>
                  <h4 className="text-sm font-medium text-gray-900">AI 기반 만성질환 예측</h4>
                  <p className="text-sm text-gray-600">80개 건강 설문을 통해 4가지 만성질환 위험도를 예측합니다</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <Activity className="h-5 w-5 text-blue-500 mt-0.5 flex-shrink-0" />
                <div>
                  <h4 className="text-sm font-medium text-gray-900">맞춤형 건강 대시보드</h4>
                  <p className="text-sm text-gray-600">개인별 건강 상태를 한눈에 확인하고 관리할 수 있습니다</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <svg className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <h4 className="text-sm font-medium text-gray-900">개인맞춤 건강 권장사항</h4>
                  <p className="text-sm text-gray-600">예측 결과를 바탕으로 맞춤형 건강 개선 방안을 제공합니다</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <p className="text-center text-xs text-gray-500 mt-6">
          로그인 시 <a href="#" className="underline hover:text-gray-700">이용약관</a> 및 <a href="#" className="underline hover:text-gray-700">개인정보처리방침</a>에 동의하는 것으로 간주됩니다
        </p>
      </div>
    </div>
  );
};
