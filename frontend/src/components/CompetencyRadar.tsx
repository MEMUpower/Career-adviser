import React, { useEffect, useRef } from "react";
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from "chart.js";
import { Radar } from "react-chartjs-2";

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

interface CompetencyRadarProps {
  scores: {
    탐구력: number;
    협업: number;
    의사소통: number;
    자기주도성: number;
  };
}

export const CompetencyRadar: React.FC<CompetencyRadarProps> = ({ scores }) => {
  const data = {
    labels: ["탐구력", "협업", "의사소통", "자기주도성"],
    datasets: [
      {
        label: "학생 역량 수치",
        data: [scores.탐구력, scores.협업, scores.의사소통, scores.자기주도성],
        backgroundColor: "rgba(59, 130, 246, 0.2)",
        borderColor: "rgba(59, 130, 246, 0.8)",
        borderWidth: 2,
        pointBackgroundColor: "rgba(59, 130, 246, 1)",
        pointBorderColor: "#fff",
        pointHoverBackgroundColor: "#fff",
        pointHoverBorderColor: "rgba(59, 130, 246, 1)",
      },
    ],
  };

  const options = {
    scales: {
      r: {
        angleLines: {
          color: "rgba(255, 255, 255, 0.1)",
        },
        grid: {
          color: "rgba(255, 255, 255, 0.1)",
        },
        pointLabels: {
          color: "#94a3b8",
          font: {
            size: 13,
            family: "Inter",
          },
        },
        ticks: {
          color: "#64748b",
          backdropColor: "transparent",
          stepSize: 20,
        },
        suggestedMin: 0,
        suggestedMax: 100,
      },
    },
    plugins: {
      legend: {
        display: false,
      },
    },
  };

  return (
    <div className="glass-panel p-6 rounded-xl border border-gray-800 flex flex-col items-center justify-center">
      <h3 className="text-lg font-bold text-white mb-4">핵심 역량 분석 레이더</h3>
      <div className="w-64 h-64">
        <Radar data={data} options={options} />
      </div>
      <div className="mt-4 grid grid-cols-2 gap-3 w-full text-xs">
        <div className="bg-gray-900/50 p-2 rounded border border-gray-800 text-center">
          <span className="text-gray-400 block">탐구력</span>
          <span className="text-brand-500 font-bold text-base">{scores.탐구력}점</span>
        </div>
        <div className="bg-gray-900/50 p-2 rounded border border-gray-800 text-center">
          <span className="text-gray-400 block">자기주도성</span>
          <span className="text-brand-500 font-bold text-base">{scores.자기주도성}점</span>
        </div>
      </div>
    </div>
  );
};

export default CompetencyRadar;
