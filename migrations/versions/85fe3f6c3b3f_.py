"""empty message

Revision ID: 85fe3f6c3b3f
Revises: 0f2e43731d1e
Create Date: 2020-07-21 20:49:54.455287

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '85fe3f6c3b3f'
down_revision = '0f2e43731d1e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('project_user_request', 'positive_status')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('project_user_request', sa.Column('positive_status', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
