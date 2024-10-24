"""empty message

Revision ID: c23431fac102
Revises: 9a22c6c491d1
Create Date: 2024-10-22 21:17:57.843336

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c23431fac102'
down_revision: Union[str, None] = '9a22c6c491d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'profile_picture')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('profile_picture', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###