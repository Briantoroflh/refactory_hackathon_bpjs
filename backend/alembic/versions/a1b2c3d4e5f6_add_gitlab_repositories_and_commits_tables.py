"""Add GitLab repositories and commits tables

Revision ID: a1b2c3d4e5f6
Revises: d4d9f9e80b2c
Create Date: 2026-05-12 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'd4d9f9e80b2c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create gitlab_repositories table
    op.create_table(
        'gitlab_repositories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('gitlab_project_id', sa.Integer(), nullable=False),
        sa.Column('gitlab_url', sa.String(500), nullable=False),
        sa.Column('gitlab_access_token', sa.String(500), nullable=False),
        sa.Column('last_sync_timestamp', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.project_id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id', name='uq_gitlab_repositories_project_id'),
    )
    op.create_index(op.f('ix_gitlab_repositories_gitlab_project_id'), 'gitlab_repositories', ['gitlab_project_id'], unique=False)

    # Create commits table
    op.create_table(
        'commits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('repository_id', sa.Integer(), nullable=False),
        sa.Column('git_hash', sa.String(40), nullable=False),
        sa.Column('author_name', sa.String(255), nullable=False),
        sa.Column('author_email', sa.String(255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('committed_at', sa.DateTime(), nullable=False),
        sa.Column('branch', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['repository_id'], ['gitlab_repositories.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('repository_id', 'git_hash', name='uq_commits_repository_git_hash'),
    )
    op.create_index(op.f('ix_commits_repository_id'), 'commits', ['repository_id'], unique=False)
    op.create_index(op.f('ix_commits_git_hash'), 'commits', ['git_hash'], unique=False)
    op.create_index(op.f('ix_commits_author_email'), 'commits', ['author_email'], unique=False)
    op.create_index(op.f('ix_commits_committed_at'), 'commits', ['committed_at'], unique=False)
    op.create_index(op.f('ix_commits_branch'), 'commits', ['branch'], unique=False)
    op.create_index(op.f('ix_commits_created_at'), 'commits', ['created_at'], unique=False)
    op.create_index('idx_commits_repository_committed_at', 'commits', ['repository_id', 'committed_at'], unique=False)
    op.create_index('idx_commits_author_email', 'commits', ['author_email'], unique=False)
    op.create_index('idx_commits_branch', 'commits', ['branch'], unique=False)


def downgrade() -> None:
    # Drop commits table
    op.drop_index('idx_commits_branch', table_name='commits')
    op.drop_index('idx_commits_author_email', table_name='commits')
    op.drop_index('idx_commits_repository_committed_at', table_name='commits')
    op.drop_index(op.f('ix_commits_created_at'), table_name='commits')
    op.drop_index(op.f('ix_commits_branch'), table_name='commits')
    op.drop_index(op.f('ix_commits_committed_at'), table_name='commits')
    op.drop_index(op.f('ix_commits_author_email'), table_name='commits')
    op.drop_index(op.f('ix_commits_git_hash'), table_name='commits')
    op.drop_index(op.f('ix_commits_repository_id'), table_name='commits')
    op.drop_table('commits')

    # Drop gitlab_repositories table
    op.drop_index(op.f('ix_gitlab_repositories_gitlab_project_id'), table_name='gitlab_repositories')
    op.drop_table('gitlab_repositories')
