import React, { createContext, useContext, useState, useEffect, useRef, ReactNode } from 'react';
import { getOAuthUrls, oauthLogin, getUserProfile, logout as apiLogout, setAuthToken, getAuthToken } from '../services/api';

interface User {
  user_id: string;
  provider: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (provider: 'kakao' | 'naver') => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  // 콜백 처리 중 checkAuth가 중복 실행되는 것을 막기 위한 플래그
  const isHandlingCallback = useRef(false);

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');

    if (code) {
      // OAuth 콜백: code가 있으면 콜백 처리만 수행 (checkAuth 건너뜀)
      isHandlingCallback.current = true;
      handleOAuthCallback(code, urlParams.get('state'));
    } else {
      // 일반 접근: 기존 토큰으로 인증 상태 복원
      checkAuth();
    }
  }, []);

  const handleOAuthCallback = async (code: string, state: string | null) => {
    // URL에서 code를 즉시 제거 (새로고침 시 만료된 code 재사용 방지)
    window.history.replaceState({}, document.title, '/');

    try {
      setIsLoading(true);
      // provider는 로그인 시작 시 저장한 값으로 판별 (state 불일치 오류 방지)
      const savedProvider = localStorage.getItem('oauth_provider') as 'kakao' | 'naver' | null;
      const savedState = localStorage.getItem('oauth_state');
      const provider: 'kakao' | 'naver' =
        savedProvider === 'naver' && state && state === savedState ? 'naver' : 'kakao';
      const redirectUri = window.location.origin + '/';

      const authResponse = await oauthLogin(provider, code, redirectUri);

      setAuthToken(authResponse.access_token);
      localStorage.setItem('user_info', JSON.stringify(authResponse.user_info));
      localStorage.removeItem('oauth_state');
      localStorage.removeItem('oauth_provider');

      setUser(authResponse.user_info);
      // React Router가 인식할 수 있도록 pushState로 경로 변경
      window.history.pushState({}, document.title, '/select-service');
    } catch (error) {
      console.error('OAuth 로그인 실패:', error);
      localStorage.removeItem('oauth_state');
      localStorage.removeItem('oauth_provider');
      setAuthToken(null);
      localStorage.removeItem('user_info');
      setUser(null);
      window.history.replaceState({}, document.title, '/');
    } finally {
      setIsLoading(false);
      isHandlingCallback.current = false;
    }
  };

  const checkAuth = async () => {
    if (isHandlingCallback.current) return;
    try {
      setIsLoading(true);
      const token = getAuthToken();

      // 토큰이 없으면 인증되지 않은 상태 — localStorage user_info만으로는 인증 불가
      if (!token) {
        localStorage.removeItem('user_info');
        setUser(null);
        return;
      }

      const userProfile = await getUserProfile();
      setUser(userProfile);
    } catch {
      setAuthToken(null);
      localStorage.removeItem('user_info');
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (provider: 'kakao' | 'naver') => {
    try {
      setIsLoading(true);
      const urls = await getOAuthUrls();
      const redirectUri = window.location.origin + '/';

      // 어떤 provider로 시작했는지 저장 (콜백 시 판별용)
      localStorage.setItem('oauth_provider', provider);

      let oauthUrl: string;

      if (provider === 'kakao') {
        oauthUrl =
          `https://kauth.kakao.com/oauth/authorize` +
          `?client_id=${urls.kakao_client_id}` +
          `&redirect_uri=${encodeURIComponent(redirectUri)}` +
          `&response_type=code`;
      } else {
        const state = Math.random().toString(36).substring(2, 15);
        localStorage.setItem('oauth_state', state);
        oauthUrl =
          `https://nid.naver.com/oauth2.0/authorize` +
          `?client_id=${urls.naver_client_id}` +
          `&redirect_uri=${encodeURIComponent(redirectUri)}` +
          `&response_type=code` +
          `&state=${state}`;
      }

      window.location.href = oauthUrl;
    } catch (error) {
      console.error('OAuth URL 가져오기 실패:', error);
      alert('로그인 설정에 문제가 있습니다. 관리자에게 문의해 주세요.');
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await apiLogout();
    } catch {
      // 로그아웃 API 실패해도 로컬 상태 정리
    } finally {
      setUser(null);
      setAuthToken(null);
      localStorage.removeItem('user_info');
      localStorage.removeItem('oauth_state');
    }
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout, checkAuth }}>
      {children}
    </AuthContext.Provider>
  );
};
