"""empty message

Revision ID: 9ff6fae469e3
Revises: 8ba818f18ca7
Create Date: 2026-06-04 19:30:09.546773

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9ff6fae469e3"
down_revision: Union[str, Sequence[str], None] = "8ba818f18ca7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        UPDATE outbox
        SET event_type = 'order.created'
        WHERE event_type = 'ORDER.CREATED'
    """)

    op.execute("""
        UPDATE outbox
        SET event_type = 'order.paid'
        WHERE event_type = 'ORDER.PAID'
    """)
