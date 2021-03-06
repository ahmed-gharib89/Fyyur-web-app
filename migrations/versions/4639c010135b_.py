"""empty message

Revision ID: 4639c010135b
Revises: 9e7aecec5be9
Create Date: 2021-01-08 19:14:50.146235

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4639c010135b'
down_revision = '9e7aecec5be9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('seeking_description', sa.String(length=250), nullable=True))
    op.add_column('Venue', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.add_column('Venue', sa.Column('website', sa.String(length=250), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'website')
    op.drop_column('Venue', 'seeking_talent')
    op.drop_column('Venue', 'seeking_description')
    # ### end Alembic commands ###
