-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create Enums
CREATE TYPE user_role AS ENUM ('student', 'teacher', 'admin');
CREATE TYPE record_status AS ENUM ('PENDING', 'PARSING', 'TAGGING', 'RECOMMENDING', 'COMPLETED', 'FAILED');
CREATE TYPE section_type AS ENUM ('교과', '세특', '창체', '독서', '수상', '진로활동');
CREATE TYPE recommendation_type AS ENUM ('전공', '직무군');
CREATE TYPE evidence_type AS ENUM ('MODEL', 'STATISTIC');
CREATE TYPE quality_flag AS ENUM ('FRESH', 'STALE', 'MISSING');

-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    role user_role NOT NULL DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Students Table
CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    masked_name VARCHAR NOT NULL,
    grade VARCHAR NOT NULL,
    school_type VARCHAR NOT NULL,
    region VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Records Table
CREATE TABLE records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    original_filename VARCHAR NOT NULL,
    stored_path VARCHAR NOT NULL,
    file_hash VARCHAR UNIQUE NOT NULL,
    status record_status NOT NULL DEFAULT 'PENDING',
    error_detail JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Parsed Sections Table
CREATE TABLE parsed_sections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    record_id UUID NOT NULL REFERENCES records(id) ON DELETE CASCADE,
    section_type section_type NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    page_number INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Profiles Table
CREATE TABLE profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    record_id UUID NOT NULL REFERENCES records(id) ON DELETE CASCADE UNIQUE,
    competency_scores JSONB NOT NULL,
    interest_tags JSONB NOT NULL,
    embedding vector(768),
    overall_confidence FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Public Metrics Table
CREATE TABLE public_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source VARCHAR NOT NULL,
    category VARCHAR NOT NULL,
    key_name VARCHAR NOT NULL,
    data JSONB NOT NULL,
    reference_year DATE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    quality_flag quality_flag NOT NULL DEFAULT 'FRESH'
);

-- Recommendations Table
CREATE TABLE recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    rec_type recommendation_type NOT NULL,
    rank INTEGER NOT NULL,
    target_name VARCHAR NOT NULL,
    score FLOAT NOT NULL,
    explanation TEXT NOT NULL,
    action_plan TEXT NOT NULL,
    confidence FLOAT DEFAULT 1.0,
    weight_snapshot JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Recommendation Evidence Table
CREATE TABLE recommendation_evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recommendation_id UUID NOT NULL REFERENCES recommendations(id) ON DELETE CASCADE,
    metric_id UUID REFERENCES public_metrics(id) ON DELETE SET NULL,
    evidence_span TEXT NOT NULL,
    section_type VARCHAR,
    evidence_type evidence_type NOT NULL DEFAULT 'MODEL',
    relevance_score FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Feedback Table
CREATE TABLE feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recommendation_id UUID NOT NULL REFERENCES recommendations(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit Logs Table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR NOT NULL,
    resource_type VARCHAR NOT NULL,
    resource_id VARCHAR NOT NULL,
    metadata JSONB,
    ip_address VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index Strategy
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_students_user_id ON students(user_id);
CREATE INDEX idx_records_student_id ON records(student_id);
CREATE INDEX idx_records_file_hash ON records(file_hash);
CREATE INDEX idx_parsed_sections_record_id ON parsed_sections(record_id);
CREATE INDEX idx_parsed_sections_type ON parsed_sections(section_type);
CREATE INDEX idx_profiles_record_id ON profiles(record_id);
CREATE INDEX idx_recommendations_profile_id ON recommendations(profile_id);
CREATE INDEX idx_recommendation_evidence_rec_id ON recommendation_evidence(recommendation_id);
CREATE INDEX idx_public_metrics_key_name ON public_metrics(key_name);
CREATE INDEX idx_feedback_rec_id ON feedback(recommendation_id);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);

-- Cosine Distance index for Vector searches
CREATE INDEX idx_profiles_embedding_cosine ON profiles USING hnsw (embedding vector_cosine_ops);
