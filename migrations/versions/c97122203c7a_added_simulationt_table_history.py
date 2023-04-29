"""Added simulationt table history

Revision ID: c97122203c7a
Revises: 30d6d4ce2c26
Create Date: 2023-04-29 14:04:01.254572

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c97122203c7a'
down_revision = '30d6d4ce2c26'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('simulation_history_data',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('fname', sa.String(length=64), nullable=True),
    sa.Column('run_date', sa.DateTime(), nullable=True),
    sa.Column('results', sa.LargeBinary(), nullable=True),
    sa.Column('sim_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['sim_id'], ['open_foam_sim_data.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('simulation_history_data', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_simulation_history_data_id'), ['id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('simulation_history_data', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_simulation_history_data_id'))

    op.drop_table('simulation_history_data')
    # ### end Alembic commands ###
