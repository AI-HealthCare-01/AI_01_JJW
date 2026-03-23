import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { Button } from "./ui/button";
import { Progress } from "./ui/progress";
import { Input } from "./ui/input";
import {
  surveyQuestions,
  surveyCategories,
} from "../data/surveyQuestions";
import {
  ArrowLeft,
  ArrowRight,
  Send,
  Activity,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { submitSurvey } from "../services/api";
import { toast } from "sonner";

const QUESTIONS_PER_PAGE = 5;

export const SurveyPage: React.FC = () => {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [answers, setAnswers] = useState<
    Record<string, string>
  >({});
  const [currentPage, setCurrentPage] = useState(0);
  // 페이지 번호가 바뀔 때마다 실행
  useEffect(() => {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }, [currentPage]); // [currentPage]는 이 값이 바뀔 때마다 실행하라는 뜻입니다.
  const [submitting, setSubmitting] = useState(false);

  const totalPages = Math.ceil(
    surveyQuestions.length / QUESTIONS_PER_PAGE,
  );
  const currentQuestions = surveyQuestions.slice(
    currentPage * QUESTIONS_PER_PAGE,
    (currentPage + 1) * QUESTIONS_PER_PAGE,
  );
  const progress = ((currentPage + 1) / totalPages) * 100;
  const answeredCount = Object.keys(answers).length;

  const currentCategory = currentQuestions[0]?.category || "";

  const handleAnswer = (variable: string, value: string) => {
    setAnswers((prev) => ({ ...prev, [variable]: value }));
  };

  const canProceed = currentQuestions.every(
    (q) =>
      answers[q.variable] !== undefined &&
      answers[q.variable] !== "",
  );

  const handleNextPage = () => {
    if (!canProceed) {
      toast.error("현재 페이지의 모든 질문에 답변해 주세요.");
      return;
    }
    setCurrentPage((p) => p + 1);
    // 페이지 최상단으로 스크롤
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handlePrevPage = () => {
    setCurrentPage((p) => p - 1);
    // 페이지 최상단으로 스크롤
    // 상태만 변경하면 useEffect가 감지함
  };

  const handleAutoFill = () => {
    // 테스트용 자동 입력 데이터
    const autoFillData: Record<string, string> = {};
    surveyQuestions.forEach((q) => {
      if (q.type === "select" && q.options) {
        // 랜덤하게 옵션 선택
        const randomOption =
          q.options[
            Math.floor(Math.random() * q.options.length)
          ];
        autoFillData[q.variable] = randomOption.value;
      } else if (q.type === "number") {
        // 중간값 입력
        const min = q.min || 0;
        const max = q.max || 100;
        const midValue = Math.floor((min + max) / 2);
        autoFillData[q.variable] = midValue.toString();
      }
    });
    setAnswers(autoFillData);
    toast.success("테스트 데이터가 자동으로 입력되었습니다!");
  };

  const handleAutoFillAndSubmit = async () => {
    // 자동 입력
    const autoFillData: Record<string, string> = {};
    surveyQuestions.forEach((q) => {
      if (q.type === "select" && q.options) {
        const randomOption =
          q.options[
            Math.floor(Math.random() * q.options.length)
          ];
        autoFillData[q.variable] = randomOption.value;
      } else if (q.type === "number") {
        const min = q.min || 0;
        const max = q.max || 100;
        const midValue = Math.floor((min + max) / 2);
        autoFillData[q.variable] = midValue.toString();
      }
    });
    setAnswers(autoFillData);

    // 바로 제출
    setSubmitting(true);
    try {
      const result = await submitSurvey(autoFillData);
      navigate("/dashboard", { state: { result } });
    } catch (error) {
      console.error("설문 제출 오류:", error);
      toast.error(
        "설문 제출에 실패했습니다. 다시 시도해 주세요.",
      );
      setSubmitting(false);
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);

    try {
      // API 서비스를 통해 서버에 설문 데이터 전송 및 결과 수신
      const result = await submitSurvey(answers);

      // 성공 시 대시보드로 이동
      navigate("/dashboard", { state: { result } });
    } catch (error) {
      console.error("설문 제출 오류:", error);
      toast.error(
        "설문 제출에 실패했습니다. 다시 시도해 주세요.",
      );
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      {/* Header */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-3xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
              <Activity className="h-4 w-4 text-white" />
            </div>
            <span className="text-gray-900">
              만성질환 예측 설문
            </span>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-500">
              {answeredCount}/80 응답
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                logout();
                navigate("/");
              }}
            >
              나가기
            </Button>
          </div>
        </div>
        <div className="max-w-3xl mx-auto px-4 pb-3">
          <div className="flex items-center justify-between text-sm text-gray-500 mb-1">
            <span>{currentCategory}</span>
            <span>
              {currentPage + 1} / {totalPages} 페이지
            </span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>
      </div>

      {/* Questions */}
      <div className="max-w-3xl mx-auto px-4 py-6">
        {/* 테스트용 자동 입력 버튼 */}
        {currentPage === 0 && answeredCount < 80 && (
          <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-yellow-800 mb-1">
                  <strong>테스트 모드:</strong> 빠르게
                  대시보드를 확인하고 싶으신가요?
                </p>
                <p className="text-xs text-yellow-600">
                  80개 문항에 랜덤 데이터를 자동으로 입력하고
                  바로 분석합니다.
                </p>
              </div>
              <div className="flex gap-2 ml-4">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={handleAutoFill}
                  className="border-yellow-400 text-yellow-700 hover:bg-yellow-100"
                >
                  자동 입력
                </Button>
                <Button
                  size="sm"
                  onClick={handleAutoFillAndSubmit}
                  disabled={submitting}
                  className="bg-yellow-600 hover:bg-yellow-700 text-white"
                >
                  {submitting
                    ? "분석 중..."
                    : "자동 입력 & 분석"}
                </Button>
              </div>
            </div>
          </div>
        )}

        <div className="space-y-4">
          {currentQuestions.map((q, idx) => (
            <Card key={q.id} className="border">
              <CardHeader className="pb-3">
                <CardTitle className="text-base flex gap-2">
                  <span className="text-blue-600 flex-shrink-0">
                    Q{q.id}.
                  </span>
                  <span>{q.question}</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {q.type === "select" && q.options ? (
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                    {q.options.map((opt) => (
                      <button
                        key={opt.value}
                        onClick={() =>
                          handleAnswer(q.variable, opt.value)
                        }
                        className={`px-3 py-2 rounded-lg border text-sm transition-all ${
                          answers[q.variable] === opt.value
                            ? "bg-blue-600 text-white border-blue-600"
                            : "bg-white text-gray-700 border-gray-200 hover:border-blue-300 hover:bg-blue-50"
                        }`}
                      >
                        {opt.label}
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <Input
                      type="number"
                      placeholder={q.placeholder}
                      value={answers[q.variable] || ""}
                      onChange={(e) =>
                        handleAnswer(q.variable, e.target.value)
                      }
                      min={q.min}
                      max={q.max}
                      className="max-w-[200px]"
                    />
                    {q.unit && (
                      <span className="text-sm text-gray-500">
                        {q.unit}
                      </span>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Navigation */}
        <div className="flex items-center justify-between mt-8 pb-8">
          <Button
            variant="outline"
            onClick={handlePrevPage}
            disabled={currentPage === 0}
          >
            <ArrowLeft className="h-4 w-4 mr-1" /> 이전
          </Button>

          {currentPage === totalPages - 1 ? (
            <Button
              onClick={handleSubmit}
              disabled={answeredCount < 80 || submitting}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {submitting ? (
                <>분석 중...</>
              ) : (
                <>
                  <Send className="h-4 w-4 mr-1" /> 설문 제출 및
                  분석
                </>
              )}
            </Button>
          ) : (
            <Button onClick={handleNextPage}>
              다음 <ArrowRight className="h-4 w-4 ml-1" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};