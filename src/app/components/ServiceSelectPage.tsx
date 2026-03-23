import React from 'react';
import { useNavigate } from 'react-router';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { ClipboardList, Activity, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const ServiceSelectPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 p-4">
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center justify-between mb-8 pt-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
              <Activity className="h-5 w-5 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-500">안녕하세요,</p>
              <p className="text-gray-900">{user?.name}님</p>
            </div>
          </div>
          <Button variant="ghost" size="sm" onClick={() => { logout(); navigate('/'); }}>
            로그아웃
          </Button>
        </div>

        <div className="text-center mb-10">
          <h1 className="text-2xl text-gray-900 mb-2">서비스 선택</h1>
          <p className="text-gray-600">이용하실 서비스를 선택해 주세요.</p>
        </div>

        <div className="space-y-4">
          <Card
            className="cursor-pointer hover:shadow-lg transition-shadow border-2 hover:border-blue-400"
            onClick={() => navigate('/survey')}
          >
            <CardContent className="flex items-center gap-5 p-6">
              <div className="w-14 h-14 bg-blue-100 rounded-xl flex items-center justify-center flex-shrink-0">
                <ClipboardList className="h-7 w-7 text-blue-600" />
              </div>
              <div className="flex-1">
                <CardTitle className="text-lg mb-1">만성질환 예측 설문 진행</CardTitle>
                <CardDescription>
                  국민건강영양조사 기반 80개 문항 설문을 통해 만성질환 위험도를 예측합니다.
                </CardDescription>
              </div>
              <ArrowRight className="h-5 w-5 text-gray-400 flex-shrink-0" />
            </CardContent>
          </Card>

          {/* 추후 추가 서비스 */}
          <Card className="opacity-50 cursor-not-allowed">
            <CardContent className="flex items-center gap-5 p-6">
              <div className="w-14 h-14 bg-gray-100 rounded-xl flex items-center justify-center flex-shrink-0">
                <Activity className="h-7 w-7 text-gray-400" />
              </div>
              <div className="flex-1">
                <CardTitle className="text-lg mb-1 text-gray-400">생활습관 개선 챌린지</CardTitle>
                <CardDescription className="text-gray-400">
                  준비 중인 서비스입니다. 곧 만나보실 수 있습니다.
                </CardDescription>
              </div>
              <span className="text-xs bg-gray-200 text-gray-500 px-2 py-1 rounded-full flex-shrink-0">Coming Soon</span>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
