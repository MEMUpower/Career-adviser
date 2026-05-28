"use client";

import React, { useState, useEffect } from "react";
import FileUploader from "@/components/FileUploader";
import api from "@/lib/api";
import { Loader2, FileSearch, Sparkles, Trophy, AlertTriangle } from "lucide-react";

export default function UploadPage() {
  const [recordId, setRecordId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>("PENDING");
  const [errorDetail, setErrorDetail] = useState<string | null>(null);
  const [authChecked, setAuthChecked] = useState(false);

  // Auth guard: redirect to /login if no token
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      window.location.href = "/login";
    } else {
      setAuthChecked(true);
    }
  }, []);

  // Hook to poll parsing status
  useEffect(() => {
    if (!recordId) return;

    const interval = setInterval(async () => {
      try {
        const res = await api.get(`/records/${recordId}`);
        const currentStatus = res.data.status;
        setStatus(currentStatus);

        if (currentStatus === "COMPLETED") {
          clearInterval(interval);
          // Redirect to dashboard on completion
          window.location.href = `/dashboard/${recordId}`;
        } else if (currentStatus === "FAILED") {
          clearInterval(interval);
          setErrorDetail(res.data.error_detail?.detail || "분석 프로세스 중 에러가 발생했습니다.");
        }
      } catch (err) {
        clearInterval(interval);
        setStatus("FAILED");
        setErrorDetail("상태 정보를 받아오는 도중 통신 장애가 발생했습니다.");
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [recordId]);

  const handleUploadSuccess = (id: string) => {
    setRecordId(id);
    setStatus("PENDING");
  };

  // Status mapping
  const getStatusConfig = () => {
    switch (status) {
      case "PENDING":
        return {
          step: 1,
          label: "대기 중",
          desc: "대기열에 등록 중입니다. 곧 파일 구조 해체에 진입합니다.",
          icon: <Loader2 className="animate-spin text-indigo-500" size={36} />,
          percent: 15,
        };
      case "PARSING":
        return {
          step: 2,
          label: "생기부 텍스트 분리 및 비식별화",
          desc: "PDF 텍스트를 추출하고 교과, 세특, 창체, 독서, 수상 영역을 인지하여 비식별화(마스킹)합니다.",
          icon: <FileSearch className="text-cyan-500 animate-pulse" size={36} />,
          percent: 40,
        };
      case "TAGGING":
        return {
          step: 3,
          label: "학생 역량 지표 태깅 및 스코어링",
          desc: "탐구력, 협업, 의사소통, 자기주도성 점수를 생성하고 관심사 핵심 키워드를 추출합니다.",
          icon: <Sparkles className="text-purple-500 animate-bounce" size={36} />,
          percent: 65,
        };
      case "RECOMMENDING":
        return {
          step: 4,
          label: "공공데이터 융합 및 맞춤 추천 생성",
          desc: "전공 취업률, 직무 전망 지표 및 가중치 설정을 결합하여 최적 전공/직무 시나리오를 구성합니다.",
          icon: <Trophy className="text-yellow-500 animate-pulse" size={36} />,
          percent: 85,
        };
      default:
        return {
          step: 0,
          label: "준비 완료",
          desc: "대기 중",
          icon: null,
          percent: 0,
        };
    }
  };

  const statusConfig = getStatusConfig();

  if (!authChecked) {
    return (
      <div className="flex justify-center items-center min-h-[70vh]">
        <Loader2 className="animate-spin text-indigo-500" size={48} />
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto py-8 sm:py-12">
      <div className="absolute top-1/4 left-1/2 -z-10 h-64 w-64 -translate-x-1/2 rounded-full bg-indigo-500/5 blur-[100px]" />
      
      {!recordId ? (
        <FileUploader onUploadSuccess={handleUploadSuccess} />
      ) : (
        <div className="glass-panel p-8 sm:p-10 text-center">
          {status === "FAILED" ? (
            <div className="flex flex-col items-center animate-fade-in">
              <div className="mb-4 p-4 bg-red-500/10 text-red-500 rounded-full">
                <AlertTriangle size={36} />
              </div>
              <h3 className="text-2xl font-bold mb-2">분석이 중단되었습니다</h3>
              <p className="text-sm text-muted mb-6 max-w-md">{errorDetail}</p>
              <button
                onClick={() => setRecordId(null)}
                className="neu-button font-bold text-sm"
              >
                다시 업로드하기
              </button>
            </div>
          ) : (
            <div className="flex flex-col items-center">
              <div className="mb-6 p-5 bg-indigo-500/5 dark:bg-indigo-950/40 rounded-full border border-indigo-500/10">
                {statusConfig.icon}
              </div>
              <h3 className="text-2xl font-extrabold mb-1">
                AI 분석 파이프라인 작동 중
              </h3>
              <span className="text-sm font-semibold text-indigo-600 dark:text-indigo-400 mb-4 block">
                {statusConfig.label} ({statusConfig.percent}%)
              </span>
              <p className="text-xs sm:text-sm text-muted leading-relaxed max-w-md mb-8">
                {statusConfig.desc}
              </p>

              {/* Progress Gauge */}
              <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-3 max-w-md mb-3 overflow-hidden border border-slate-200/50 dark:border-slate-700/30">
                <div
                  className="bg-gradient-to-r from-indigo-500 to-cyan-400 h-full rounded-full transition-all duration-1000 ease-out"
                  style={{ width: `${statusConfig.percent}%` }}
                />
              </div>
              <span className="text-[11px] text-muted block">
                평균 분석 소요 시간은 약 10초~20초입니다. 페이지를 이동하지 마십시오.
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
