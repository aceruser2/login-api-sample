"""add customer email

Revision ID: [new_revision_id]
Revises: 0477f0365103
Create Date: [timestamp]

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "[new_revision_id]"
down_revision = "0477f0365103"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("customers", sa.Column("email", sa.String(), nullable=True))
    op.create_unique_constraint("uq_customer_email", "customers", ["email"])


def downgrade():
    op.drop_constraint("uq_customer_email", "customers", type_="unique")
    op.drop_column("customers", "email")
