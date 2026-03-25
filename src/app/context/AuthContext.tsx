import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { getOAuthUrls, oauthLogin, getUserProfile, logout as apiLogout, setAuthToken, getAuthToken } from '../services/api';

interface User {
  user_id: string;
  email: string;
  name: string;
  provider: string;
  profile_image?: string;
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

  // 페이지 로드 시 기존 토큰으로 사용자 정보 확인
  useEffect(() => {
    checkAuth();
  }, []);

  // URL에서 OAuth 콜백 처리
  useEffect(() => {
    const handleOAuthCallback = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');
      const state = urlParams.get('state');
      
      if (code) {
        try {
          setIsLoading(true);
          const provider = state ? 'naver' : 'kakao';
          const redirectUri = window.location.origin + window.location.pathname;
          
          const authResponse = await oauthLogin(provider, code, redirectUri);
          
          // 토큰 저장
          setAuthToken(authResponse.access_token);
          localStorage.setItem('user_info', JSON.stringify(authResponse.user_info));
          
          setUser(authResponse.user_info);
          
          // URL에서 쿼리 파라미터 제거
          window.history.replaceState({}, document.title, window.location.pathname);
        } catch (error) {
          console.error('OAuth 로그인 실패:', error);
          alert('로그인에 실패했습니다. 다시 시도해 주세요.');
        } finally {
          setIsLoading(false);
        }
      }
    };

    handleOAuthCallback();
  }, []);

  const checkAuth = async () => {
    try {
      setIsLoading(true);
      const token = getAuthToken();
      
      if (!token) {
        // 로컬 스토리지에서 사용자 정보 확인
        const savedUserInfo = localStorage.getItem('user_info');
        if (savedUserInfo) {
          setUser(JSON.parse(savedUserInfo));
        }
        return;
      }

      // 토큰이 있으면 서버에서 사용자 정보 확인
      const userProfile = await getUserProfile();
      setUser(userProfile);
    } catch (error) {
      console.error('인증 확인 실패:', error);
      // 토큰이 유효하지 않으면 제거
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
      
      // OAuth URL 가져오기
      const urls = await getOAuthUrls();
      const redirectUri = encodeURIComponent(window.location.origin + window.location.pathname);
      
      let oauthUrl: string;
      
      if (provider === 'kakao') {
        oauthUrl = urls.kakao.replace('{redirect_uri}', redirectUri);
      } else {
        const state = Math.random().toString(36).substring(2, 15);
        localStorage.setItem('oauth_state', state);
        oauthUrl = urls.naver
          .replace('{redirect_uri}', redirectUri)
          .replace('{state}', state);
      }
      
      // OAuth 페이지로 리다이렉트
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
    } catch (error) {
      console.error('로그아웃 API 호출 실패:', error);
    } finally {
      setUser(null);
      localStorage.removeItem('user_info');
      localStorage.removeItem('oauth_state');
    }
  };

  const value: AuthContextType = {
    user,
    isLoading,
    login,
    logout,
    checkAuth,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};