"""Create BookCrossing schema.

Revision ID: 0001
Revises:
Create Date: 2026-09-21
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


book_condition = sa.Enum("new", "good", "worn", name="bookcondition")
entry_status = sa.Enum("available", "reserved", "unavailable", name="entrystatus")
exchange_status = sa.Enum(
    "pending", "accepted", "rejected", "cancelled", name="exchangestatus"
)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_username", "users", ["username"])

    op.create_table(
        "authors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("biography", sa.String(), nullable=True),
    )
    op.create_index("ix_authors_name", "authors", ["name"])

    op.create_table(
        "books",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("isbn", sa.String(length=20), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("published_year", sa.Integer(), nullable=True),
        sa.Column("cover_url", sa.String(length=1000), nullable=True),
        sa.Column("source_url", sa.String(length=1000), nullable=True, unique=True),
    )
    op.create_index("ix_books_title", "books", ["title"])
    op.create_index("ix_books_isbn", "books", ["isbn"])

    op.create_table(
        "book_authors",
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["author_id"], ["authors.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("book_id", "author_id"),
    )

    op.create_table(
        "library_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("condition", book_condition, nullable=False),
        sa.Column("status", entry_status, nullable=False),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("added_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"]),
    )
    op.create_index("ix_library_entries_owner_id", "library_entries", ["owner_id"])
    op.create_index("ix_library_entries_book_id", "library_entries", ["book_id"])

    op.create_table(
        "exchange_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("requester_id", sa.Integer(), nullable=False),
        sa.Column("requested_entry_id", sa.Integer(), nullable=False),
        sa.Column("offered_entry_id", sa.Integer(), nullable=True),
        sa.Column("status", exchange_status, nullable=False),
        sa.Column("message", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["requester_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["requested_entry_id"], ["library_entries.id"]),
        sa.ForeignKeyConstraint(["offered_entry_id"], ["library_entries.id"]),
    )
    op.create_index(
        "ix_exchange_requests_requester_id", "exchange_requests", ["requester_id"]
    )
    op.create_index(
        "ix_exchange_requests_requested_entry_id",
        "exchange_requests",
        ["requested_entry_id"],
    )
    op.create_index(
        "ix_exchange_requests_offered_entry_id",
        "exchange_requests",
        ["offered_entry_id"],
    )


def downgrade() -> None:
    op.drop_table("exchange_requests")
    op.drop_table("library_entries")
    op.drop_table("book_authors")
    op.drop_table("books")
    op.drop_table("authors")
    op.drop_table("users")
    exchange_status.drop(op.get_bind(), checkfirst=True)
    entry_status.drop(op.get_bind(), checkfirst=True)
    book_condition.drop(op.get_bind(), checkfirst=True)
