"""empty message

Revision ID: b76532ce05f7
Revises: 2f19c194ab29
Create Date: 2024-01-12 16:02:17.329458

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b76532ce05f7'
down_revision = '2f19c194ab29'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('student')
    with op.batch_alter_table('employee', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('employee', schema=None) as batch_op:
        batch_op.drop_column('image')

    op.create_table('student',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('email', sa.VARCHAR(), nullable=False),
    sa.Column('first_name', sa.VARCHAR(length=150), nullable=False),
    sa.Column('last_name', sa.VARCHAR(length=150), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###
