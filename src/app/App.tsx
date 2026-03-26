import { useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { Toaster } from "./components/ui/sonner";
import { toast } from "sonner";
import { LoginPage } from "./components/LoginPage";
import { ServiceSelectPage } from "./components/ServiceSelectPage";
import { SurveyPage } from "./components/SurveyPage";
import { DashboardPage } from "./components/DashboardPage";
import { Loader2 } from "lucide-react";

const LoadingSpinner = () => (
  <div className="min-h-screen flex items-center justify-center">
    <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
  </div>
);

// 비인증 사용자 접근 차단
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();
  if (isLoading) return <LoadingSpinner />;
  if (!user) return <Navigate to="/" replace />;
  return <>{children}</>;
}

// 인증 상태에 따라 로그인 또는 서비스 선택 페이지로 분기
function RootRedirect() {
  const { user, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && user) {
      const providerLabel = user.provider === "kakao" ? "카카오" : "네이버";
      toast.info(`이미 ${providerLabel} 로그인이 되어있습니다.`);
    }
  }, [isLoading, user]);

  if (isLoading) return <LoadingSpinner />;
  if (user) return <Navigate to="/select-service" replace />;
  return <LoginPage />;
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<RootRedirect />} />
          <Route path="/login.html" element={<RootRedirect />} />
          <Route
            path="/select-service"
            element={
              <ProtectedRoute>
                <ServiceSelectPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/survey"
            element={
              <ProtectedRoute>
                <SurveyPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
        </Routes>
        <Toaster position="top-center" />
      </AuthProvider>
    </BrowserRouter>
  );
}
