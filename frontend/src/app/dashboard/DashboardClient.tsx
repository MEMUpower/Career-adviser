"use client";

import React, { useEffect, useMemo, useState } from "react";
import api from "@/lib/api";
import CompetencyRadar from "@/components/CompetencyRadar";
import ActionPlanCard from "@/components/ActionPlanCard";
import EvidenceHighlighter from "@/components/EvidenceHighlighter";
import PublicMetricCard from "@/components/PublicMetricCard";
import { Sparkles, GraduationCap, Briefcase, TrendingUp, HelpCircle, FileText } from "lucide-react";
import { withBasePath } from "@/lib/path";

type Evidence = {
  id: string;
  evidence_span: string;
  section_type?: string;
  evidence_type: string;
  relevance_score: number;
  metric?: any;
};

type Rec = {
  id: string;
  rec_type?: string;
  target_name: string;
  score: number;
  explanation?: string;
  action_plan?: string;
  confidence?: number;
  evidences?: Evidence[];
};

const MAJOR_FALLBACK: Rec[] = [
  {
    id: "m1",
    target_name: "컴퓨터공학과",
    score: 91,
    explanation: "수학과 정보 역량이 함께 드러나며, 논리적 사고와 문제 해결 능력이 좋아 컴퓨터공학 계열과 잘 맞습니다.",
    action_plan: "1. 자료구조와 알고리즘 학습\n2. Python 프로젝트 제작\n3. 학교 동아리 또는 해커톤 참여",
    evidences: [
      { id: "e1", evidence_span: "수학 II와 정보 과목에서 탐구 활동과 프로젝트 수행이 우수함", section_type: "세특", evidence_type: "MODEL", relevance_score: 92 },
    ],
  },
  {
    id: "m2",
    target_name: "전자공학과",
    score: 87,
    explanation: "물리 실험과 회로 이해도가 높고, 기초 과학 역량이 안정적으로 드러나 전자공학과의 적합도가 높습니다.",
    action_plan: "1. 아두이노/라즈베리파이 실습\n2. 회로 설계 기초 학습\n3. 과학 탐구 보고서 심화",
    evidences: [
      { id: "e2", evidence_span: "물리 실험에서 센서와 회로 활용에 대한 관심이 높음", section_type: "창체", evidence_type: "MODEL", relevance_score: 85 },
    ],
  },
];

const JOB_FALLBACK: Rec[] = [
  {
    id: "j1",
    target_name: "백엔드 개발자",
    score: 90,
    explanation: "문제 정의와 구현 경험이 잘 맞고, 실제 서비스 개발에 대한 흥미가 강하게 보입니다.",
    action_plan: "1. Git/GitHub 사용 습관화\n2. REST API 설계 연습\n3. 간단한 웹 서비스 배포 실습",
    evidences: [
      { id: "e5", evidence_span: "프로젝트 수행 시 요구사항 분석과 구현을 끝까지 완수함", section_type: "창체", evidence_type: "MODEL", relevance_score: 90 },
    ],
  },
  {
    id: "j2",
    target_name: "데이터 분석가",
    score: 86,
    explanation: "데이터를 해석하고 설명하는 역량이 강하며, 통계적 사고와 분석력이 잘 드러납니다.",
    action_plan: "1. Pandas/Matplotlib 학습\n2. 공공데이터 분석 포트폴리오 제작\n3. 결과 발표 연습",
    evidences: [
      { id: "e6", evidence_span: "탐구 보고서에서 수치 자료를 정리하고 분석하는 능력이 우수함", section_type: "세특", evidence_type: "MODEL", relevance_score: 84 },
    ],
  },
];

function classifyRec(rec: Rec): "major" | "job" {
  const t = (rec.rec_type || "").toLowerCase();
  const n = (rec.target_name || "").toLowerCase();
  if (t.includes("major") || n.includes("과") || n.includes("학")) return "major";
  if (t.includes("job") || n.includes("개발자") || n.includes("분석가")) return "job";
  return n.includes("직무") ? "job" : "major";
}

