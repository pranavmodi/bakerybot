"""Revision ID: e7b36440521c
Revises: c527b48944a0
Create Date: 2024-03-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7b36440521c'
down_revision: Union[str, None] = 'c527b48944a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add summary column to orders table
    op.add_column('orders', sa.Column('summary', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove summary column from orders table
    op.drop_column('orders', 'summary')
