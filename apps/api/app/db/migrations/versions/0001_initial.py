"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-01-01
"""

from alembic import op
from app.models import Base

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # The first revision materialises the complete model metadata.
    # Later revisions should use explicit op.create_table / op.add_column calls.
    Base.metadata.create_all(bind=op.get_bind())

    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_jobs_search_document
        ON jobs USING GIN (
            to_tsvector('english'::regconfig,
                coalesce(title, '') || ' ' ||
                coalesce(description, '')
            )
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_jobs_title_trgm ON jobs USING GIN (title gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_companies_name_trgm ON companies USING GIN (name gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_jobs_city_trgm ON jobs USING GIN (city gin_trgm_ops)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_jobs_city_trgm")
    op.execute("DROP INDEX IF EXISTS ix_companies_name_trgm")
    op.execute("DROP INDEX IF EXISTS ix_jobs_title_trgm")
    op.execute("DROP INDEX IF EXISTS ix_jobs_search_document")
    Base.metadata.drop_all(bind=op.get_bind())