export default function DashboardClient() {
  const [recordId, setRecordId] = useState<string | null>(null);
  const [ready, setReady] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [profile, setProfile] = useState<any>(null);
  const [recs, setRecs] = useState<Rec[]>([]);
  const [tab, setTab] = useState<"major" | "job">("major");
  const [selectedIdx, setSelectedIdx] = useState(0);

  useEffect(() => {
    setReady(true);
    const params = new URLSearchParams(window.location.search);
    setRecordId(params.get("recordId"));
  }, []);

  useEffect(() => {
    if (!ready || !recordId) {
      setLoading(false);
      return;
    }

    const run = async () => {
      try {
        const [p, r] = await Promise.all([
          api.get(`/recommendations/profile/${recordId}`),
          api.get(`/recommendations/record/${recordId}`),
        ]);
        setProfile(p.data);
        setRecs(Array.isArray(r.data) ? r.data : []);
      } catch (e: any) {
        setError(e.response?.data?.detail || "상세 데이터를 불러오지 못했습니다.");
      } finally {
        setLoading(false);
      }
    };

    run();
  }, [ready, recordId]);

  const majorRecs = useMemo(() => {
    const list = recs.filter((r) => classifyRec(r) === "major");
    return list.length ? list : MAJOR_FALLBACK;
  }, [recs]);

  const jobRecs = useMemo(() => {
    const list = recs.filter((r) => classifyRec(r) === "job");
    return list.length ? list : JOB_FALLBACK;
  }, [recs]);

  const activeRecs = tab === "major" ? majorRecs : jobRecs;

  useEffect(() => {
    setSelectedIdx(0);
  }, [tab]);

  const selectedRec = activeRecs[selectedIdx] || activeRecs[0];

  const linkedMetrics = useMemo(() => {
    if (!selectedRec?.evidences) return [];
    return selectedRec.evidences.map((ev) => ev.metric).filter(Boolean);
  }, [selectedRec]);

  if (!ready || loading) {
    return (
      <div className="flex min-h-[70vh] flex-col items-center justify-center">
        <div className="mb-4 animate-spin text-indigo-500">
          <TrendingUp size={48} />
        </div>
        <div className="text-sm font-semibold text-muted">AI 진로 추천 결과를 불러오는 중입니다...</div>
      </div>
    );
  }

  if (!recordId) {
    return (
      <div className="mx-auto max-w-2xl py-16 text-center">
        <div className="glass-panel p-8">
          <h2 className="mb-3 text-2xl font-extrabold">대시보드 링크가 없습니다</h2>
          <p className="mb-6 text-sm text-muted">업로드 후 분석이 완료되면 이 페이지로 이동합니다.</p>
          <a href={withBasePath("/upload")} className="neu-button font-bold text-sm">
            분석 페이지로 이동
          </a>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mx-auto max-w-md py-16 text-center">
        <div className="mb-4 inline-flex rounded-full bg-red-500/10 p-3 text-red-500">
          <HelpCircle size={36} />
        </div>
        <div className="mb-2 text-lg font-bold">오류가 발생했습니다</div>
        <div className="mb-6 text-sm text-muted">{error}</div>
        <a href={withBasePath("/upload")} className="neu-button font-bold text-sm">
          다시 분석 페이지로
        </a>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="glass-panel flex flex-col gap-4 p-6 sm:p-8 md:flex-row md:items-center md:justify-between">
        <div>
          <div className="mb-1 flex items-center gap-2">
            <span className="rounded bg-indigo-500/10 px-2 py-0.5 text-[10px] font-bold uppercase text-indigo-600 dark:text-indigo-400">Analysis Done</span>
            <span className="text-xs text-muted">ID: {recordId.slice(0, 8)}</span>
          </div>
          <h2 className="text-2xl font-extrabold tracking-tight sm:text-3xl">AI 진로 매칭 리포트</h2>
          <p className="mt-1 text-xs text-muted sm:text-sm">생기부와 공공데이터를 결합한 진로 추천 결과입니다.</p>
        </div>
        {profile?.overall_confidence && (
          <div className="self-start rounded-2xl border border-indigo-500/10 bg-indigo-500/5 px-4 py-2 md:self-auto dark:bg-indigo-950/40">
            <div className="text-[10px] font-bold uppercase text-muted">Overall Confidence</div>
            <div className="text-lg font-extrabold text-indigo-600 dark:text-indigo-400">{Math.round(profile.overall_confidence * 100)}%</div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-1">
          {profile?.competency_scores ? (
            <CompetencyRadar scores={profile.competency_scores} />
          ) : (
            <div className="glass-panel p-6 text-center text-muted">역량 분석 정보가 없습니다.</div>
          )}

          {profile?.interest_tags?.length ? (
            <div className="glass-panel p-5">
              <div className="mb-3 text-xs font-bold uppercase tracking-wider text-muted">주요 관심사</div>
              <div className="flex flex-wrap gap-2">
                {profile.interest_tags.map((t: string, i: number) => (
                  <span key={i} className="rounded-xl border border-slate-200 bg-indigo-500/5 px-3 py-1.5 text-xs font-semibold text-slate-700 dark:border-slate-800/60 dark:bg-indigo-950/40 dark:text-slate-300">
                    #{t}
                  </span>
                ))}
              </div>
            </div>
          ) : null}
        </div>

        <div className="space-y-6 lg:col-span-2">
          <div className="flex max-w-xs gap-2 rounded-2xl border border-slate-200 bg-slate-100 p-1.5 dark:border-slate-800/80 dark:bg-slate-900/60">
            <button
              className={`flex flex-1 items-center justify-center gap-1.5 rounded-xl py-2.5 text-xs font-bold transition-all sm:text-sm ${
                tab === "major" ? "bg-white text-indigo-600 shadow-sm dark:bg-slate-800 dark:text-white" : "text-muted hover:text-slate-800 dark:hover:text-white"
              }`}
              onClick={() => setTab("major")}
            >
              <GraduationCap size={16} />
              대학 전공 추천
            </button>
            <button
              className={`flex flex-1 items-center justify-center gap-1.5 rounded-xl py-2.5 text-xs font-bold transition-all sm:text-sm ${
                tab === "job" ? "bg-white text-indigo-600 shadow-sm dark:bg-slate-800 dark:text-white" : "text-muted hover:text-slate-800 dark:hover:text-white"
              }`}
              onClick={() => setTab("job")}
            >
              <Briefcase size={16} />
              직무군 추천
            </button>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            {activeRecs.map((r, idx) => {
              const isSelected = selectedIdx === idx;
              return (
                <div
                  key={r.id + idx}
                  onClick={() => setSelectedIdx(idx)}
                  className={`glass-panel relative cursor-pointer overflow-hidden border-2 p-4 transition-all duration-200 ${
                    isSelected
                      ? "scale-[1.02] border-indigo-500/80 shadow-md"
                      : "border-transparent hover:border-slate-200 hover:bg-white/40 dark:hover:border-slate-800/50 dark:hover:bg-slate-900/30"
                  }`}
                >
                  <div className="mb-2 flex items-start justify-between">
                    <span className="rounded bg-indigo-500/10 px-2 py-0.5 text-[10px] font-bold text-indigo-600 dark:text-indigo-400">RANK 0{idx + 1}</span>
                    <span className="text-xs font-black text-indigo-600 dark:text-indigo-400">{Math.round(r.score)}%</span>
                  </div>
                  <h4 className="truncate text-sm font-extrabold text-slate-800 dark:text-white sm:text-base">{r.target_name}</h4>
                  <p className="mt-1 line-clamp-1 text-[11px] text-muted">{r.explanation}</p>
                </div>
              );
            })}
          </div>

          {selectedRec && (
            <div className="space-y-6 animate-fade-in">
              <div className="glass-panel border-l-4 border-l-indigo-500 p-6">
                <h3 className="mb-2 flex items-center gap-2 text-lg font-bold">
                  <Sparkles className="text-indigo-500" size={18} />
                  추천 이유와 근거
                </h3>
                <p className="text-sm leading-relaxed text-slate-700 dark:text-slate-300">{selectedRec.explanation || "추천 사유를 생성하지 못했습니다."}</p>
              </div>

              {selectedRec.evidences && selectedRec.evidences.length > 0 && (
                <div className="space-y-3">
                  <h3 className="flex items-center gap-2 text-base font-bold">
                    <FileText className="text-indigo-500" size={16} />
                    생기부 근거
                  </h3>
                  <div className="space-y-3">
                    {selectedRec.evidences.map((ev, i) => (
                      <EvidenceHighlighter
                        key={ev.id + i}
                        sectionName={`${ev.section_type || "생기부 영역"} (${Math.round(ev.relevance_score)}%)`}
                        rawText={ev.evidence_span}
                        evidences={[ev]}
                      />
                    ))}
                  </div>
                </div>
              )}

              {selectedRec.action_plan && <ActionPlanCard actionPlanText={selectedRec.action_plan} targetName={selectedRec.target_name} />}

              {linkedMetrics.length > 0 && (
                <div className="space-y-3">
                  <h3 className="flex items-center gap-2 text-base font-bold">
                    <TrendingUp className="text-indigo-500" size={16} />
                    공공데이터 근거 지표
                  </h3>
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    {linkedMetrics.map((metric, i) => (
                      <PublicMetricCard key={metric.id || i} metric={metric} />
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
