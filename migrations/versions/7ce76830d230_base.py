"""Base

Revision ID: 7ce76830d230
Revises: 
Create Date: 2023-06-24 11:00:09.506618

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "7ce76830d230"
down_revision = None
branch_labels = None
depends_on = None


def _upgrade():
    op.create_table(
        "Building",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_Building")),
    )

    op.create_table(
        "Department",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_Department")),
    )

    op.create_table(
        "Facility",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_Facility")),
    )

    op.create_table(
        "User",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("firstname", sa.String(length=100), nullable=False),
        sa.Column("middlename", sa.String(length=100), nullable=True),
        sa.Column("lastname", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("createdon", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_User")),
        sa.UniqueConstraint("email", name=op.f("uq_User_email")),
    )

    op.create_table(
        "APIToken",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(length=32), nullable=False),
        sa.Column("expiration", sa.DateTime(), nullable=False),
        sa.Column("createdon", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["User.id"],
            name=op.f("fk_APIToken_user_id_User_id"),
        ),
        sa.PrimaryKeyConstraint("user_id", name=op.f("pk_APIToken")),
    )

    op.create_table(
        "CovidCase",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("facility_id", sa.Integer(), nullable=True),
        sa.Column("building_id", sa.Integer(), nullable=True),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.Column("last_work_date", sa.Date(), nullable=True),
        sa.Column("test_date", sa.Date(), nullable=True),
        sa.Column("post_date", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["building_id"],
            ["Building.id"],
            name=op.f("fk_CovidCase_building_id_Building_id"),
        ),
        sa.ForeignKeyConstraint(
            ["department_id"],
            ["Department.id"],
            name=op.f("fk_CovidCase_department_id_Department_id"),
        ),
        sa.ForeignKeyConstraint(
            ["facility_id"],
            ["Facility.id"],
            name=op.f("fk_CovidCase_facility_id_Facility_id"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_CovidCase")),
    )

    op.create_table(
        "Password",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("hash", sa.String(length=128), nullable=False),
        sa.Column("salt", sa.String(length=5), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["User.id"],
            name=op.f("fk_Password_user_id_User_id"),
        ),
        sa.PrimaryKeyConstraint("user_id", name=op.f("pk_Password")),
    )


def _downgrade():
    op.drop_table("Password")
    op.drop_table("CovidCase")
    op.drop_table("APIToken")
    op.drop_table("User")
    op.drop_table("Facility")
    op.drop_table("Department")
    op.drop_table("Building")


def upgrade(engine_name: str) -> None:
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name: str) -> None:
    globals()["downgrade_%s" % engine_name]()


def upgrade_dev() -> None:
    _upgrade()


def downgrade_dev() -> None:
    _downgrade()


def upgrade_test() -> None:
    _upgrade()


def downgrade_test() -> None:
    _downgrade()


def upgrade_prod() -> None:
    _upgrade()


def downgrade_prod() -> None:
    _downgrade()
