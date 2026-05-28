import React from "react";

interface Evidence {
  evidence_span: string;
  section_type?: string;
  relevance_score: number;
}

interface EvidenceHighlighterProps {
  sectionName: string;
  rawText: string;
  evidences: Evidence[];
}

export const EvidenceHighlighter: React.FC<EvidenceHighlighterProps> = ({
  sectionName,
  rawText,
  evidences,
}) => {
  if (!rawText) return null;

  // Find all evidence spans matching this section (or any if not specified)
  const activeSpans = evidences.map((ev) => ev.evidence_span.trim()).filter(Boolean);

  if (activeSpans.length === 0) {
    return (
      <div className="glass-panel p-4 rounded-lg text-gray-300 text-sm leading-relaxed whitespace-pre-wrap">
        {rawText}
      </div>
    );
  }

  // Escape regex specials
  const escapeRegExp = (str: string) => {
    return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  };

  // Build sorting and regex replacements
  // To avoid nested highlights, we sort spans from longest to shortest
  const sortedSpans = [...activeSpans].sort((a, b) => b.length - a.length);
  
  // Custom splitting renderer
  let renderedElements: React.ReactNode[] = [rawText];

  sortedSpans.forEach((span) => {
    const nextElements: React.ReactNode[] = [];
    
    renderedElements.forEach((el) => {
      if (typeof el !== "string") {
        nextElements.push(el);
        return;
      }

      const parts = el.split(new RegExp(`(${escapeRegExp(span)})`, "gi"));
      parts.forEach((part, index) => {
        if (part.toLowerCase() === span.toLowerCase()) {
          nextElements.push(
            <span
              key={`${span}-${index}`}
              className="bg-yellow-500/20 text-yellow-300 border-b border-yellow-400 font-medium px-1 rounded transition-all duration-300 hover:bg-yellow-500/40 cursor-help"
              title="AI 추천 근거 문장 발췌"
            >
              {part}
            </span>
          );
        } else {
          nextElements.push(part);
        }
      });
    });
    
    renderedElements = nextElements;
  });

  return (
    <div className="glass-panel p-5 rounded-xl border border-gray-800 text-gray-300 text-sm leading-relaxed max-h-80 overflow-y-auto whitespace-pre-wrap">
      <div className="flex justify-between items-center mb-3">
        <span className="text-xs font-semibold text-brand-500 px-2 py-0.5 rounded bg-brand-500/10">
          {sectionName}
        </span>
        <span className="text-[11px] text-gray-400">
          💡 하이라이트된 문장은 AI의 주요 추천 팩트 기반 근거입니다.
        </span>
      </div>
      <div>{renderedElements}</div>
    </div>
  );
};

export default EvidenceHighlighter;
