"use client";

import React from "react";
import { Sparkles, Shield, Database, BarChart3, ArrowRight } from "lucide-react";
import { withBasePath } from "@/lib/path";

export default function LandingPage() {
  return (
    <div className="relative flex flex-col items-center justify-center py-10 md:py-16">
      <div className="absolute top-1/4 left-1/2 -z-10 h-72 w-72 -translate-x-1/2 rounded-full bg-indigo-500/10 blur-[100px]" />
      <div className="absolute top-1/3 left-1/4 -z-10 h-60 w-60 rounded-full bg-cyan-500/10 blur-[80px]" />

      <div className="mb-6 inline-flex items-center gap-1.5 rounded-full bg-indigo-50/80 dark:bg-indigo-950/40 border border-indigo-100 dark:border-indigo-900/50 px-4 py-1.5 text-xs font-semibold text-indigo-600 dark:text-indigo-400">
        <Sparkles size={14} className="animate-pulse" />
        AI 기반 생기부 분석과 공공데이터 진로 추천
      </div>

      <h1 className="mb-6 max-w-4xl text-center text-4xl font-extrabold leading-tight tracking-tight sm:text-5xl md:text-6xl">
        생기부를 바탕으로
        <br />
        <span className="bg-gradient-to-r from-indigo-500 via-purple-500 to-cyan-500 bg-clip-text text-transparent">
          전공과 직무를 함께 추천
        </span>
        합니다.
      </h1>

      <p className="text-muted mb-10 max-w-2xl text-center text-sm leading-relaxed sm:text-base">
        학생의 교과 성취, 세특, 창체, 독서, 진로 활동을 분석하고, 공공데이터를 결합해 적합한 대학 전공과 직무군을 설명 가능한 형태로 제안합니다.
      </p>

      <div className="mb-16 flex flex-col gap-4 sm:flex-row">
        <a href={withBasePath("/upload")} className="neu-button neu-brand group px-8 py-4 text-sm font-bold shadow-lg">
          분석 시작하기
          <ArrowRight size={16} className="transition-transform group-hover:translate-x-1" />
        </a>
        <a href={withBasePath("/login")} className="neu-button px-8 py-4 text-sm font-bold text-muted">
          로그인 / 회원가입
        </a>
      </div>

      <div className="grid w-full max-w-5xl grid-cols-1 gap-6 text-left md:grid-cols-3">
        <div className="glass-panel p-6">
          <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-500/10 text-indigo-600 dark:text-indigo-400">
            <Shield size={22} />
          </div>
          <h3 className="mb-2 text-lg font-bold">개인정보 비식별화</h3>
          <p className="text-muted text-sm leading-relaxed">
            이름, 학번 등 민감 정보는 최소한으로 다루고, 분석 결과는 필요한 범위만 보여주도록 설계했습니다.
          </p>
        </div>

        <div className="glass-panel p-6">
          <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-cyan-500/10 text-cyan-600 dark:text-cyan-400">
            <Database size={22} />
          </div>
          <h3 className="mb-2 text-lg font-bold">공공데이터 연동</h3>
          <p className="text-muted text-sm leading-relaxed">
            KOSIS, data.go.kr 등 공공데이터를 활용해 전공별 취업률과 직무 전망을 함께 반영합니다.
          </p>
        </div>

        <div className="glass-panel p-6">
          <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400">
            <BarChart3 size={22} />
          </div>
          <h3 className="mb-2 text-lg font-bold">근거 중심 추천</h3>
          <p className="text-muted text-sm leading-relaxed">
            추천 이유와 생기부 근거를 함께 보여줘서, 왜 이 전공과 직무가 어울리는지 바로 이해할 수 있습니다.
          </p>
        </div>
      </div>
    </div>
  );
}
