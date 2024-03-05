"""add content column in post table

Revision ID: aa043c0873d5
Revises: 9b7ef609991b
Create Date: 2024-02-29 15:12:45.679738

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aa043c0873d5'
down_revision: Union[str, None] = '9b7ef609991b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts',sa.Column('content',sa.String(),nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('posts','content')
    pass
