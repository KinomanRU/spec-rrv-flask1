"""0002 Add Author's surname

Revision ID: 9506a647f1f5
Revises: d29d28a0b357
Create Date: 2025-03-27 11:19:05.056186

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9506a647f1f5'
down_revision = 'd29d28a0b357'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('authors', schema=None) as batch_op:
        batch_op.add_column(sa.Column('surname', sa.String(length=32), nullable=True))
        batch_op.drop_index('ix_authors_name')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('authors', schema=None) as batch_op:
        batch_op.create_index('ix_authors_name', ['name'], unique=1)
        batch_op.drop_column('surname')

    # ### end Alembic commands ###
