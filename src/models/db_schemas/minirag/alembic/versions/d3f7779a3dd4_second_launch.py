"""second launch

Revision ID: d3f7779a3dd4
Revises: 70e67c558e02
Create Date: 2026-09-02 22:19:16.131438

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3f7779a3dd4'
down_revision: Union[str, Sequence[str], None] = '70e67c558e02'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
