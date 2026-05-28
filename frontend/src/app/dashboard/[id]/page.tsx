"use client";

import React, { useEffect, useMemo, useState } from "react";
import api from "@/lib/api";
import CompetencyRadar from "@/components/CompetencyRadar";
import ActionPlanCard from "@/components/ActionPlanCard";
import EvidenceHighlighter from "@/components/EvidenceHighlighter";
import PublicMetricCard from "@/components/PublicMetricCard";
import { Sparkles, GraduationCap, Briefcase, Award, TrendingUp, HelpCircle, FileText, ChevronRight } from "lucide-react";

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
    explanation: "수학 및 정보교과 과목의 탁월한 성취도와 교과 세특에 기술된 다양한 하드웨어/소프트웨어 융합 프로젝트 설계 역량이 높게 반영되었습니다.", 
    action_plan: "1. 자료구조 및 알고리즘 심화 개념 습득\n2. 파이썬을 활용한 오픈소스 인공지능 기초 모델 토이 프로젝트 진행\n3. 학교 동아리 내 IT 솔루션 설계 역할 수행",
    evidences: [
      { id: "e1", evidence_span: "수학 II 교과에서 알고리즘적 사고력이 뛰어남을 증명함", section_type: "세특", evidence_type: "MODEL", relevance_score: 92 },
      { id: "e2", evidence_span: "정보 교과 시간에 파이썬을 활용한 데이터 분석 보고서를 작성함", section_type: "세특", evidence_type: "MODEL", relevance_score: 88 }
    ]
  },
  { 
    id: "m2", 
    target_name: "전자공학과", 
    score: 87, 
    explanation: "물리학 탐구 실험에서의 높은 자기주도성과 전기회로 제어와 관련된 학업 활동이 돋보입니다.", 
    action_plan: "1. 일반물리학 전자기학 파트 선행 독서\n2. 브레드보드를 활용한 기초 회로도 구성 및 실험 분석 보고서 작성",
    evidences: [
      { id: "e3", evidence_span: "물리학I 실험 중 전기 회로의 옴의 법칙을 심화 탐구함", section_type: "세특", evidence_type: "MODEL", relevance_score: 85 }
    ]
  },
  { 
    id: "m3", 
    target_name: "데이터사이언스학과", 
    score: 85, 
    explanation: "확률과 통계의 통계적 추정 단원에서 데이터 시각화 기법을 연계한 융합적 과제 해결 노력이 우수합니다.", 
    action_plan: "1. 통계 데이터 분석 기법 독학\n2. 공공데이터포털(data.go.kr)의 CSV 데이터를 활용한 시각화 포트폴리오 기획",
    evidences: [
      { id: "e4", evidence_span: "실생활 통계 조사 프로젝트에서 뛰어난 지표 해석 능력을 보임", section_type: "창체", evidence_type: "MODEL", relevance_score: 89 }
    ]
  },
];

const JOB_FALLBACK: Rec[] = [
  { 
    id: "j1", 
    target_name: "소프트웨어 개발자", 
    score: 90, 
    explanation: "문제 해결을 위해 새로운 기술 스택을 탐색하고 적용하는 도전적 문제 해결 역량이 돋보입니다.", 
    action_plan: "1. Git/GitHub 버전 관리 기본 사용법 습득\n2. 웹 API 설계 기초 및 간단한 백엔드 인터페이스 구축",
    evidences: [
      { id: "e5", evidence_span: "소프트웨어 프로젝트 동아리에서 조장을 맡아 협업 결과물을 도출함", section_type: "창체", evidence_type: "MODEL", relevance_score: 90 }
    ]
  },
  { 
    id: "j2", 
    target_name: "데이터 분석가", 
    score: 86, 
    explanation: "복잡한 문제의 변수를 식별하고, 논리적이고 정량적인 수치로 문제를 재정의하는 능력이 뛰어납니다.", 
    action_plan: "1. 파이썬 Pandas 라이브러리 기초 활용 학습\n2. 기초 통계 분석 이론 학습 및 주 단위 분석 연습 진행",
    evidences: [
      { id: "e6", evidence_span: "동아리 활동에서 부원들의 설문 자료 데이터를 통계 분석함", section_type: "창체", evidence_type: "MODEL", relevance_score: 84 }
    ]
  },
  { 
    id: "j3", 
    target_name: "시스템 임베디드 엔지니어", 
    score: 84, 
    explanation: "물리 및 코딩 실습의 융합 지식을 기반으로 하드웨어와 연동되는 임베디드 제어에 강한 관심이 보입니다.", 
    action_plan: "1. 아두이노/라즈베리파이 등 하드웨어 마이크로컨트롤러 실습 진행\n2. C언어 포인터 및 하드웨어 메모리 기초 매커니즘 이해",
    evidences: [
      { id: "e7", evidence_span: "물리 정보 융합 탐구 활동에서 스마트 홈 IoT 아이디어를 구현함", section_type: "세특", evidence_type: "MODEL", relevance_score: 83 }
    ]
  },
];

