"use client";

import React, { useState } from "react";
import { Lock, Mail, User as UserIcon, AlertCircle, CheckCircle } from "lucide-react";
import api from "@/lib/api";
import { withBasePath } from "@/lib/path";

export default function LoginPage() {
  const [isSignup, setIsSignup] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("student");
  const [maskedName, setMaskedName] = useState("");
  const [grade, setGrade] = useState("2학년");
  const [schoolType, setSchoolType] = useState("일반고");
  const [region, setRegion] = useState("서울");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    try {
      if (isSignup) {
        await api.post("/auth/signup", {
          email,
          password,
          role,
          masked_name: maskedName || "학생",
          grade,
          school_type: schoolType,
          region,
        });
        setSuccess("회원가입이 완료되었습니다. 로그인해 주세요.");
        setIsSignup(false);
        return;
      }

      const response = await api.post("/auth/login", { email, password });
      localStorage.setItem("token", response.data.access_token);
      localStorage.setItem("role", role);
      window.location.href = withBasePath("/upload");
    } catch (err: any) {
      setError(err.response?.data?.detail || "요청 처리 중 오류가 발생했습니다.");
    }
  };

  return (
    <div className="flex min-h-[75vh] items-center justify-center py-6">
      <div className="absolute top-1/3 left-1/2 -z-10 h-64 w-64 -translate-x-1/2 rounded-full bg-indigo-500/10 blur-[100px]" />

      <div className="glass-panel w-full max-w-lg p-8 sm:p-10">
        <h2 className="mb-2 text-center text-3xl font-extrabold tracking-tight">
          {isSignup ? "회원가입" : "로그인"}
        </h2>
        <p className="text-muted mb-8 text-center text-sm">
          {isSignup
            ? "학생 또는 교사 계정을 만들고 맞춤형 진로 분석을 시작해 보세요."
            : "생기부 분석과 진로 추천 서비스를 바로 이용할 수 있습니다."}
        </p>

        {error && (
          <div className="mb-6 flex items-start gap-2.5 rounded-xl border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-500">
            <AlertCircle size={16} className="mt-0.5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="mb-6 flex items-start gap-2.5 rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-3 text-sm text-emerald-500">
            <CheckCircle size={16} className="mt-0.5 shrink-0" />
            <span>{success}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="text-muted mb-1.5 block text-xs font-bold uppercase tracking-wider">이메일</label>
            <div className="relative">
              <Mail className="text-muted absolute left-3.5 top-3.5" size={16} />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-xl border border-slate-200 bg-white/60 py-3 pl-11 pr-4 text-sm outline-none transition-all focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 dark:border-slate-800 dark:bg-slate-900/60"
                placeholder="example@school.com"
              />
            </div>
          </div>

          <div>
            <label className="text-muted mb-1.5 block text-xs font-bold uppercase tracking-wider">비밀번호</label>
            <div className="relative">
              <Lock className="text-muted absolute left-3.5 top-3.5" size={16} />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-xl border border-slate-200 bg-white/60 py-3 pl-11 pr-4 text-sm outline-none transition-all focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 dark:border-slate-800 dark:bg-slate-900/60"
                placeholder="비밀번호를 입력하세요"
              />
            </div>
          </div>

          {isSignup && (
            <div className="space-y-4 border-t border-slate-200 pt-2 dark:border-slate-800">
              <div>
                <label className="text-muted mb-1.5 block text-xs font-bold uppercase tracking-wider">계정 역할</label>
                <div className="relative">
                  <UserIcon className="text-muted absolute left-3.5 top-3.5" size={16} />
                  <select
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    className="w-full appearance-none rounded-xl border border-slate-200 bg-white/60 py-3 pl-11 pr-4 text-sm outline-none transition-all focus:border-indigo-500 dark:border-slate-800 dark:bg-slate-900/60"
                  >
                    <option value="student">학생</option>
                    <option value="teacher">교사</option>
                  </select>
                </div>
              </div>

              {role === "student" && (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-muted mb-1.5 block text-xs font-bold">이름(마스킹)</label>
                    <input
                      type="text"
                      required
                      value={maskedName}
                      onChange={(e) => setMaskedName(e.target.value)}
                      className="w-full rounded-xl border border-slate-200 bg-white/60 px-4 py-3 text-sm outline-none transition-all focus:border-indigo-500 dark:border-slate-800 dark:bg-slate-900/60"
                      placeholder="홍길동"
                    />
                  </div>

                  <div>
                    <label className="text-muted mb-1.5 block text-xs font-bold">학년</label>
                    <select
                      value={grade}
                      onChange={(e) => setGrade(e.target.value)}
                      className="w-full rounded-xl border border-slate-200 bg-white/60 px-4 py-3 text-sm outline-none transition-all focus:border-indigo-500 dark:border-slate-800 dark:bg-slate-900/60"
                    >
                      <option value="1학년">1학년</option>
                      <option value="2학년">2학년</option>
                      <option value="3학년">3학년</option>
                    </select>
                  </div>

                  <div>
                    <label className="text-muted mb-1.5 block text-xs font-bold">학교 유형</label>
                    <select
                      value={schoolType}
                      onChange={(e) => setSchoolType(e.target.value)}
                      className="w-full rounded-xl border border-slate-200 bg-white/60 px-4 py-3 text-sm outline-none transition-all focus:border-indigo-500 dark:border-slate-800 dark:bg-slate-900/60"
                    >
                      <option value="일반고">일반고</option>
                      <option value="특목고">특목고</option>
                      <option value="자사고">자사고</option>
                    </select>
                  </div>

                  <div>
                    <label className="text-muted mb-1.5 block text-xs font-bold">지역</label>
                    <select
                      value={region}
                      onChange={(e) => setRegion(e.target.value)}
                      className="w-full rounded-xl border border-slate-200 bg-white/60 px-4 py-3 text-sm outline-none transition-all focus:border-indigo-500 dark:border-slate-800 dark:bg-slate-900/60"
                    >
                      <option value="서울">서울</option>
                      <option value="경기">경기</option>
                      <option value="인천">인천</option>
                      <option value="부산">부산</option>
                      <option value="광주">광주</option>
                      <option value="대구">대구</option>
                    </select>
                  </div>
                </div>
              )}
            </div>
          )}

          <button type="submit" className="neu-button neu-brand mt-4 w-full py-3.5 text-sm font-bold shadow-md">
            {isSignup ? "회원가입하기" : "로그인"}
          </button>
        </form>

        <div className="mt-8 border-t border-slate-200 pt-6 text-center dark:border-slate-800/80">
          <button
            onClick={() => {
              setIsSignup(!isSignup);
              setError(null);
              setSuccess(null);
            }}
            className="text-xs font-semibold text-indigo-600 hover:underline dark:text-indigo-400"
          >
            {isSignup ? "이미 계정이 있으신가요? 로그인" : "계정이 없으신가요? 회원가입"}
          </button>
        </div>
      </div>
    </div>
  );
}
