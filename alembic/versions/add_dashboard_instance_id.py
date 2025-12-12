"""Add dashboard_instance_id columns

Revision ID: add_dashboard_instance_id
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_dashboard_instance_id'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add dashboard_instance_id column to projects table
    op.add_column('projects', sa.Column('dashboard_instance_id', sa.String(100), nullable=True))
    
    # Add dashboard_instance_id column to dashboard_deployments table
    op.add_column('dashboard_deployments', sa.Column('dashboard_instance_id', sa.String(100), nullable=True))


def downgrade():
    # Remove dashboard_instance_id column from dashboard_deployments table
    op.drop_column('dashboard_deployments', 'dashboard_instance_id')
    
    # Remove dashboard_instance_id column from projects table
    op.drop_column('projects', 'dashboard_instance_id')