function classifyRec(rec: Rec): "major" | "job" {
  const t = (rec.rec_type || "").toLowerCase();
  const n = (rec.target_name || "").toLowerCase();
  if (t.includes("major") || t.includes("전공") || n.includes("학과") || n.includes("공학")) return "major";
  if (t.includes("job") || t.includes("직무")) return "job";
  return n.includes("개발") || n.includes("분석") || n.includes("엔지니어") ? "job" : "major";
}

export default function DashboardPage({ params }: { params: { id: string } }) {
  const recordId = params.id;
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [profile, setProfile] = useState<any>(null);
  const [recs, setRecs] = useState<Rec[]>([]);
  const [tab, setTab] = useState<"major" | "job">("major");
  
  // Track selected recommendation index for details view
  const [selectedIdx, setSelectedIdx] = useState<number>(0);

  useEffect(() => {
    const run = async () => {
      try {
        const [p, r] = await Promise.all([
          api.get(`/recommendations/profile/${recordId}`),
          api.get(`/recommendations/record/${recordId}`),
        ]);
        setProfile(p.data);
        setRecs(Array.isArray(r.data) ? r.data : []);
      } catch (e: any) {
        setError(e.response?.data?.detail || "대시보드 데이터를 불러오지 못했습니다.");
      } finally {
        setLoading(false);
      }
    };
    run();
  }, [recordId]);

  const majorRecs = useMemo(() => {
    const list = recs.filter((r) => classifyRec(r) === "major");
    return list.length ? list : MAJOR_FALLBACK;
  }, [recs]);

  const jobRecs = useMemo(() => {
    const list = recs.filter((r) => classifyRec(r) === "job");
    return list.length ? list : JOB_FALLBACK;
  }, [recs]);

  const activeRecs = tab === "major" ? majorRecs : jobRecs;

  // Reset selected recommendation when changing tabs
  useEffect(() => {
    setSelectedIdx(0);
  }, [tab]);

  const selectedRec = activeRecs[selectedIdx] || activeRecs[0];

  // Helper to extract metric elements from evidences
  const linkedMetrics = useMemo(() => {
    if (!selectedRec || !selectedRec.evidences) return [];
    return selectedRec.evidences
      .map(ev => ev.metric)
      .filter(Boolean);
  }, [selectedRec]);

  if (loading) {
    return (
      <div className="flex flex-col justify-center items-center min-h-[70vh]">
        <div className="animate-spin text-indigo-500 mb-4">
          <TrendingUp size={48} />
        </div>
        <div className="text-sm font-semibold text-muted">학생 생활기록부 기반 역량 및 진로 모델 추천 결과 로딩 중...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-md mx-auto text-center py-16">
        <div className="text-red-500 mb-4 inline-flex p-3 bg-red-500/10 rounded-full">
          <HelpCircle size={36} />
        </div>
        <div className="text-lg font-bold mb-2">에러가 발생했습니다</div>
        <div className="text-sm text-muted mb-6">{error}</div>
        <a href="/upload" className="neu-button font-bold text-sm">다시 분석 페이지로</a>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="glass-panel p-6 sm:p-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-indigo-500/10 text-indigo-600 dark:text-indigo-400">Analysis Done</span>
            <span className="text-xs text-muted">ID: {recordId.slice(0, 8)}</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight">AI 진로 매핑 포트폴리오</h2>
          <p className="text-xs sm:text-sm text-muted mt-1">학생의 교과/세특 텍스트 분석에 근거한 정량적 추천 보고서입니다.</p>
        </div>
        {profile?.overall_confidence && (
          <div className="self-start md:self-auto px-4 py-2 bg-indigo-500/5 dark:bg-indigo-950/40 border border-indigo-500/10 rounded-2xl">
            <div className="text-[10px] text-muted font-bold uppercase">Overall Confidence</div>
            <div className="text-lg font-extrabold text-indigo-600 dark:text-indigo-400">
              {Math.round(profile.overall_confidence * 100)}%
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Competency Profiles & Interest Tags */}
        <div className="space-y-6 lg:col-span-1">
          {/* Radar Chart */}
          {profile?.competency_scores ? (
            <CompetencyRadar scores={profile.competency_scores} />
          ) : (
            <div className="glass-panel p-6 text-center text-muted">역량 수치 정보를 불러올 수 없습니다.</div>
          )}

          {/* Interest Tags */}
          {profile?.interest_tags?.length ? (
            <div className="glass-panel p-5">
              <div className="mb-3 text-xs font-bold text-muted uppercase tracking-wider">주요 관심 키워드</div>
              <div className="flex flex-wrap gap-2">
                {profile.interest_tags.map((t: string, i: number) => (
                  <span key={i} className="text-xs font-semibold px-3 py-1.5 rounded-xl bg-indigo-500/5 dark:bg-indigo-950/40 border border-slate-200 dark:border-slate-800/60 text-slate-700 dark:text-slate-300">
                    #{t}
                  </span>
                ))}
              </div>
            </div>
          ) : null}
        </div>

        {/* Right Column: Recommendations & Evidence Analysis */}
        <div className="lg:col-span-2 space-y-6">
          {/* Tabs */}
          <div className="flex gap-2 p-1.5 bg-slate-100 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/80 rounded-2xl max-w-xs">
            <button 
              className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-xl text-xs sm:text-sm font-bold transition-all ${
                tab === "major" 
                  ? "bg-white dark:bg-slate-800 text-indigo-600 dark:text-white shadow-sm" 
                  : "text-muted hover:text-slate-800 dark:hover:text-white"
              }`} 
              onClick={() => setTab("major")}
            >
              <GraduationCap size={16} />
              대학 전공 추천
            </button>
            <button 
              className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-xl text-xs sm:text-sm font-bold transition-all ${
                tab === "job" 
                  ? "bg-white dark:bg-slate-800 text-indigo-600 dark:text-white shadow-sm" 
                  : "text-muted hover:text-slate-800 dark:hover:text-white"
              }`} 
              onClick={() => setTab("job")}
            >
              <Briefcase size={16} />
              직무군 추천
            </button>
          </div>

          {/* Rec Selection List */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {activeRecs.map((r, idx) => {
              const isSelected = selectedIdx === idx;
              return (
                <div 
                  key={r.id + idx} 
                  onClick={() => setSelectedIdx(idx)}
                  className={`glass-panel p-4 cursor-pointer relative overflow-hidden transition-all duration-200 border-2 ${
                    isSelected 
                      ? "border-indigo-500/80 shadow-md scale-[1.02]" 
                      : "border-transparent hover:border-slate-200 dark:hover:border-slate-800/50 hover:bg-white/40 dark:hover:bg-slate-900/30"
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-600 dark:text-indigo-400">
                      RANK 0{idx + 1}
                    </span>
                    <span className="text-xs font-black text-indigo-600 dark:text-indigo-400">{Math.round(r.score)}점</span>
                  </div>
                  <h4 className="text-sm sm:text-base font-extrabold truncate text-slate-800 dark:text-white">{r.target_name}</h4>
                  <p className="text-[11px] text-muted line-clamp-1 mt-1">{r.explanation}</p>
                </div>
              );
            })}
          </div>

          {/* Selected Rec Detail Content */}
          {selectedRec && (
            <div className="space-y-6 animate-fade-in">
              {/* Detailed Explanation Panel */}
              <div className="glass-panel p-6 border-l-4 border-l-indigo-500">
                <h3 className="text-lg font-bold mb-2 flex items-center gap-2">
                  <Sparkles className="text-indigo-500" size={18} />
                  정성적 분석 및 적합사유
                </h3>
                <p className="text-sm leading-relaxed text-slate-700 dark:text-slate-300">
                  {selectedRec.explanation || "추천 이유를 생성하고 있습니다."}
                </p>
              </div>

              {/* Evidences (EvidenceHighlighter) */}
              {selectedRec.evidences && selectedRec.evidences.length > 0 && (
                <div className="space-y-3">
                  <h3 className="text-base font-bold flex items-center gap-2">
                    <FileText className="text-indigo-500" size={16} />
                    생기부 내 추천 핵심 근거
                  </h3>
                  <div className="space-y-3">
                    {selectedRec.evidences.map((ev, i) => (
                      <EvidenceHighlighter 
                        key={ev.id + i}
                        sectionName={`${ev.section_type || "생기부 영역"} (신뢰 지수: ${Math.round(ev.relevance_score)}%)`}
                        rawText={ev.evidence_span}
                        evidences={[ev]}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Action Plan */}
              {selectedRec.action_plan && (
                <ActionPlanCard 
                  actionPlanText={selectedRec.action_plan} 
                  targetName={selectedRec.target_name} 
                />
              )}

              {/* Public Metrics (PublicMetricCard) */}
              {linkedMetrics.length > 0 && (
                <div className="space-y-3">
                  <h3 className="text-base font-bold flex items-center gap-2">
                    <TrendingUp className="text-indigo-500" size={16} />
                    공공데이터 연계 진로 통계 지표
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
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
