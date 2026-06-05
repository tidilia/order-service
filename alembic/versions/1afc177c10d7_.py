"""fix outbox status_kafka and status_notification types (boolean -> text)

Revision ID: 1afc177c10d7
Revises: e204d57d444f
Create Date: 2026-06-05
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1afc177c10d7"
down_revision: Union[str, Sequence[str], None] = "e204d57d444f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # status_kafka: BOOLEAN -> VARCHAR
    op.alter_column(
        "outbox",
        "status_kafka",
        type_=sa.String(),
        existing_type=sa.Boolean(),
        nullable=False,
        server_default=None,
        postgresql_using="""
            CASE
                WHEN status_kafka = true THEN 'SENT'
                ELSE 'PENDING'
            END
        """,
    )

    # status_notification: BOOLEAN -> VARCHAR
    op.alter_column(
        "outbox",
        "status_notification",
        type_=sa.String(),
        existing_type=sa.Boolean(),
        nullable=False,
        server_default=None,
        postgresql_using="""
            CASE
                WHEN status_notification = true THEN 'SENT'
                ELSE 'PENDING'
            END
        """,
    )


def downgrade():
    # VARCHAR -> BOOLEAN (rollback)
    op.alter_column(
        "outbox",
        "status_kafka",
        type_=sa.Boolean(),
        existing_type=sa.String(),
        nullable=False,
        postgresql_using="""
            CASE
                WHEN status_kafka = 'SENT' THEN true
                ELSE false
            END
        """,
    )

    op.alter_column(
        "outbox",
        "status_notification",
        type_=sa.Boolean(),
        existing_type=sa.String(),
        nullable=False,
        postgresql_using="""
            CASE
                WHEN status_notification = 'SENT' THEN true
                ELSE false
            END
        """,
    )
