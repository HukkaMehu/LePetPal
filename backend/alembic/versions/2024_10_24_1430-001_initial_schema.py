"""initial schema

Revision ID: 001
Revises: 
Create Date: 2024-10-24 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('role', sa.String(50), nullable=False, server_default='owner'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # Create devices table
    op.create_table(
        'devices',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='offline'),
        sa.Column('last_seen_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('capabilities', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create events table
    # Enable TimescaleDB extension first
    op.execute('CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;')
    
    op.create_table(
        'events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ts', sa.TIMESTAMP(), nullable=False),
        sa.Column('type', sa.String(100), nullable=False),
        sa.Column('data', postgresql.JSONB(), nullable=True),
        sa.Column('video_ts_ms', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id', 'ts'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_events_ts', 'events', ['ts'])
    op.create_index('idx_events_user_type_ts', 'events', ['user_id', 'type', 'ts'])
    op.create_index(
        'idx_events_video_ts',
        'events',
        ['video_ts_ms'],
        postgresql_where=sa.text('video_ts_ms IS NOT NULL')
    )

    # Create hypertable for events
    op.execute("SELECT create_hypertable('events', 'ts', if_not_exists => TRUE);")

    # Create clips table
    op.create_table(
        'clips',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('start_ts', sa.TIMESTAMP(), nullable=False),
        sa.Column('duration_ms', sa.Integer(), nullable=False),
        sa.Column('s3_uri', sa.String(500), nullable=False),
        sa.Column('labels', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('preview_png', sa.String(500), nullable=True),
        sa.Column('share_token', sa.String(100), nullable=True, unique=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_clips_user_start', 'clips', ['user_id', 'start_ts'])

    # Create snapshots table
    op.create_table(
        'snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ts', sa.TIMESTAMP(), nullable=False),
        sa.Column('s3_uri', sa.String(500), nullable=False),
        sa.Column('labels', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_snapshots_user_ts', 'snapshots', ['user_id', 'ts'])

    # Create routines table
    op.create_table(
        'routines',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('cron', sa.String(100), nullable=False),
        sa.Column('steps', postgresql.JSONB(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create ai_metrics_daily table
    op.create_table(
        'ai_metrics_daily',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('sit_count', sa.Integer(), server_default='0'),
        sa.Column('stand_count', sa.Integer(), server_default='0'),
        sa.Column('lie_count', sa.Integer(), server_default='0'),
        sa.Column('fetch_count', sa.Integer(), server_default='0'),
        sa.Column('fetch_success_count', sa.Integer(), server_default='0'),
        sa.Column('treats_dispensed', sa.Integer(), server_default='0'),
        sa.Column('time_in_frame_min', sa.Integer(), server_default='0'),
        sa.Column('barks', sa.Integer(), server_default='0'),
        sa.Column('howls', sa.Integer(), server_default='0'),
        sa.Column('whines', sa.Integer(), server_default='0'),
        sa.Column('calm_minutes', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'date', name='uq_user_date'),
    )
    op.create_index('idx_metrics_user_date', 'ai_metrics_daily', ['user_id', 'date'])

    # Create models table
    op.create_table(
        'models',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('artifact_uri', sa.String(500), nullable=False),
        sa.Column('version', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='available'),
        sa.Column('model_metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint('name', 'version', name='uq_model_name_version'),
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('models')
    op.drop_table('ai_metrics_daily')
    op.drop_table('routines')
    op.drop_table('snapshots')
    op.drop_table('clips')
    
    # Drop events table (TimescaleDB hypertable)
    op.execute("DROP TABLE IF EXISTS events CASCADE;")
    
    op.drop_table('devices')
    op.drop_table('users')
    
    # Optionally drop TimescaleDB extension (commented out to avoid affecting other databases)
    # op.execute('DROP EXTENSION IF EXISTS timescaledb CASCADE;')
