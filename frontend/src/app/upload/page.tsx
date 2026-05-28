"use client";

import React, { useEffect, useState } from "react";
import FileUploader from "@/components/FileUploader";
import api from "@/lib/api";
import { Loader2, FileSearch, Sparkles, Trophy, AlertTriangle } from "lucide-react";
import { withBasePath } from "@/lib/path";

export default function UploadPage() {
  const [recordId, setRecordId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>("PENDING");
  const [errorDetail, setErrorDetail] = useState<string | null>(null);
  const [authChecked, setAuthChecked] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      window.location.href = withBasePath("/login");
      return;
    }
    setAuthChecked(true);
  }, []);

  useEffect(() => {
    if (!recordId) return;

    const interval = setInterval(async () => {
      try {
        const res = await api.get(`/records/${recordId}`);
        const currentStatus = res.data.status;
        setStatus(currentStatus);

        if (currentStatus === "COMPLETED") {
          clearInterval(interval);
          window.location.href = withBasePath(`/dashboard?recordId=${encodeURIComponent(recordId)}`);
        } else if (currentStatus === "FAILED") {
          clearInterval(interval);
          setErrorDetail(res.data.error_detail?.detail || "분석 프로세스에서 오류가 발생했습니다.");
        }
      } catch {
        clearInterval(interval);
        setStatus("FAILED");
        setErrorDetail("상태 정보를 불러오는 중 오류가 발생했습니다.");
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [recordId]);

  const handleUploadSuccess = (id: string) => {
    setRecordId(id);
    setStatus("PENDING");
  };

  const getStatusConfig = () => {
    switch (status) {
      case "PENDING":
        return {
          label: "대기 중",
          desc: "업로드된 파일을 확인하고 분석을 준비하고 있습니다.",
          icon: <Loader2 className="animate-spin text-indigo-500" size={36} />,
          percent: 15,
        };
      case "PARSING":
        return {
          label: "텍스트 분리 및 전처리",
          desc: "PDF 텍스트 추출과 OCR을 통해 생기부 내용을 구조화하고 있습니다.",
          icon: <FileSearch className="animate-pulse text-cyan-500" size={36} />,
          percent: 40,
        };
      case "TAGGING":
        return {
          label: "역량 태깅",
          desc: "관심사와 역량을 추출하여 학생 프로필을 생성하고 있습니다.",
          icon: <Sparkles className="animate-bounce text-purple-500" size={36} />,
          percent: 65,
        };
      case "RECOMMENDING":
        return {
          label: "추천 생성",
          desc: "공공데이터와 분석 결과를 결합해 전공과 직무 추천을 만들고 있습니다.",
          icon: <Trophy className="animate-pulse text-yellow-500" size={36} />,
          percent: 85,
        };
      default:
        return {
          label: "준비 완료",
          desc: "",
          icon: null,
          percent: 0,
        };
    }
  };

  const statusConfig = getStatusConfig();

  if (!authChecked) {
    return (
      <div className="flex min-h-[70vh] items-center justify-center">
        <Loader2 className="animate-spin text-indigo-500" size={48} />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl py-8 sm:py-12">
      <div className="absolute top-1/4 left-1/2 -z-10 h-64 w-64 -translate-x-1/2 rounded-full bg-indigo-500/5 blur-[100px]" />

      {!recordId ? (
        <FileUploader onUploadSuccess={handleUploadSuccess} />
      ) : (
        <div className="glass-panel p-8 text-center sm:p-10">
          {status === "FAILED" ? (
            <div className="flex flex-col items-center animate-fade-in">
              <div className="mb-4 rounded-full bg-red-500/10 p-4 text-red-500">
                <AlertTriangle size={36} />
              </div>
              <h3 className="mb-2 text-2xl font-bold">분석이 중단되었습니다</h3>
              <p className="mb-6 max-w-md text-sm text-muted">{errorDetail}</p>
              <button onClick={() => setRecordId(null)} className="neu-button font-bold text-sm">
                다시 업로드하기
              </button>
            </div>
          ) : (
            <div className="flex flex-col items-center">
              <div className="mb-6 rounded-full border border-indigo-500/10 bg-indigo-500/5 p-5 dark:bg-indigo-950/40">
                {statusConfig.icon}
              </div>
              <h3 className="mb-1 text-2xl font-extrabold">AI 분석이 진행 중입니다</h3>
              <span className="mb-4 block text-sm font-semibold text-indigo-600 dark:text-indigo-400">
                {statusConfig.label} ({statusConfig.percent}%)
              </span>
              <p className="mb-8 max-w-md text-xs leading-relaxed text-muted sm:text-sm">{statusConfig.desc}</p>

              <div className="mb-3 h-3 w-full max-w-md overflow-hidden rounded-full border border-slate-200/50 bg-slate-100 dark:border-slate-700/30 dark:bg-slate-800">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-cyan-400 transition-all duration-1000 ease-out"
                  style={{ width: `${statusConfig.percent}%` }}
                />
              </div>
              <span className="block text-[11px] text-muted">
                분석에는 보통 10초에서 20초 정도 걸립니다. 잠시만 기다려 주세요.
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
