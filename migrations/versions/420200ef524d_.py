"""empty message

Revision ID: 420200ef524d
Revises: dda6fa00db7a
Create Date: 2022-06-03 23:25:02.477580

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '420200ef524d'
down_revision = 'dda6fa00db7a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('shows_artist_id_fkey', 'shows', type_='foreignkey')
    op.drop_constraint('shows_venue_id_fkey', 'shows', type_='foreignkey')
    op.drop_column('shows', 'artist_id')
    op.drop_column('shows', 'venue_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shows', sa.Column('venue_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('shows', sa.Column('artist_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('shows_venue_id_fkey', 'shows', 'venues', ['venue_id'], ['id'])
    op.create_foreign_key('shows_artist_id_fkey', 'shows', 'artists', ['artist_id'], ['id'])
    # ### end Alembic commands ###
