"""add topics table

Este archivo de migración crea una tabla topics para almacenar los temas, 
con una referencia a la tabla users para el autor del tema

Revision ID: e8634796ad93
Revises: 3d47c515809d
Create Date: 2023-02-14 10:08:20.947653+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8634796ad93'
down_revision = '3d47c515809d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('topics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('description', sa.String(length=123), nullable=False),
    sa.Column('title', sa.String(length=30), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('topics')
    # ### end Alembic commands ###
