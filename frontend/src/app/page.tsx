"use client";

import React from "react";
import { Sparkles, Shield, Database, BarChart3, GraduationCap, ArrowRight } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="flex flex-col items-center justify-center py-10 md:py-16">
      {/* Background decoration elements */}
      <div className="absolute top-1/4 left-1/2 -z-10 h-72 w-72 -translate-x-1/2 rounded-full bg-indigo-500/10 blur-[100px]" />
      <div className="absolute top-1/3 left-1/4 -z-10 h-60 w-60 rounded-full bg-cyan-500/10 blur-[80px]" />

      <div className="mb-6 inline-flex items-center gap-1.5 rounded-full bg-indigo-50/80 dark:bg-indigo-950/40 border border-indigo-100 dark:border-indigo-900/50 px-4 py-1.5 text-xs font-semibold text-indigo-600 dark:text-indigo-400">
        <Sparkles size={14} className="animate-pulse" />
        AI & 공공데이터 기반 융합형 진로 설계 어드바이저
      </div>

      <h1 className="mb-6 max-w-4xl text-4xl font-extrabold leading-tight tracking-tight sm:text-5xl md:text-6xl text-center">
        학교생활기록부 업로드 한 번으로
        <br />
        <span className="bg-gradient-to-r from-indigo-500 via-purple-500 to-cyan-500 bg-clip-text text-transparent">
          최적의 대학 전공과 직무군
        </span>
        을 추천받으세요.
      </h1>

      <p className="text-muted mb-10 max-w-2xl text-center text-sm sm:text-base leading-relaxed">
        학생의 교과 성취도, 세부능력 및 특기사항(세특), 독서, 동아리 활동을 정밀 분석하고,
        KOSIS 취업 통계 및 워크넷 시장 전망 데이터를 결합하여 신뢰성 높은 최적의 진로 설계를 제안합니다.
      </p>

      <div className="mb-16 flex flex-col sm:flex-row gap-4">
        <a href="/upload" className="neu-button neu-brand px-8 py-4 font-bold text-sm shadow-lg group">
          생활기록부 무료 분석 시작하기
          <ArrowRight size={16} className="transition-transform group-hover:translate-x-1" />
        </a>
        <a href="/login" className="neu-button px-8 py-4 font-bold text-sm text-muted">
          로그인 / 회원가입
        </a>
      </div>

      {/* Feature cards section */}
      <div className="grid w-full max-w-5xl grid-cols-1 gap-6 text-left md:grid-cols-3">
        <div className="glass-panel p-6">
          <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-500/10 text-indigo-600 dark:text-indigo-400">
            <Shield size={22} />
          </div>
          <h3 className="mb-2 text-lg font-bold">강력한 개인정보 비식별화</h3>
          <p className="text-muted text-xs sm:text-sm leading-relaxed">
            이름, 학번, 학교명과 같은 민감 정보는 브라우저 업로드 시 자동 탐지되어 안전하게 마스킹 처리 후 암호화 분석을 실행합니다.
          </p>
        </div>

        <div className="glass-panel p-6">
          <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-cyan-500/10 text-cyan-600 dark:text-cyan-400">
            <Database size={22} />
          </div>
          <h3 className="mb-2 text-lg font-bold">공공데이터 실시간 융합</h3>
          <p className="text-muted text-xs sm:text-sm leading-relaxed">
            KOSIS 학과별 취업률 및 워크넷 일자리 전망 등 공공 OpenAPI 지표를 실시간 반영하여 객관적 진로 적합도 스코어를 산출합니다.
          </p>
        </div>

        <div className="glass-panel p-6">
          <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400">
            <BarChart3 size={22} />
          </div>
          <h3 className="mb-2 text-lg font-bold">근거 기반 팩트 하이라이트</h3>
          <p className="text-muted text-xs sm:text-sm leading-relaxed">
            추천 전공 및 직무의 타당성을 입증하는 생활기록부 원문의 구체적인 문장들을 발췌하여 설명력 있는 보고서를 자동 구성합니다.
          </p>
        </div>
      </div>
    </div>
  );
}
