"""Add Match and UserInteraction models for post-match functionality

Revision ID: add_match_models
Revises: add_keywords_to_membership
Create Date: 2025-01-06 05:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_match_models'
down_revision = 'add_keywords_to_membership'
branch_labels = None
depends_on = None


def upgrade():
    # Create Match table
    op.create_table('match',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user1_id', sa.Integer(), nullable=False),
    sa.Column('user2_id', sa.Integer(), nullable=False),
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.Column('matched_at', sa.DateTime(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
    sa.ForeignKeyConstraint(['user1_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['user2_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user1_id', 'user2_id', 'event_id', name='unique_match_pair'),
    sa.CheckConstraint('user1_id != user2_id', name='no_self_match')
    )
    
    # Create UserInteraction table
    op.create_table('user_interaction',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('target_user_id', sa.Integer(), nullable=False),
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.Column('action', sa.String(length=10), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
    sa.ForeignKeyConstraint(['target_user_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'target_user_id', 'event_id', name='unique_user_interaction'),
    sa.CheckConstraint('user_id != target_user_id', name='no_self_interaction'),
    sa.CheckConstraint("action IN ('like', 'pass')", name='valid_action')
    )


def downgrade():
    op.drop_table('user_interaction')
    op.drop_table('match')
