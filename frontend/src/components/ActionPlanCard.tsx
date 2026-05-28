import React, { useState } from "react";
import { Sparkles, CheckSquare, Square, CheckCircle } from "lucide-react";

interface ActionPlanCardProps {
  actionPlanText: string;
  targetName: string;
}

export const ActionPlanCard: React.FC<ActionPlanCardProps> = ({ actionPlanText, targetName }) => {
  // Parse actionPlanText split by lines to generate a checklist
  const lines = actionPlanText
    .split(/[.\n]/)
    .map((line) => line.trim())
    .filter((line) => line.length > 5);

  const [checkedItems, setCheckedItems] = useState<Record<number, boolean>>({});

  const toggleCheck = (idx: number) => {
    setCheckedItems((prev) => ({
      ...prev,
      [idx]: !prev[idx],
    }));
  };

  const completedCount = Object.values(checkedItems).filter(Boolean).length;
  const progressPercent = lines.length > 0 ? Math.round((completedCount / lines.length) * 100) : 0;

  return (
    <div className="glass-panel p-6 rounded-xl border border-gray-800">
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center gap-2">
          <Sparkles className="text-yellow-400" size={18} />
          <h3 className="text-lg font-bold text-white">진로 맞춤형 액션 플랜 ({targetName})</h3>
        </div>
        <span className="text-xs bg-brand-500/20 text-brand-400 px-2 py-0.5 rounded-full font-semibold">
          달성률 {progressPercent}%
        </span>
      </div>

      <p className="text-sm text-gray-400 mb-4 leading-relaxed">
        AI 분석 결과, {targetName} 방향성의 적합도를 높이기 위해 다음 학기까지 완수해야 할 학업/비교과 보완 행동 리스트입니다.
      </p>

      {/* Progress Bar */}
      <div className="w-full bg-gray-900 rounded-full h-2 mb-5">
        <div
          className="bg-brand-500 h-2 rounded-full transition-all duration-500"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      <div className="space-y-3">
        {lines.map((line, idx) => {
          const isChecked = !!checkedItems[idx];
          return (
            <div
              key={idx}
              onClick={() => toggleCheck(idx)}
              className={`flex items-start gap-3 p-3 rounded-lg cursor-pointer transition-all duration-200 border ${
                isChecked
                  ? "bg-brand-500/5 border-brand-500/20 text-gray-400"
                  : "bg-gray-900/40 border-transparent hover:border-gray-800 text-gray-200"
              }`}
            >
              <div className="mt-0.5 text-brand-500">
                {isChecked ? <CheckSquare size={16} /> : <Square size={16} />}
              </div>
              <span className={`text-sm leading-relaxed ${isChecked ? "line-through" : ""}`}>
                {line}
              </span>
            </div>
          );
        })}
      </div>

      {progressPercent === 100 && lines.length > 0 && (
        <div className="mt-4 flex items-center gap-2 text-xs bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 p-3 rounded-lg">
          <CheckCircle size={16} />
          <span>축하합니다! 추천받은 모든 학기별 액션 플랜을 달성하였습니다.</span>
        </div>
      )}
    </div>
  );
};

export default ActionPlanCard;
