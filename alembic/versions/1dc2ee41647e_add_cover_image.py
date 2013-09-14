"""add cover image

Revision ID: 1dc2ee41647e
Revises: None
Create Date: 2013-09-14 21:36:23.630555

"""

# revision identifiers, used by Alembic.
revision = '1dc2ee41647e'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('albums', sa.Column('coverimage', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('albums', 'coverimage')
    ### end Alembic commands ###