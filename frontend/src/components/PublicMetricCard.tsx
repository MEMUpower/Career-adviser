import React from "react";
import { AlertCircle, Calendar, CheckCircle } from "lucide-react";

interface PublicMetric {
  source: string;
  category: string;
  key_name: string;
  data: Record<string, any>;
  reference_year?: string;
  quality_flag: "FRESH" | "STALE" | "MISSING";
}

interface PublicMetricCardProps {
  metric: PublicMetric;
}

export const PublicMetricCard: React.FC<PublicMetricCardProps> = ({ metric }) => {
  const isStale = metric.quality_flag === "STALE";
  const isMissing = metric.quality_flag === "MISSING";

  return (
    <div className="glass-card p-5 rounded-xl border border-gray-800 flex flex-col justify-between">
      <div>
        <div className="flex justify-between items-start mb-3">
          <span className="text-[11px] font-bold tracking-wider text-gray-400 uppercase bg-gray-800 px-2 py-0.5 rounded">
            {metric.source} · {metric.category}
          </span>
          
          {/* Quality Badges */}
          {isStale && (
            <span className="flex items-center gap-1 text-[11px] bg-yellow-500/10 text-yellow-400 border border-yellow-500/30 px-2 py-0.5 rounded-full">
              <AlertCircle size={10} />
              지표 업데이트 필요 (1년 경과)
            </span>
          )}
          {isMissing && (
            <span className="flex items-center gap-1 text-[11px] bg-red-500/10 text-red-400 border border-red-500/30 px-2 py-0.5 rounded-full">
              <AlertCircle size={10} />
              지표 결측 상태
            </span>
          )}
          {!isStale && !isMissing && (
            <span className="flex items-center gap-1 text-[11px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded-full">
              <CheckCircle size={10} />
              최신 지표 (신뢰성 높음)
            </span>
          )}
        </div>

        <h4 className="text-lg font-bold text-white mb-2">{metric.key_name}</h4>
        
        {/* Render key values inside JSON dynamically */}
        <div className="space-y-1 text-sm text-gray-300">
          {Object.entries(metric.data).map(([key, val]) => {
            let label = key;
            if (key === "employment_rate") label = "평균 취업률";
            if (key === "growth_index") label = "성장 전망";
            if (key === "annual_openings") label = "연간 신규 채용인원";
            if (key === "demand_region") label = "수요 밀집 지역";
            
            return (
              <div key={key} className="flex justify-between border-b border-gray-900 py-1">
                <span className="text-gray-400">{label}</span>
                <span className="font-semibold text-white">
                  {typeof val === "number" && key.includes("rate") ? `${val}%` : val}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      <div className="mt-4 flex items-center gap-1.5 text-xs text-gray-400">
        <Calendar size={12} />
        <span>지표 기준일: {metric.reference_year || "연도 미표기"}</span>
      </div>
    </div>
  );
};

export default PublicMetricCard;
