"""add status_notif to outbox

Revision ID: e204d57d444f
Revises: 89fd5874f340
Create Date: 2026-06-05 19:27:16.822123

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e204d57d444f"
down_revision: Union[str, Sequence[str], None] = "89fd5874f340"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "outbox",
        sa.Column(
            "status_kafka",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    op.add_column(
        "outbox",
        sa.Column(
            "status_notification",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    # переносим старые данные
    op.execute("""
        UPDATE outbox
        SET status_kafka =
            CASE
                WHEN status = 'SENT' THEN true
                ELSE false
            END
    """)

    op.drop_column("outbox", "status")


def downgrade():
    op.add_column(
        "outbox",
        sa.Column(
            "status",
            sa.String(),
            nullable=False,
            server_default="PENDING",
        ),
    )

    op.execute("""
        UPDATE outbox
        SET status =
            CASE
                WHEN status_kafka = true THEN 'SENT'
                ELSE 'PENDING'
            END
    """)

    op.drop_column("outbox", "status_notification")
    op.drop_column("outbox", "status_kafka")
