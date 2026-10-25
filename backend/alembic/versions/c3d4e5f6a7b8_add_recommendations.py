"""add recommendations

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-10-25 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "credit_products",
        sa.Column("description", sa.Text(), nullable=True),
    )
    op.add_column(
        "credit_products",
        sa.Column(
            "supported_purposes",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
    )
    op.add_column(
        "credit_products",
        sa.Column(
            "min_business_age_months",
            sa.Integer(),
            nullable=True,
        ),
    )
    op.add_column(
        "credit_products",
        sa.Column(
            "requires_collateral",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )

    op.create_table(
        "recommendations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "requested_amount",
            sa.Numeric(precision=15, scale=2),
            nullable=False,
        ),
        sa.Column("term_months", sa.Integer(), nullable=False),
        sa.Column("purpose", sa.String(length=100), nullable=False),
        sa.Column(
            "monthly_revenue",
            sa.Numeric(precision=15, scale=2),
            nullable=True,
        ),
        sa.Column("business_age_months", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_recommendations_id"),
        "recommendations",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_recommendations_user_id"),
        "recommendations",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "recommendation_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("recommendation_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column(
            "match_score",
            sa.Numeric(precision=5, scale=2),
            nullable=False,
        ),
        sa.Column(
            "estimated_monthly_payment",
            sa.Numeric(precision=15, scale=2),
            nullable=True,
        ),
        sa.Column(
            "reasons",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["recommendation_id"],
            ["recommendations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["credit_products.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_recommendation_items_id"),
        "recommendation_items",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_recommendation_items_recommendation_id"),
        "recommendation_items",
        ["recommendation_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_recommendation_items_product_id"),
        "recommendation_items",
        ["product_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_recommendation_items_product_id"),
        table_name="recommendation_items",
    )
    op.drop_index(
        op.f("ix_recommendation_items_recommendation_id"),
        table_name="recommendation_items",
    )
    op.drop_index(
        op.f("ix_recommendation_items_id"),
        table_name="recommendation_items",
    )
    op.drop_table("recommendation_items")

    op.drop_index(
        op.f("ix_recommendations_user_id"),
        table_name="recommendations",
    )
    op.drop_index(
        op.f("ix_recommendations_id"),
        table_name="recommendations",
    )
    op.drop_table("recommendations")

    op.drop_column("credit_products", "requires_collateral")
    op.drop_column("credit_products", "min_business_age_months")
    op.drop_column("credit_products", "supported_purposes")
    op.drop_column("credit_products", "description")
