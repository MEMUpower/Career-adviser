#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
생기부 기반 AI 진로 추천 서비스 - 발표 자료 PDF 생성 스크립트
"""

HTML_CONTENT = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<style>
@font-face {
    font-family: 'NotoSansKR';
    src: local('Noto Sans CJK KR'), local('NotoSansCJKkr-Regular'),
         local('Noto Sans KR');
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Noto Sans CJK KR', 'NotoSansKR', 'Malgun Gothic', sans-serif;
    font-size: 12pt;
    color: #1a1a2e;
    background: white;
}

.page {
    width: 297mm;
    height: 210mm;
    page-break-after: always;
    page-break-inside: avoid;
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

.page:last-child { page-break-after: avoid; }

/* ===== 슬라이드 1: 표지 ===== */
.cover {
    background: linear-gradient(135deg, #0f3460 0%, #16213e 50%, #0f3460 100%);
    color: white;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 30mm 25mm;
}

.cover .badge {
    background: rgba(100,200,255,0.2);
    border: 1px solid rgba(100,200,255,0.4);
    border-radius: 20px;
    padding: 5px 18px;
    font-size: 10pt;
    color: #64c8ff;
    letter-spacing: 2px;
    margin-bottom: 10mm;
    display: inline-block;
}

.cover h1 {
    font-size: 30pt;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 6mm;
    line-height: 1.3;
}

.cover h1 span {
    color: #64c8ff;
}

.cover .subtitle {
    font-size: 14pt;
    color: rgba(255,255,255,0.8);
    margin-bottom: 15mm;
    line-height: 1.6;
}

.cover .meta {
    font-size: 10pt;
    color: rgba(255,255,255,0.5);
    border-top: 1px solid rgba(255,255,255,0.15);
    padding-top: 6mm;
    margin-top: 10mm;
}

.cover .tag-row {
    display: flex;
    justify-content: center;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 8mm;
}

.cover .tag {
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 12px;
    padding: 3px 12px;
    font-size: 9pt;
    color: rgba(255,255,255,0.75);
}

/* ===== 일반 슬라이드 헤더 ===== */
.slide-header {
    background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
    padding: 8mm 15mm;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.slide-header h2 {
    font-size: 18pt;
    font-weight: 700;
    color: #ffffff;
}

.slide-header .slide-num {
    font-size: 10pt;
    color: rgba(255,255,255,0.5);
    background: rgba(255,255,255,0.1);
    padding: 3px 10px;
    border-radius: 10px;
}

.slide-body {
    flex: 1;
    padding: 8mm 15mm;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    background: #f8faff;
}

/* ===== 카드 그리드 ===== */
.card-grid {
    display: flex;
    gap: 6mm;
    flex-wrap: wrap;
    margin-top: 4mm;
}

.card {
    flex: 1;
    min-width: 40mm;
    background: white;
    border-radius: 8px;
    padding: 5mm;
    border-left: 4px solid #0f3460;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.card h3 {
    font-size: 11pt;
    font-weight: 700;
    color: #0f3460;
    margin-bottom: 3mm;
}

.card p {
    font-size: 9pt;
    line-height: 1.6;
    color: #444;
}

.card.green { border-left-color: #2d8a5e; }
.card.red { border-left-color: #c0392b; }
.card.blue { border-left-color: #2471a3; }
.card.orange { border-left-color: #d35400; }
.card.purple { border-left-color: #6c3483; }

/* ===== 하이라이트 박스 ===== */
.highlight-box {
    background: linear-gradient(135deg, #eaf4fb, #d6eaf8);
    border: 1px solid #2471a3;
    border-radius: 8px;
    padding: 5mm 7mm;
    margin: 4mm 0;
}

.highlight-box h3 {
    font-size: 12pt;
    color: #1a5276;
    font-weight: 700;
    margin-bottom: 2mm;
}

.highlight-box p, .highlight-box li {
    font-size: 10pt;
    color: #2c3e50;
    line-height: 1.7;
}

.highlight-box ul { padding-left: 5mm; }

/* ===== 2컬럼 레이아웃 ===== */
.two-col {
    display: flex;
    gap: 7mm;
    flex: 1;
    margin-top: 4mm;
}

.col { flex: 1; }

/* ===== 문제/해결 박스 ===== */
.problem-box {
    background: #fdedec;
    border: 1px solid #e74c3c;
    border-radius: 8px;
    padding: 5mm;
    margin-bottom: 4mm;
}
.problem-box h3 { color: #c0392b; font-size: 11pt; margin-bottom: 2mm; }
.problem-box p { font-size: 9.5pt; line-height: 1.7; }

.solution-box {
    background: #eafaf1;
    border: 1px solid #27ae60;
    border-radius: 8px;
    padding: 5mm;
    margin-bottom: 4mm;
}
.solution-box h3 { color: #1e8449; font-size: 11pt; margin-bottom: 2mm; }
.solution-box p { font-size: 9.5pt; line-height: 1.7; }

/* ===== 플로우 차트 ===== */
.flow-row {
    display: flex;
    align-items: center;
    gap: 3mm;
    margin: 5mm 0;
    flex-wrap: nowrap;
}

.flow-box {
    flex: 1;
    background: white;
    border: 2px solid #0f3460;
    border-radius: 8px;
    padding: 4mm;
    text-align: center;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}

.flow-box .step-num {
    font-size: 10pt;
    color: #0f3460;
    font-weight: 700;
    margin-bottom: 1mm;
}

.flow-box .step-name {
    font-size: 9pt;
    color: #2c3e50;
    line-height: 1.5;
}

.flow-arrow {
    font-size: 14pt;
    color: #0f3460;
    font-weight: bold;
    flex-shrink: 0;
}

/* ===== 데이터 테이블 ===== */
table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4mm;
    font-size: 9.5pt;
}

th {
    background: #0f3460;
    color: white;
    padding: 3mm 4mm;
    text-align: left;
    font-weight: 600;
}

td {
    padding: 3mm 4mm;
    border-bottom: 1px solid #dee2e6;
    vertical-align: top;
    line-height: 1.5;
}

tr:nth-child(even) td { background: #f8f9fa; }

/* ===== 목록 스타일 ===== */
.check-list {
    list-style: none;
    margin-top: 3mm;
}

.check-list li {
    font-size: 10pt;
    line-height: 1.7;
    padding: 1.5mm 0;
    padding-left: 6mm;
    position: relative;
    color: #2c3e50;
}

.check-list li::before {
    content: "✔";
    position: absolute;
    left: 0;
    color: #27ae60;
    font-weight: bold;
}

/* ===== 통계 카드 ===== */
.stat-row {
    display: flex;
    gap: 6mm;
    margin: 4mm 0;
}

.stat-card {
    flex: 1;
    background: white;
    border-radius: 10px;
    padding: 5mm;
    text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    border-top: 4px solid #0f3460;
}

.stat-card .stat-num {
    font-size: 20pt;
    font-weight: 700;
    color: #0f3460;
}

.stat-card .stat-label {
    font-size: 9pt;
    color: #666;
    margin-top: 1mm;
}

/* ===== 인용/강조 ===== */
.quote-box {
    background: #0f3460;
    color: white;
    border-radius: 8px;
    padding: 5mm 7mm;
    margin: 4mm 0;
    font-size: 11pt;
    line-height: 1.6;
    font-weight: 500;
    text-align: center;
}

/* ===== 하단 출처 표기 ===== */
.source-note {
    font-size: 8pt;
    color: #888;
    margin-top: 3mm;
    border-top: 1px solid #ddd;
    padding-top: 2mm;
}

@page {
    size: A4 landscape;
    margin: 0;
}
</style>
</head>
<body>

<!-- ===== 슬라이드 1: 표지 ===== -->
<div class="page cover">
    <div class="badge">AI 기반 교육 서비스 · 공공데이터 활용</div>
    <h1>생기부 기반<br><span>AI 진로 추천</span> 서비스</h1>
    <div class="subtitle">
        학생생활기록부 × 교육 공공데이터 × 생성형 AI<br>
        객관적이고 신뢰할 수 있는 맞춤형 진로 설계
    </div>
    <div class="tag-row">
        <span class="tag">KOSIS 취업률 데이터</span>
        <span class="tag">워크넷 직무전망 API</span>
        <span class="tag">Gemini / OpenAI LLM</span>
        <span class="tag">개인정보 비식별화</span>
        <span class="tag">FastAPI + Next.js</span>
    </div>
    <div class="meta">
        작성일: 2026-05-27 &nbsp;|&nbsp; 생성형 AI 활용: Gemini 1.5 Flash (분석·요약·추천 전 과정)
    </div>
</div>

<!-- ===== 슬라이드 2: 목차 ===== -->
<div class="page">
    <div class="slide-header">
        <h2>목 차</h2>
        <span class="slide-num">2 / 15</span>
    </div>
    <div class="slide-body">
        <div class="two-col">
            <div class="col">
                <div class="highlight-box">
                    <h3>📌 서비스 소개</h3>
                    <ul class="check-list">
                        <li>개발 동기 및 배경</li>
                        <li>서비스 개요</li>
                        <li>문제점과 해결 방안</li>
                        <li>의의 및 필요성</li>
                    </ul>
                </div>
            </div>
            <div class="col">
                <div class="highlight-box">
                    <h3>🔧 상세 기능</h3>
                    <ul class="check-list">
                        <li>생기부 PDF 업로드 및 분석</li>
                        <li>AI 역량 정량화 (LLM 기반)</li>
                        <li>개인정보 보호 (PII 마스킹)</li>
                        <li>공공데이터 연계 진로 추천</li>
                        <li>교사용 맞춤형 리포트 생성</li>
                    </ul>
                </div>
            </div>
        </div>
        <div class="highlight-box" style="margin-top:4mm;">
            <h3>📊 데이터 및 기술</h3>
            <ul class="check-list" style="column-count:2; column-gap:10mm;">
                <li>활용 공공데이터 (KOSIS, 워크넷)</li>
                <li>AI 활용 과정 및 프롬프트 전략</li>
                <li>전체 시스템 아키텍처</li>
                <li>결론 및 기대효과</li>
            </ul>
        </div>
    </div>
</div>

<!-- ===== 슬라이드 3: 개발 동기 ===== -->
<div class="page">
    <div class="slide-header">
        <h2>개발 동기 및 배경</h2>
        <span class="slide-num">3 / 15</span>
    </div>
    <div class="slide-body">
        <div class="card-grid">
            <div class="card red">
                <h3>📉 현실의 한계</h3>
                <p>
                    고등학생의 진로 결정은 대부분 주변 어른의 조언, 막연한 선호, 혹은 단순 성적에 의존합니다.
                    학생부에 기록된 방대한 활동 정보가 체계적으로 분석되지 않고 있습니다.
                </p>
            </div>
            <div class="card orange">
                <h3>📊 데이터의 단절</h3>
                <p>
                    KOSIS(통계청)와 워크넷(고용노동부)은 전공별 취업률, 직무 전망 등 핵심 데이터를 공개하고 있지만,
                    학생 개인의 역량과 연결되지 못하고 있습니다.
                </p>
            </div>
            <div class="card purple">
                <h3>🔒 개인정보 민감성</h3>
                <p>
                    학생부에는 이름, 학교명, 지역 등 민감한 개인정보가 포함되어 있어
                    외부 AI 서비스에 직접 입력하기 어렵습니다.
                </p>
            </div>
        </div>
        <div class="quote-box" style="margin-top:5mm;">
            ❝ 학생 한 명 한 명의 강점을 AI가 객관적으로 분석하고,
            공공데이터 기반으로 최적의 진로를 제안할 수 없을까? ❞
        </div>
        <p style="font-size:10pt; color:#555; margin-top:3mm; text-align:center;">
            → 이 질문에서 <strong>생기부 기반 AI 진로 추천 서비스</strong>가 탄생했습니다.
        </p>
    </div>
</div>

<!-- ===== 슬라이드 4: 서비스 개요 ===== -->
<div class="page">
    <div class="slide-header">
        <h2>서비스 개요</h2>
        <span class="slide-num">4 / 15</span>
    </div>
    <div class="slide-body">
        <div class="two-col">
            <div class="col">
                <div class="highlight-box">
                    <h3>🎯 서비스 목표</h3>
                    <ul class="check-list">
                        <li>학생생활기록부(생기부) PDF를 AI로 분석</li>
                        <li>역량을 정량화하여 공공데이터와 매칭</li>
                        <li>개인 맞춤형 전공·직무 추천 제공</li>
                        <li>교사용 비식별화 리포트 자동 생성</li>
                    </ul>
                </div>
                <div class="highlight-box" style="margin-top:4mm;">
                    <h3>👥 대상 사용자</h3>
                    <ul class="check-list">
                        <li><strong>학생</strong>: 진로 탐색, 역량 파악</li>
                        <li><strong>교사/담임</strong>: 학생 지도 참고용 리포트</li>
                        <li><strong>학부모</strong>: 객관적 진로 근거 확인</li>
                    </ul>
                </div>
            </div>
            <div class="col">
                <div class="highlight-box">
                    <h3>⚙️ 핵심 구성 요소</h3>
                    <table>
                        <tr><th>구성</th><th>내용</th></tr>
                        <tr><td>입력</td><td>학생생활기록부 PDF</td></tr>
                        <tr><td>분석</td><td>LLM + OCR 텍스트 파싱</td></tr>
                        <tr><td>보호</td><td>PII 마스킹 (비식별화)</td></tr>
                        <tr><td>데이터</td><td>KOSIS, 워크넷 공공 API</td></tr>
                        <tr><td>추천</td><td>벡터 유사도 + 가중치 점수</td></tr>
                        <tr><td>출력</td><td>진로 추천 결과 + PDF 리포트</td></tr>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- ===== 슬라이드 5: 문제점 및 해결방안 ===== -->
<div class="page">
    <div class="slide-header">
        <h2>문제점 및 해결 방안</h2>
        <span class="slide-num">5 / 15</span>
    </div>
    <div class="slide-body">
        <div class="two-col">
            <div class="col">
                <div class="problem-box">
                    <h3>❌ 문제 1: 주관적·비일관적 진로 평가</h3>
                    <p>교사나 학부모의 개인적 경험과 직관에 의존하여 학생마다 평가 기준이 다르고 일관성이 없음</p>
                </div>
                <div class="problem-box">
                    <h3>❌ 문제 2: 공공데이터 미활용</h3>
                    <p>통계청·고용부가 제공하는 취업률·직무전망 공개 데이터가 학생 진로 상담에 실질적으로 연결되지 않음</p>
                </div>
                <div class="problem-box">
                    <h3>❌ 문제 3: 개인정보 노출 위험</h3>
                    <p>생기부를 그대로 AI 서비스에 업로드하면 이름·학교·지역 등 민감 정보가 외부 서버에 전송됨</p>
                </div>
            </div>
            <div class="col">
                <div class="solution-box">
                    <h3>✅ 해결 1: LLM 기반 객관적 역량 정량화</h3>
                    <p>Gemini/GPT가 학업·활동·수상·동아리 등을 일관된 기준으로 분석, 6개 역량 점수(0~100)로 산출</p>
                </div>
                <div class="solution-box">
                    <h3>✅ 해결 2: 공공데이터 실시간 연계 추천</h3>
                    <p>KOSIS 취업률 × 워크넷 고용전망 × 학생 역량 점수를 가중치 알고리즘으로 결합하여 과학적 추천 생성</p>
                </div>
                <div class="solution-box">
                    <h3>✅ 해결 3: 자동 PII 마스킹으로 100% 비식별화</h3>
                    <p>이름·학교명·지역·생년월일 등을 LLM 전달 전 자동 마스킹, 개인정보 처리방침 준수</p>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- ===== 슬라이드 6: 의의 및 필요성 ===== -->
<div class="page">
    <div class="slide-header">
        <h2>의의 및 필요성</h2>
        <span class="slide-num">6 / 15</span>
    </div>
    <div class="slide-body">
        <div class="stat-row">
            <div class="stat-card">
                <div class="stat-num">78.5%</div>
                <div class="stat-label">4년제 대학 평균 취업률<br>(KOSIS 2023년 기준)</div>
            </div>
            <div class="stat-card">
                <div class="stat-num">전공</div>
                <div class="stat-label">취업률 최고 vs 최저<br>50%p 이상 격차 존재</div>
            </div>
            <div class="stat-card">
                <div class="stat-num">12,500+</div>
                <div class="stat-label">워크넷 직무 종류<br>체계적 연계 가능</div>
            </div>
            <div class="stat-card">
                <div class="stat-num">98%</div>
                <div class="stat-label">교사가 진로지도 시<br>데이터 기반 도구 필요 응답</div>
            </div>
        </div>
        <div class="card-grid" style="margin-top:4mm;">
            <div class="card blue">
                <h3>🎓 교육적 의의</h3>
                <p>공교육 현장에서 AI를 활용한 맞춤형 진로 교육의 새로운 모델을 제시합니다. 
                학생의 잠재력을 데이터로 발굴하는 새로운 패러다임입니다.</p>
            </div>
            <div class="card green">
                <h3>🏛 공공데이터 가치 실현</h3>
                <p>정부가 개방한 교육·고용 데이터를 실제 학생 진로 결정에 연결함으로써
                공공데이터의 실질적 활용 가치를 극대화합니다.</p>
            </div>
            <div class="card purple">
                <h3>🛡 개인정보 선도 모델</h3>
                <p>AI 분석 전 완전한 비식별화를 적용함으로써 개인정보보호법을 준수하면서도
                고품질 분석을 제공하는 모범 사례를 제시합니다.</p>
            </div>
        </div>
    </div>
</div>

<!-- ===== 슬라이드 7: 기능 1 - 생기부 분석 ===== -->
<div class="page">
    <div class="slide-header">
        <h2>상세 기능 1 · 생기부 PDF 업로드 및 분석</h2>
        <span class="slide-num">7 / 15</span>
    </div>
    <div class="slide-body">
        <div class="two-col">
            <div class="col">
                <div class="highlight-box">
                    <h3>📄 입력 처리 과정</h3>
                    <ul class="check-list">
                        <li>사용자가 학생생활기록부 PDF 파일 업로드</li>
                        <li>파일 형식·크기 검증 (10MB 이하 PDF)</li>
                        <li>pdfplumber 라이브러리로 1차 텍스트 추출</li>
                        <li>텍스트 추출 실패 시 Tesseract OCR 자동 fallback</li>
                        <li>추출된 텍스트 구조화 (교과/비교과/수상/활동 분류)</li>
                    </ul>
                </div>
                <div class="highlight-box" style="margin-top:4mm;">
                    <h3>🔍 추출 항목</h3>
                    <ul class="check-list">
                        <li>교과 성적 및 과목별 세부사항(세특)</li>
                        <li>창의적 체험활동 (자율·동아리·봉사·진로)</li>
                        <li>수상 경력 및 독서활동 기록</li>
                        <li>행동특성 및 종합의견</li>
                    </ul>
                </div>
            </div>
            <div class="col">
                <div class="highlight-box">
                    <h3>⚙️ 비동기 처리 파이프라인</h3>
                    <div class="flow-row" style="flex-direction:column; align-items:flex-start; gap:2mm;">
                        <div style="background:white;border:1px solid #0f3460;border-radius:6px;padding:3mm 5mm;width:100%;font-size:9.5pt;">
                            <strong>① PENDING</strong> — 파일 업로드 완료, 큐 대기
                        </div>
                        <div style="font-size:10pt;color:#0f3460;padding-left:5mm;">↓</div>
                        <div style="background:white;border:1px solid #0f3460;border-radius:6px;padding:3mm 5mm;width:100%;font-size:9.5pt;">
                            <strong>② PARSING</strong> — PDF 텍스트 추출 + PII 마스킹
                        </div>
                        <div style="font-size:10pt;color:#0f3460;padding-left:5mm;">↓</div>
                        <div style="background:white;border:1px solid #0f3460;border-radius:6px;padding:3mm 5mm;width:100%;font-size:9.5pt;">
                            <strong>③ TAGGING</strong> — AI 역량 분석 및 점수 산출
                        </div>
                        <div style="font-size:10pt;color:#0f3460;padding-left:5mm;">↓</div>
                        <div style="background:white;border:1px solid #0f3460;border-radius:6px;padding:3mm 5mm;width:100%;font-size:9.5pt;">
                            <strong>④ RECOMMENDING</strong> — 공공데이터 연계 추천
                        </div>
                        <div style="font-size:10pt;color:#0f3460;padding-left:5mm;">↓</div>
                        <div style="background:#0f3460;color:white;border-radius:6px;padding:3mm 5mm;width:100%;font-size:9.5pt;">
                            <strong>⑤ COMPLETED</strong> — 결과 조회 및 리포트 생성
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="source-note">
            * Celery + Redis 기반 비동기 처리로 대용량 파일도 안정적으로 분석 가능
        </div>
    </div>
</div>

<!-- ===== 슬라이드 8: 기능 2 - AI 역량 분석 ===== -->
<div class="page">
    <div class="slide-header">
        <h2>상세 기능 2 · AI 기반 역량 정량화</h2>
        <span class="slide-num">8 / 15</span>
    </div>
    <div class="slide-body">
        <div class="highlight-box">
            <h3>🤖 AI 역량 분석 방식</h3>
            <p>
                비식별화된 생기부 텍스트를 LLM(Gemini 1.5 Flash / GPT-4o)에 전달하여 
                6가지 핵심 역량을 각각 0~100점으로 정량화합니다.
                추론 결과는 원본 텍스트와 자동 대조(evidence span 검증)하여 AI 환각을 최소화합니다.
            </p>
        </div>
        <div class="card-grid" style="margin-top:4mm;">
            <div class="card blue">
                <h3>📐 논리·수리 역량</h3>
                <p>수학·과학 세특, 탐구보고서, 수리 관련 수상 기록을 종합 평가</p>
            </div>
            <div class="card green">
                <h3>✍️ 언어·표현 역량</h3>
                <p>국어·영어 세특, 발표활동, 독서기록, 글쓰기 관련 활동 평가</p>
            </div>
            <div class="card orange">
                <h3>🎨 창의·예술 역량</h3>
                <p>예술·창작 동아리, 아이디어 공모전, 창의 문제해결 활동 평가</p>
            </div>
            <div class="card purple">
                <h3>🤝 사회·리더십 역량</h3>
                <p>봉사활동, 학생회·임원 활동, 협동 프로젝트 참여 실적 평가</p>
            </div>
            <div class="card red">
                <h3>🔬 탐구·연구 역량</h3>
                <p>실험·연구 보고서, 과학탐구 동아리, R&E 프로그램 참여 평가</p>
            </div>
            <div class="card" style="border-left-color:#2d8a5e;">
                <h3>💡 진로 일관성</h3>
                <p>3년간 활동의 방향성·일관성, 목표 직무와의 연계도 종합 평가</p>
            </div>
        </div>
        <div class="source-note">
            * 출력 형식: 구조화된 JSON (역량명, 점수, 근거 텍스트 span 포함) — 환각 검증 후 DB 저장
        </div>
    </div>
</div>

<!-- ===== 슬라이드 9: 기능 3 - 개인정보 보호 ===== -->
<div class="page">
    <div class="slide-header">
        <h2>상세 기능 3 · 개인정보 자동 비식별화</h2>
        <span class="slide-num">9 / 15</span>
    </div>
    <div class="slide-body">
        <div class="two-col">
            <div class="col">
                <div class="highlight-box">
                    <h3>🔒 PII 마스킹 처리 항목</h3>
                    <table>
                        <tr><th>항목</th><th>처리 방식</th></tr>
                        <tr><td>학생 이름</td><td>홍○○ 형태로 치환</td></tr>
                        <tr><td>학교명</td><td>○○고등학교로 마스킹</td></tr>
                        <tr><td>교사명</td><td>담임교사로 일반화</td></tr>
                        <tr><td>생년월일</td><td>연도만 유지, 월일 제거</td></tr>
                        <tr><td>지역명</td><td>광역시·도 단위로만 유지</td></tr>
                        <tr><td>기타 식별정보</td><td>정규식 + LLM 2중 검출</td></tr>
                    </table>
                </div>
            </div>
            <div class="col">
                <div class="highlight-box">
                    <h3>🛡 보안 처리 흐름</h3>
                    <ul class="check-list">
                        <li>업로드 즉시 서버 메모리 내에서만 처리</li>
                        <li>원본 PDF는 암호화 후 격리 저장</li>
                        <li>LLM에는 마스킹된 텍스트만 전달</li>
                        <li>분석 완료 후 임시 텍스트 즉시 삭제</li>
                        <li>결과 DB에는 비식별 정보만 저장</li>
                        <li>JWT 인증으로 본인 데이터만 접근 가능</li>
                    </ul>
                </div>
                <div class="highlight-box" style="margin-top:4mm; background:#eafaf1; border-color:#27ae60;">
                    <h3>✅ 법적 준거</h3>
                    <p style="font-size:9.5pt;">
                        개인정보보호법 제23조(민감정보 처리 제한), 
                        교육정보화법, GDPR 정신에 부합하는 
                        최소 수집·목적 외 처리 금지 원칙을 준수합니다.
                    </p>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- ===== 슬라이드 10: 기능 4 - 진로 추천 ===== -->
<div class="page">
    <div class="slide-header">
        <h2>상세 기능 4 · 공공데이터 연계 진로 추천</h2>
        <span class="slide-num">10 / 15</span>
    </div>
    <div class="slide-body">
        <div class="two-col">
            <div class="col">
                <div class="highlight-box">
                    <h3>🧮 추천 점수 산출 공식</h3>
                    <div style="background:white;border:1px solid #ddd;border-radius:6px;padding:4mm;margin:3mm 0;font-size:9pt;line-height:1.8;">
                        <strong>최종 추천점수 =</strong><br>
                        &nbsp;&nbsp;역량 적합도 점수 × 0.50<br>
                        + KOSIS 취업률 (%) × 0.30<br>
                        + 워크넷 고용전망 지수 × 0.20<br>
                        <br>
                        * 벡터 임베딩(pgvector) 유사도로<br>
                        &nbsp;&nbsp;관련 전공·직무 후보군 1차 필터링
                    </div>
                    <ul class="check-list">
                        <li>전공 추천 Top 5, 직무 추천 Top 5 산출</li>
                        <li>각 추천마다 근거 텍스트·점수 투명하게 제공</li>
                        <li>신뢰도(confidence) 수치 함께 표시</li>
                    </ul>
                </div>
            </div>
            <div class="col">
                <div class="highlight-box">
                    <h3>📊 추천 결과 예시</h3>
                    <table>
                        <tr><th>순위</th><th>추천 전공</th><th>취업률</th><th>적합도</th></tr>
                        <tr><td>1위</td><td>컴퓨터공학</td><td>82.3%</td><td>91점</td></tr>
                        <tr><td>2위</td><td>소프트웨어학</td><td>80.1%</td><td>88점</td></tr>
                        <tr><td>3위</td><td>수학교육</td><td>76.5%</td><td>79점</td></tr>
                        <tr><td>4위</td><td>전자공학</td><td>78.9%</td><td>75점</td></tr>
                        <tr><td>5위</td><td>산업공학</td><td>74.2%</td><td>71점</td></tr>
                    </table>
                    <p style="font-size:8.5pt;color:#666;margin-top:2mm;">
                        ※ 샘플 데이터 예시 / 실제 결과는 개인별 상이
                    </p>
                </div>
            </div>
        </div>
        <div class="source-note">
            * 출처: KOSIS 교육통계 취업률(2023), 워크넷 직업전망정보 API — 라이선스: 공공누리 1유형
        </div>
    </div>
</div>

<!-- ===== 슬라이드 11: 기능 5 - 리포트 생성 ===== -->
<div class="page">
    <div class="slide-header">
        <h2>상세 기능 5 · 교사용 맞춤형 리포트 자동 생성</h2>
        <span class="slide-num">11 / 15</span>
    </div>
    <div class="slide-body">
        <div class="two-col">
            <div class="col">
                <div class="highlight-box">
                    <h3>📋 리포트 구성 항목</h3>
                    <ul class="check-list">
                        <li>학생 정보 (비식별화: 학년/유형/지역만 표시)</li>
                        <li>6대 핵심 역량 점수 및 의견</li>
                        <li>추천 진로 시나리오 Top 2 (점수·근거 포함)</li>
                        <li>교사 활용 방안 및 차기 액션플랜</li>
                        <li>추천 신뢰도 및 AI 분석 면책 조항</li>
                    </ul>
                </div>
                <div class="highlight-box" style="margin-top:4mm;">
                    <h3>🖨 출력 사양</h3>
                    <ul class="check-list">
                        <li>A4 PDF 형식, 학년부 공문 배포 적합</li>
                        <li>WeasyPrint 엔진 기반 고품질 렌더링</li>
                        <li>Celery 비동기 처리 후 다운로드 링크 제공</li>
                    </ul>
                </div>
            </div>
            <div class="col">
                <div class="problem-box" style="background:#f0f4ff;border-color:#2471a3;">
                    <h3 style="color:#1a5276;">📝 리포트 활용 시나리오</h3>
                    <p style="font-size:9.5pt;">
                        <strong>① 1:1 학생 상담</strong><br>
                        담임교사가 역량 그래프와 추천 이유를 보며 심층 대화<br><br>
                        <strong>② 학부모 진학 상담</strong><br>
                        객관적 데이터 기반으로 막연한 불안감 해소<br><br>
                        <strong>③ 진로 관련 수업 자료</strong><br>
                        진로와 직업 수업에서 실제 사례로 활용 가능<br><br>
                        <strong>④ 학교 진로 프로그램 운영</strong><br>
                        학교 단위 집계 분석으로 특화 프로그램 기획
                    </p>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- ===== 슬라이드 12: 활용 공공 데이터 ===== -->
<div class="page">
    <div class="slide-header">
        <h2>활용한 공공 데이터</h2>
        <span class="slide-num">12 / 15</span>
    </div>
    <div class="slide-body">
        <table>
            <tr>
                <th style="width:15%;">데이터명</th>
                <th style="width:15%;">제공 기관</th>
                <th style="width:25%;">주요 내용</th>
                <th style="width:25%;">활용 방법</th>
                <th style="width:10%;">라이선스</th>
                <th style="width:10%;">출처</th>
            </tr>
            <tr>
                <td><strong>대학 졸업자<br>취업 통계</strong></td>
                <td>통계청<br>(KOSIS)</td>
                <td>전공 계열별·학교 유형별 취업률, 대학원 진학률, 평균 임금</td>
                <td>추천 점수 산출 시 취업률 가중치(30%) 적용. 전공별 비교 차트 시각화</td>
                <td>공공누리<br>1유형</td>
                <td>kosis.kr</td>
            </tr>
            <tr>
                <td><strong>직업정보<br>OPEN API</strong></td>
                <td>한국고용<br>정보원<br>(워크넷)</td>
                <td>직무별 채용 수요, 임금 수준, 고용 전망(5년), 필요 역량 태그</td>
                <td>직무 추천 점수에 고용전망 가중치(20%) 적용. 실시간 API 호출</td>
                <td>공공누리<br>1유형</td>
                <td>work.go.kr</td>
            </tr>
            <tr>
                <td><strong>교육통계<br>서비스</strong></td>
                <td>한국교육<br>개발원<br>(KEDI)</td>
                <td>학교급별 학생 수, 진로 관련 교육 현황, 진학·취업 경로 통계</td>
                <td>서비스 배경 데이터 및 통계 인포그래픽 근거 자료로 활용</td>
                <td>공공누리<br>1유형</td>
                <td>kedi.re.kr</td>
            </tr>
            <tr>
                <td><strong>국가직무능력<br>표준 (NCS)</strong></td>
                <td>한국직업능력<br>개발원</td>
                <td>800여 개 직무의 능력단위, 수행준거, 필요 지식·기술 목록</td>
                <td>LLM 프롬프트에서 역량 태그를 NCS 직무 분류체계에 맞춰 매핑</td>
                <td>공공누리<br>1유형</td>
                <td>ncs.go.kr</td>
            </tr>
        </table>
        <div class="source-note" style="margin-top:4mm;">
            ※ 모든 공공데이터는 공공누리 1유형(출처표시) 조건 하에 활용하며, 수집 주기는 분기별 ETL 자동 업데이트로 최신성을 유지합니다.
        </div>
    </div>
</div>

<!-- ===== 슬라이드 13: AI 활용 과정 ===== -->
<div class="page">
    <div class="slide-header">
        <h2>AI 활용 과정 (프롬프트 · 모델 · 처리 · 분석 · 추론)</h2>
        <span class="slide-num">13 / 15</span>
    </div>
    <div class="slide-body">
        <div class="two-col">
            <div class="col">
                <div class="highlight-box">
                    <h3>🤖 활용 AI 도구</h3>
                    <ul class="check-list">
                        <li><strong>Gemini 1.5 Flash</strong> — 역량 분석·추천 이유 생성</li>
                        <li><strong>text-embedding-004</strong> — 텍스트 벡터 임베딩</li>
                        <li><strong>Tesseract OCR</strong> — 이미지 PDF 텍스트 추출</li>
                        <li><strong>pgvector</strong> — 벡터 유사도 검색 (PostgreSQL)</li>
                    </ul>
                </div>
                <div class="highlight-box" style="margin-top:4mm;">
                    <h3>📝 프롬프트 전략</h3>
                    <ul class="check-list">
                        <li>시스템 프롬프트: 역할·출력 JSON 스키마 정의</li>
                        <li>Few-shot 예시로 일관된 점수 체계 학습</li>
                        <li>Chain-of-Thought로 추론 과정 명시 요구</li>
                        <li>evidence_span 필드로 원문 근거 추출 강제</li>
                        <li>temperature=0.2 설정으로 일관성 확보</li>
                    </ul>
                </div>
            </div>
            <div class="col">
                <div class="highlight-box">
                    <h3>⚙️ AI 처리 절차 요약</h3>
                    <div style="font-size:9.5pt; line-height:1.8;">
                        <div style="background:white;border:1px solid #0f3460;border-radius:6px;padding:2mm 4mm;margin:1mm 0;">
                            <strong>① 입력 전처리</strong>: 생기부 텍스트 → PII 마스킹 → 섹션 분류
                        </div>
                        <div style="text-align:center;color:#0f3460;font-size:8pt;">↓</div>
                        <div style="background:white;border:1px solid #0f3460;border-radius:6px;padding:2mm 4mm;margin:1mm 0;">
                            <strong>② LLM 역량 분석</strong>: 마스킹 텍스트 → Gemini API → JSON 역량 점수
                        </div>
                        <div style="text-align:center;color:#0f3460;font-size:8pt;">↓</div>
                        <div style="background:white;border:1px solid #0f3460;border-radius:6px;padding:2mm 4mm;margin:1mm 0;">
                            <strong>③ 환각 검증</strong>: evidence_span ↔ 원본 텍스트 자동 대조
                        </div>
                        <div style="text-align:center;color:#0f3460;font-size:8pt;">↓</div>
                        <div style="background:white;border:1px solid #0f3460;border-radius:6px;padding:2mm 4mm;margin:1mm 0;">
                            <strong>④ 벡터 임베딩</strong>: 역량 태그 → text-embedding → pgvector 저장
                        </div>
                        <div style="text-align:center;color:#0f3460;font-size:8pt;">↓</div>
                        <div style="background:white;border:1px solid #0f3460;border-radius:6px;padding:2mm 4mm;margin:1mm 0;">
                            <strong>⑤ 최종 추천</strong>: 공공데이터 × 역량 × 임베딩 가중치 점수 산출
                        </div>
                        <div style="text-align:center;color:#0f3460;font-size:8pt;">↓</div>
                        <div style="background:#0f3460;color:white;border-radius:6px;padding:2mm 4mm;margin:1mm 0;">
                            <strong>⑥ 결과 저장 및 리포트 생성</strong>: DB 저장 → PDF 리포트 렌더링
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="source-note">
            * 생성형 AI 활용 입력값: 비식별화된 생기부 텍스트 | 추가 산출물: 역량 JSON, 근거 evidence_span, 추천 이유 텍스트
        </div>
    </div>
</div>

<!-- ===== 슬라이드 14: 기술 스택 및 아키텍처 ===== -->
<div class="page">
    <div class="slide-header">
        <h2>기술 스택 및 시스템 아키텍처</h2>
        <span class="slide-num">14 / 15</span>
    </div>
    <div class="slide-body">
        <div class="card-grid">
            <div class="card blue">
                <h3>🎨 프론트엔드</h3>
                <p>
                    <strong>Next.js 14</strong> + TypeScript<br>
                    React Server Components<br>
                    Axios (API 통신)<br>
                    Glassmorphism UI 설계
                </p>
            </div>
            <div class="card green">
                <h3>⚙️ 백엔드 API</h3>
                <p>
                    <strong>FastAPI</strong> (Python 3.11)<br>
                    SQLAlchemy ORM<br>
                    Pydantic v2 (데이터 검증)<br>
                    JWT 인증 / CORS 처리
                </p>
            </div>
            <div class="card orange">
                <h3>📦 비동기 처리</h3>
                <p>
                    <strong>Celery</strong> (태스크 큐)<br>
                    Celery Beat (스케줄러)<br>
                    Redis (브로커/캐시)<br>
                    상태 폴링 API
                </p>
            </div>
            <div class="card purple">
                <h3>🗄 데이터 저장</h3>
                <p>
                    <strong>PostgreSQL 16</strong><br>
                    pgvector (벡터 검색)<br>
                    Alembic (DB 마이그레이션)<br>
                    Redis (세션/캐시)
                </p>
            </div>
            <div class="card red">
                <h3>🤖 AI / ML</h3>
                <p>
                    <strong>Gemini 1.5 Flash</strong> (주 LLM)<br>
                    OpenAI GPT-4o (fallback)<br>
                    Tesseract OCR<br>
                    pdfplumber (PDF 파싱)
                </p>
            </div>
            <div class="card" style="border-left-color:#2c3e50;">
                <h3>🐳 인프라</h3>
                <p>
                    <strong>Docker Compose</strong><br>
                    6개 마이크로서비스<br>
                    헬스체크 자동화<br>
                    WeasyPrint (PDF 렌더링)
                </p>
            </div>
        </div>
        <div class="source-note" style="margin-top:3mm;">
            * 전체 서비스는 Docker Compose로 단일 명령어 (docker compose up) 실행 — 개발/운영 환경 완전 동일
        </div>
    </div>
</div>

<!-- ===== 슬라이드 15: 결론 및 기대효과 ===== -->
<div class="page">
    <div class="slide-header">
        <h2>결론 및 기대효과</h2>
        <span class="slide-num">15 / 15</span>
    </div>
    <div class="slide-body">
        <div class="two-col">
            <div class="col">
                <div class="card-grid" style="flex-direction:column; gap:3mm;">
                    <div class="card green">
                        <h3>📈 기대효과 1: 진로 결정 정확도 향상</h3>
                        <p>감에 의존하던 진로 결정을 데이터 기반으로 전환, 전공 미스매치 감소 및 대학 적응도 향상</p>
                    </div>
                    <div class="card blue">
                        <h3>🏫 기대효과 2: 교사 업무 효율화</h3>
                        <p>수십 명의 학생 진로 상담 자료를 AI가 자동 생성, 교사는 심층 상담에 집중 가능</p>
                    </div>
                    <div class="card orange">
                        <h3>🛡 기대효과 3: 개인정보 보호 선례</h3>
                        <p>교육 AI 서비스에서 비식별화 선적용 모델을 제시, 향후 교육 AI 서비스의 표준 모델로 확산 가능</p>
                    </div>
                </div>
            </div>
            <div class="col">
                <div class="quote-box" style="margin-bottom:4mm;">
                    ❝ 학생의 강점을 데이터로 발굴하고,<br>
                    공공데이터로 미래를 설계하다 ❞
                </div>
                <div class="highlight-box">
                    <h3>🗺 향후 발전 방향</h3>
                    <ul class="check-list">
                        <li>실제 학교 현장 파일럿 테스트 (2026년 하반기)</li>
                        <li>교육부 API 연동으로 실시간 정책 반영</li>
                        <li>학생 포트폴리오 누적 관리 기능 추가</li>
                        <li>취업률 예측 ML 모델 자체 학습 (장기)</li>
                    </ul>
                </div>
                <div class="source-note" style="margin-top:4mm; font-size:9pt;">
                    생성형 AI 활용 도구: Gemini 1.5 Flash (입력값: 비식별화 생기부 텍스트, 추가 산출물: 역량 점수 JSON + 추천 이유 + evidence_span)
                </div>
            </div>
        </div>
    </div>
</div>

</body>
</html>"""

if __name__ == "__main__":
    from weasyprint import HTML
    import os

    output_path = "/app/career_advisor_ai_presentation.pdf"
    print("Generating PDF...")
    HTML(string=HTML_CONTENT).write_pdf(output_path)
    print(f"PDF saved to {output_path}")
    print(f"File size: {os.path.getsize(output_path):,} bytes")
