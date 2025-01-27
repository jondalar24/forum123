"""Add role column to users

Revision ID: 64034456b8d7
Revises: ad143b90cf27
Create Date: 2024-09-14 11:28:21.284973+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '64034456b8d7'
down_revision = 'ad143b90cf27'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('role', sa.String(length=50), nullable=False, server_default='student'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'role')
    # ### end Alembic commands ###