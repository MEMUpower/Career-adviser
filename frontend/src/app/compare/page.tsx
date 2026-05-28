"use client";

import React, { useState } from "react";
import { Scale, ArrowRight, BookOpen, AlertCircle, Award, Target, CheckCircle2, TrendingUp } from "lucide-react";

const COMPARISON_SCENARIOS = {
  "컴퓨터공학과": {
    employmentRate: "78.5%",
    growth: "매우높음",
    keySubject: "수학II, 미적분, 확률과 통계, 정보, 인공지능 기초",
    difficulty: "매우 높음 (소프트웨어 개발 포트폴리오 및 깃허브 실적 필수)",
    actionPlan: "아두이노 하드웨어 센서 제어 실습 및 심화 신경망 기초 탐구 보고서",
    pros: "IT/플랫폼 융합 산업의 기하급수적 인력 수요 및 글로벌 커리어 확장",
  },
  "전자공학과": {
    employmentRate: "76.2%",
    growth: "높음",
    keySubject: "물리학I/II, 미적분, 기하, 화학I",
    difficulty: "높음 (반도체/전자회로 설계 프로젝트 및 고난도 실험 물리 증명)",
    actionPlan: "전기회로 기본 이론 학습 및 브레드보드 디지털 논리회로 실습 보고서 작성",
    pros: "국내 대기업 반도체/지능형 모빌리티 제조 벨트 연구직 채용 우대",
  },
  "화학공학과": {
    employmentRate: "71.0%",
    growth: "보통",
    keySubject: "화학I/II, 수학II, 영어, 생명과학I",
    difficulty: "보통 (소재 물리화학 반응 데이터 수립 및 분자 구조 3D 시뮬레이션)",
    actionPlan: "나노 신소재 실험 참여 및 배터리 전해액 기초 전기화학 반응식 모델링",
    pros: "2차전지, 친환경 에너지 솔루션 및 바이오 신약 융합 인프라 진입 용이",
  }
};

