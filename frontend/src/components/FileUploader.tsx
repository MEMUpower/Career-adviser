import React, { useState, useRef } from "react";
import { UploadCloud, File, AlertCircle, CheckCircle } from "lucide-react";
import api from "@/lib/api";

interface FileUploaderProps {
  onUploadSuccess: (recordId: string) => void;
}

export const FileUploader: React.FC<FileUploaderProps> = ({ onUploadSuccess }) => {
  const [file, setFile] = useState<File | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [consent, setConsent] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    setError(null);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0];
      validateAndSetFile(droppedFile);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    if (e.target.files && e.target.files.length > 0) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (selectedFile: File) => {
    if (!selectedFile.name.toLowerCase().endsWith(".pdf")) {
      setError("생활기록부 분석은 PDF 포맷만 지원합니다.");
      setFile(null);
      return;
    }
    if (selectedFile.size > 20 * 1024 * 1024) {
      setError("파일 크기는 최대 20MB 이하만 가능합니다.");
      setFile(null);
      return;
    }
    setFile(selectedFile);
  };

  const handleUpload = async () => {
    if (!file) return;
    if (!consent) {
      setError("개인정보 마스킹(비식별화) 수집 및 활용 동의가 필요합니다.");
      return;
    }

    setLoading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await api.post("/records/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      onUploadSuccess(response.data.id);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "파일 업로드 중 네트워크 오류가 발생했습니다."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel p-6 sm:p-8">
      <h3 className="text-2xl font-bold mb-2">학교생활기록부 업로드</h3>
      <p className="text-xs text-muted mb-6">
        AI가 나이스(NEIS)에서 발급받은 PDF 파일을 파싱하여 분석 및 맞춤형 전공/직무 시나리오 추천을 생성합니다.
      </p>

      {/* Drag & Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-2xl p-8 sm:p-12 flex flex-col items-center justify-center cursor-pointer transition-all duration-300 ${
          isDragOver
            ? "border-indigo-500 bg-indigo-500/5 dark:bg-indigo-500/10 scale-[0.99]"
            : file
            ? "border-emerald-500/50 bg-emerald-500/5"
            : "border-slate-200 dark:border-slate-800 hover:border-indigo-400 dark:hover:border-indigo-500/50 bg-white/20 dark:bg-slate-950/20"
        }`}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept=".pdf"
          className="hidden"
        />

        {file ? (
          <div className="text-center animate-fade-in">
            <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-500">
              <File size={28} />
            </div>
            <span className="text-sm font-semibold block mb-1 truncate max-w-xs">{file.name}</span>
            <span className="text-xs text-muted bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded-full">
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </span>
          </div>
        ) : (
          <div className="text-center">
            <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-indigo-50 dark:bg-indigo-950/40 text-indigo-500 dark:text-indigo-400">
              <UploadCloud size={28} />
            </div>
            <span className="text-sm font-semibold text-slate-700 dark:text-slate-200 block mb-1">
              생활기록부 PDF 드래그 또는 파일 선택
            </span>
            <span className="text-xs text-muted">지원 형식: PDF (최대 20MB)</span>
          </div>
        )}
      </div>

      {/* Consent Checkbox */}
      <div className="mt-6 flex items-start gap-3 p-4 rounded-xl bg-slate-50 dark:bg-slate-900/40 border border-slate-100 dark:border-slate-800/60">
        <input
          type="checkbox"
          id="consent"
          checked={consent}
          onChange={(e) => setConsent(e.target.checked)}
          className="mt-1 h-4 w-4 rounded border-slate-300 dark:border-slate-700 text-indigo-600 focus:ring-indigo-500 cursor-pointer"
        />
        <label htmlFor="consent" className="text-xs text-muted leading-relaxed cursor-pointer select-none">
          <strong className="text-slate-800 dark:text-slate-200 block mb-0.5">개인정보 비식별화 및 마스킹 동의</strong>
          업로드 시 이름, 학년, 학번, 학교명과 같은 학생 식별 정보는 자동으로 마스킹 처리되어 개인 식별이 불가한 상태로 분석됩니다.
        </label>
      </div>

      {error && (
        <div className="mt-4 flex items-center gap-2.5 text-xs bg-red-500/10 border border-red-500/20 text-red-400 p-3.5 rounded-xl">
          <AlertCircle size={16} className="shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={!file || loading}
        className={`mt-6 w-full py-4 rounded-xl font-bold text-sm transition-all duration-200 ${
          file && !loading
            ? "bg-gradient-to-r from-indigo-500 to-cyan-500 text-white shadow-lg shadow-indigo-500/20 hover:opacity-95 hover:translate-y-[-1px]"
            : "bg-slate-100 dark:bg-slate-800/80 text-slate-400 dark:text-slate-500 cursor-not-allowed"
        }`}
      >
        {loading ? "AI 분석 파이프라인 작동 중..." : "생기부 심층 분석 시작하기"}
      </button>
    </div>
  );
};

export default FileUploader;
