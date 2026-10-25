"""Cross-database JSON column type."""

from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB

# JSONB для Postgres, JSON для остальных (SQLite в тестах)
JSONType = JSON().with_variant(JSONB(), "postgresql")
