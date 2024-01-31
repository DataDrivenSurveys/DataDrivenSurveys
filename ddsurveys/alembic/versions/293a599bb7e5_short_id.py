"""short_id

Revision ID: 293a599bb7e5
Revises: da503e3b823b
Create Date: 2023-09-11 13:49:05.169540

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '293a599bb7e5'
down_revision = 'da503e3b823b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('project', sa.Column('short_id', sa.Integer(), nullable=True))
    op.drop_column('project', 'num_responses')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('project', sa.Column('num_responses', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.drop_column('project', 'short_id')
    # ### end Alembic commands ###
