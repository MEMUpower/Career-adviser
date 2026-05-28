"""Initial migration

Revision ID: 0001_initial
Revises: 
Create Date: 2026-05-22 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '0001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Enable Vector Extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Table Users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('role', sa.Enum('student', 'teacher', 'admin', name='userrole'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'))
    )
    op.create_index('idx_users_email', 'users', ['email'])

    # Table Students
    op.create_table(
        'students',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('masked_name', sa.String(), nullable=False),
        sa.Column('grade', sa.String(), nullable=False),
        sa.Column('school_type', sa.String(), nullable=False),
        sa.Column('region', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'))
    )
    op.create_index('idx_students_user_id', 'students', ['user_id'])

    # Table Records
    op.create_table(
        'records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('students.id', ondelete='CASCADE'), nullable=False),
        sa.Column('original_filename', sa.String(), nullable=False),
        sa.Column('stored_path', sa.String(), nullable=False),
        sa.Column('file_hash', sa.String(), nullable=False, unique=True),
        sa.Column('status', sa.Enum('PENDING', 'PARSING', 'TAGGING', 'RECOMMENDING', 'COMPLETED', 'FAILED', name='recordstatus'), nullable=False),
        sa.Column('error_detail', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'))
    )
    op.create_index('idx_records_student_id', 'records', ['student_id'])
    op.create_index('idx_records_file_hash', 'records', ['file_hash'])

    # Table Parsed Sections
    op.create_table(
        'parsed_sections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('record_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('records.id', ondelete='CASCADE'), nullable=False),
        sa.Column('section_type', sa.Enum('교과', '세특', '창체', '독서', '수상', '진로활동', name='sectiontype'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'))
    )
    op.create_index('idx_parsed_sections_record_id', 'parsed_sections', ['record_id'])

    # Table Profiles
    op.create_table(
        'profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('record_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('records.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('competency_scores', sa.JSON(), nullable=False),
        sa.Column('interest_tags', sa.JSON(), nullable=False),
        sa.Column('embedding', Vector(768), nullable=True),
        sa.Column('overall_confidence', sa.Float(), default=1.0),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'))
    )
    op.create_index('idx_profiles_record_id', 'profiles', ['record_id'])

    # Table Public Metrics
    op.create_table(
        'public_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('key_name', sa.String(), nullable=False),
        sa.Column('data', sa.JSON(), nullable=False),
        sa.Column('reference_year', sa.Date(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('quality_flag', sa.Enum('FRESH', 'STALE', 'MISSING', name='qualityflag'), nullable=False)
    )
    op.create_index('idx_public_metrics_key_name', 'public_metrics', ['key_name'])

    # Table Recommendations
    op.create_table(
        'recommendations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('profile_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('rec_type', sa.Enum('전공', '직무군', name='recommendationtype'), nullable=False),
        sa.Column('rank', sa.Integer(), nullable=False),
        sa.Column('target_name', sa.String(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column('action_plan', sa.Text(), nullable=False),
        sa.Column('confidence', sa.Float(), default=1.0),
        sa.Column('weight_snapshot', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'))
    )
    op.create_index('idx_recommendations_profile_id', 'recommendations', ['profile_id'])

    # Table Recommendation Evidence
    op.create_table(
        'recommendation_evidence',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('recommendation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('recommendations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('metric_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('public_metrics.id', ondelete='SET NULL'), nullable=True),
        sa.Column('evidence_span', sa.Text(), nullable=False),
        sa.Column('section_type', sa.String(), nullable=True),
        sa.Column('evidence_type', sa.Enum('MODEL', 'STATISTIC', name='evidencetype'), nullable=False),
        sa.Column('relevance_score', sa.Float(), default=1.0),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'))
    )
    op.create_index('idx_recommendation_evidence_rec_id', 'recommendation_evidence', ['recommendation_id'])

    # Table Feedback
    op.create_table(
        'feedback',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('recommendation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('recommendations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'))
    )
    op.create_index('idx_feedback_rec_id', 'feedback', ['recommendation_id'])

    # Table Audit Logs
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('resource_type', sa.String(), nullable=False),
        sa.Column('resource_id', sa.String(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'))
    )
    op.create_index('idx_audit_logs_user_id', 'audit_logs', ['user_id'])

    # Vector HNSW Index Strategy
    op.execute("CREATE INDEX idx_profiles_embedding_cosine ON profiles USING hnsw (embedding vector_cosine_ops)")

def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('feedback')
    op.drop_table('recommendation_evidence')
    op.drop_table('recommendations')
    op.drop_table('public_metrics')
    op.drop_table('profiles')
    op.drop_table('parsed_sections')
    op.drop_table('records')
    op.drop_table('students')
    op.drop_table('users')
    op.execute("DROP TYPE IF EXISTS userrole CASCADE")
    op.execute("DROP TYPE IF EXISTS recordstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS sectiontype CASCADE")
    op.execute("DROP TYPE IF EXISTS recommendationtype CASCADE")
    op.execute("DROP TYPE IF EXISTS evidencetype CASCADE")
    op.execute("DROP TYPE IF EXISTS qualityflag CASCADE")
