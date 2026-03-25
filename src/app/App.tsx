import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { Toaster } from "./components/ui/sonner";
import { LoginPage } from "./components/LoginPage";
import { ServiceSelectPage } from "./components/ServiceSelectPage";
import { SurveyPage } from "./components/SurveyPage";
import { DashboardPage } from "./components/DashboardPage";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route path="/select-service" element={<ServiceSelectPage />} />
          <Route path="/survey" element={<SurveyPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
        </Routes>
        <Toaster position="top-center" />
      </AuthProvider>
    </BrowserRouter>
  );
}
