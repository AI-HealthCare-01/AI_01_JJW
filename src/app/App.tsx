import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { Toaster } from "./components/ui/sonner";
import { LoginPage } from "./components/LoginPage";
import { ServiceSelectPage } from "./components/ServiceSelectPage";
import { SurveyPage } from "./components/SurveyPage";
import { DashboardPage } from "./components/DashboardPage";
import { Loader2 } from "lucide-react";

// 인증 상태에 따라 로그인 또는 서비스 선택 페이지로 분기
function RootRedirect() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return user ? <Navigate to="/select-service" replace /> : <LoginPage />;
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* / 와 /login.html 모두 인증 상태 기반 분기 */}
          <Route path="/" element={<RootRedirect />} />
          <Route path="/login.html" element={<RootRedirect />} />
          <Route path="/select-service" element={<ServiceSelectPage />} />
          <Route path="/survey" element={<SurveyPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
        </Routes>
        <Toaster position="top-center" />
      </AuthProvider>
    </BrowserRouter>
  );
}
