"""empty message

Revision ID: a382eded05e2
Revises: c8e970ef62ca
Create Date: 2020-07-25 22:21:02.770879

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a382eded05e2'
down_revision = 'c8e970ef62ca'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('project_members')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('project_members',
    sa.Column('project_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['project.id'], name='project_members_ibfk_1'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='project_members_ibfk_2'),
    mysql_collate='utf8_unicode_ci',
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