export default function ComparePage() {
  const [leftTrack, setLeftTrack] = useState<keyof typeof COMPARISON_SCENARIOS>("컴퓨터공학과");
  const [rightTrack, setRightTrack] = useState<keyof typeof COMPARISON_SCENARIOS>("전자공학과");

  const leftData = COMPARISON_SCENARIOS[leftTrack];
  const rightData = COMPARISON_SCENARIOS[rightTrack];

  return (
    <div className="space-y-8 max-w-4xl mx-auto py-4">
      {/* Header */}
      <div className="glass-panel p-6 sm:p-8">
        <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight flex items-center gap-2">
          <Scale className="text-indigo-500" size={24} />
          진로 시나리오 양방향 비교
        </h2>
        <p className="text-xs sm:text-sm text-muted mt-1">
          서로 다른 추천 전공 시나리오의 취업률 통계와 교과 이수 권장 과목을 실시간으로 비교 대조해 보세요.
        </p>
      </div>

      {/* Selectors grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 p-6 glass-panel">
        <div>
          <label className="block text-xs font-bold text-muted uppercase tracking-wider mb-2">비교 대상 A</label>
          <select
            value={leftTrack}
            onChange={(e) => setLeftTrack(e.target.value as any)}
            className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl py-3 px-4 text-sm text-slate-800 dark:text-slate-200 focus:outline-none focus:border-indigo-500 transition-all appearance-none"
          >
            {Object.keys(COMPARISON_SCENARIOS).map((name) => (
              <option key={name} value={name}>{name}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-bold text-muted uppercase tracking-wider mb-2">비교 대상 B</label>
          <select
            value={rightTrack}
            onChange={(e) => setRightTrack(e.target.value as any)}
            className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl py-3 px-4 text-sm text-slate-800 dark:text-slate-200 focus:outline-none focus:border-indigo-500 transition-all appearance-none"
          >
            {Object.keys(COMPARISON_SCENARIOS).map((name) => (
              <option key={name} value={name}>{name}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Comparison Grid */}
      <div className="glass-panel overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/60">
                <th className="p-4 text-xs font-bold text-muted uppercase tracking-wider w-1/4">평가 지표</th>
                <th className="p-4 text-sm font-extrabold text-indigo-600 dark:text-indigo-400 text-center w-3/8 bg-indigo-500/5">
                  {leftTrack}
                </th>
                <th className="p-4 text-sm font-extrabold text-cyan-600 dark:text-cyan-400 text-center w-3/8">
                  {rightTrack}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/80">
              <tr>
                <td className="p-4 font-semibold text-slate-600 dark:text-slate-400 flex items-center gap-1.5">
                  <Target size={14} className="text-indigo-500" />
                  평균 취업률
                </td>
                <td className="p-4 text-center font-bold text-slate-800 dark:text-white bg-indigo-500/5">{leftData.employmentRate}</td>
                <td className="p-4 text-center font-bold text-slate-800 dark:text-white">{rightData.employmentRate}</td>
              </tr>
              <tr>
                <td className="p-4 font-semibold text-slate-600 dark:text-slate-400 flex items-center gap-1.5">
                  <TrendingUp size={14} className="text-indigo-500" />
                  직무 성장 전망
                </td>
                <td className="p-4 text-center bg-indigo-500/5">
                  <span className="inline-block px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 text-xs font-bold">
                    {leftData.growth}
                  </span>
                </td>
                <td className="p-4 text-center">
                  <span className="inline-block px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 text-xs font-bold">
                    {rightData.growth}
                  </span>
                </td>
              </tr>
              <tr>
                <td className="p-4 font-semibold text-slate-600 dark:text-slate-400 flex items-center gap-1.5">
                  <BookOpen size={14} className="text-indigo-500" />
                  이수 권장 교과
                </td>
                <td className="p-4 text-center text-xs text-slate-700 dark:text-slate-300 bg-indigo-500/5 leading-relaxed">{leftData.keySubject}</td>
                <td className="p-4 text-center text-xs text-slate-700 dark:text-slate-300 leading-relaxed">{rightData.keySubject}</td>
              </tr>
              <tr>
                <td className="p-4 font-semibold text-slate-600 dark:text-slate-400 flex items-center gap-1.5">
                  <AlertCircle size={14} className="text-indigo-500" />
                  활동 난이도
                </td>
                <td className="p-4 text-center text-xs text-slate-600 dark:text-slate-400 bg-indigo-500/5 leading-relaxed">{leftData.difficulty}</td>
                <td className="p-4 text-center text-xs text-slate-600 dark:text-slate-400 leading-relaxed">{rightData.difficulty}</td>
              </tr>
              <tr>
                <td className="p-4 font-semibold text-slate-600 dark:text-slate-400 flex items-center gap-1.5">
                  <Award size={14} className="text-indigo-500" />
                  차기 보완 계획
                </td>
                <td className="p-4 text-center text-xs text-slate-700 dark:text-slate-300 bg-indigo-500/5 leading-relaxed">{leftData.actionPlan}</td>
                <td className="p-4 text-center text-xs text-slate-700 dark:text-slate-300 leading-relaxed">{rightData.actionPlan}</td>
              </tr>
              <tr>
                <td className="p-4 font-semibold text-slate-600 dark:text-slate-400 flex items-center gap-1.5">
                  <CheckCircle2 size={14} className="text-indigo-500" />
                  시나리오 장점
                </td>
                <td className="p-4 text-center text-indigo-600 dark:text-indigo-400 bg-indigo-500/5 text-xs font-bold leading-relaxed">{leftData.pros}</td>
                <td className="p-4 text-center text-indigo-600 dark:text-indigo-400 text-xs font-bold leading-relaxed">{rightData.pros}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div className="flex gap-3 items-start bg-indigo-500/5 dark:bg-indigo-950/40 p-4 rounded-2xl border border-indigo-500/10 text-xs sm:text-sm text-muted">
        <ArrowRight className="text-indigo-500 shrink-0 mt-0.5" size={16} />
        <span>
          선택하는 진로 트랙에 맞춰 다음 학기 수강 신청 과목 및 창체/세특 탐구 활동 방향성을 미리 조정해두어야 대입 학종 전형에서 경쟁력을 확보할 수 있습니다.
        </span>
      </div>
    </div>
  );
}
