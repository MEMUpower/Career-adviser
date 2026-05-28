# 생기부 업로드 기반 + 공공데이터 연계 진로 추천 서비스 MVP 실행 가이드

본 프로젝트는 고등학생의 학교생활기록부(생활기록부 PDF)를 분석하여 종합 역량을 정량화하고, 공공데이터(KOSIS 대학전공 취업률, 워크넷 직무 고용 전망)와 가중치를 결합하여 적합한 전공/직무 시나리오를 추천하는 풀스택 서비스 MVP입니다.

---

## 🛠️ 기술 스택 및 구조

- **Frontend**: Next.js 14 (App Router) + TypeScript + Tailwind CSS (Glassmorphism UI 포함)
- **Backend**: FastAPI + Python 3.11 + SQLAlchemy ORM (Pydantic v2)
- **DB**: PostgreSQL 16 + pgvector (768차원 벡터 검색)
- **Queue/Cache**: Redis 7 + Celery (비동기 분석 파이프라인 및 Beat 스케줄러)
- **Infra**: Docker Compose

---

## 📂 프로젝트 파일 트리

```
career-advisor/
├── docker-compose.yml
├── .env.example
├── README.md
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic/
│   └── app/
│       ├── main.py
│       ├── database.py
│       ├── config.py
│       ├── models/
│       ├── schemas/
│       ├── api/
│       ├── pipeline/
│       ├── tasks/
│       └── etl/
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── tailwind.config.ts
    └── src/
        ├── app/
        ├── components/
        └── lib/
```

---

## 🚀 로컬 실행 방법 (Docker Compose)

### 1. 환경 변수 설정
`.env.example` 파일을 복사하여 `.env` 파일을 생성합니다.
```bash
cp .env.example .env
```
*주의: OpenAI API 키가 없는 경우에도 기본 탑재된 Mock Pipeline 모듈이 작동하여 테스트가 가능합니다.*

### 2. 컨테이너 빌드 및 구동
로컬 인프라(FastAPI, Next.js, PostgreSQL, Redis, Celery Worker, Beat)를 한 번에 빌드하고 구동합니다.
```bash
docker compose up --build -d
```

### 3. 접속 주소
- **프론트엔드 웹 UI**: [http://localhost:3000](http://localhost:3000)
- **백엔드 API Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Redis 호스트**: `localhost:6379`
- **PostgreSQL 호스트**: `localhost:5432`

---

## 🧪 테스트 시나리오 및 검증 방법

### 1. 백엔드 단위 테스트 구동 (pytest)
백엔드 로직의 비식별화 마스킹 검증, AI 환각 차단 알고리즘, 회원가입 API 동작 등을 테스트합니다.
```bash
# 로컬 가상환경 진입 또는 backend 컨테이너 내부 실행
docker compose exec backend pytest tests/ -v
```

### 2. 검증 테스트 시나리오
본 서비스의 정상 작동 및 개인정보 제어 여부를 검증하기 위한 3가지 표준 수동 시나리오입니다.

#### 📌 시나리오 A: 이공계 성향 학생 업로드 및 취업률 연계 추천
1. [http://localhost:3000/login](http://localhost:3050/login) 에서 가입(일반고, 서울 지역, 2학년) 후 로그인합니다.
2. [분석 시작] 메뉴에서 샘플 생활기록부 PDF를 업로드하고 [마스킹 활용 동의]를 체크합니다.
3. **분석 흐름 점검**: PENDING -> PARSING (마스킹) -> TAGGING (역량 점수 산출) -> RECOMMENDING (공공데이터 융합)을 거쳐 완료됩니다.
4. **결과 확인**: 전공 탭에 **컴퓨터공학과** 또는 **전자공학과**가 90점 이상의 높은 점수로 나타나며, KOSIS 제공 지표인 **평균 취업률 78.5%** 및 **최신 기준일 배지**가 우측 하단 카드로 매핑되어 노출되는지 확인합니다.

#### 📌 시나리오 B: AI 추천 환각 검증 (Explainability)
1. 추천 전공 상세 정보에서 **[생기부 발췌 근거 구절]** 섹션을 확인합니다.
2. 텍스트 본문 중 "정보 교과 시간에 스스로 아두이노 키트를 활용해 온도 조절 장치를 프로그래밍하여..." 구절에 노란색 형광펜 하이라이트가 부여되었는지 대조합니다.
3. 해당 하이라이트 구문이 업로드한 원본 생활기록부 파일 텍스트에 포함된 문장인지 검증합니다. (LLM이 지어낸 가짜 근거인 경우 `validate_evidences_against_record`에 의해 에러가 나도록 설계되어 있습니다.)

#### 📌 시나리오 C: 교사용 요약 리포트 PDF 다운로드
1. 가입 시 역할을 `teacher`로 지정하여 교사 계정을 생성합니다.
2. 분석이 완료된 학생 레코드의 결과 대시보드 [http://localhost:3000/dashboard/[id]](http://localhost:3000/dashboard/[id]) 에 접속합니다.
3. 상단 우측의 **[교사용 요약 리포트 (PDF) 발행]** 버튼을 클릭합니다.
4. 백그라운드 Weasyprint 빌드가 완료된 후 활성화되는 **[PDF 리포트 다운로드]** 링크를 클릭하여 다운로드된 파일의 레이아웃과 학생 비식별화 여부를 PDF 뷰어로 검증합니다.
