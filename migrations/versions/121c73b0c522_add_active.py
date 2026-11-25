"""Add active

Revision ID: 121c73b0c522
Revises: 8432150e8510
Create Date: 2026-11-25 17:35:39.891239

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '121c73b0c522'
down_revision = '8432150e8510'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table(
        'products',
        recreate='always'
    ) as batch_op:

        batch_op.add_column(
            sa.Column(
                'created_at',
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP")
            )
        )


def downgrade():
    with op.batch_alter_table('products') as batch_op:
        batch_op.drop_column('created_at')
