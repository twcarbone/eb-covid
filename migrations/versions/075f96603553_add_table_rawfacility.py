"""Add table RawFacility

Revision ID: 075f96603553
Revises: 7ce76830d230
Create Date: 2023-07-09 20:49:34.737427

"""
import itertools

import sqlalchemy as sa
from alembic import op

import app.models as db

# revision identifiers, used by Alembic.
revision = "075f96603553"
down_revision = "7ce76830d230"
branch_labels = None
depends_on = None


def _create_rawfacility() -> None:
    op.create_table(
        "RawFacility",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("facility_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["facility_id"], ["Facility.id"], name=op.f("fk_RawFacility_facility_id_Facility_id")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_RawFacility")),
    )


def _drop_rawfacility() -> None:
    op.drop_table("RawFacility")


def _insert_facility() -> None:
    op.execute(
        sa.insert(db.Facility).values(
            [
                {"id": 1, "name": "Bangor"},
                {"id": 2, "name": "Cape Canaveral"},
                {"id": 3, "name": "Eagle Park"},
                {"id": 4, "name": "Electric Boat Kesselring Site Operation"},
                {"id": 5, "name": "Fitchburg"},
                {"id": 6, "name": "Groton"},
                {"id": 7, "name": "Groton Airport"},
                {"id": 8, "name": "Groton Subase"},
                {"id": 9, "name": "HSI"},
                {"id": 10, "name": "Kentucky"},
                {"id": 11, "name": "King's Bay"},
                {"id": 12, "name": "King's Highway"},
                {"id": 13, "name": "Long Hill Rd"},
                {"id": 14, "name": "New London"},
                {"id": 15, "name": "Newport Engineering Office"},
                {"id": 16, "name": "Newport News"},
                {"id": 17, "name": "Norfolk Naval Shipyard"},
                {"id": 18, "name": "Pennsylvania"},
                {"id": 19, "name": "Philadelphia"},
                {"id": 20, "name": "Portsmouth Naval Shipyard"},
                {"id": 21, "name": "Puget Sound"},
                {"id": 22, "name": "Quonset Point"},
                {"id": 23, "name": "Shaw's Cove"},
                {"id": 24, "name": "South Carolina (Goose Creek)"},
                {"id": 25, "name": "Washington Engineering Office (WEO)"},
            ]
        )
    )


def _delete_facility() -> None:
    op.execute(sa.delete(db.Facility))


def _insert_rawfacility() -> None:
    id_ = itertools.count(start=1)
    op.execute(
        sa.insert(db.RawFacility).values(
            [
                {"id": next(id_), "name": "Bangor", "facility_id": 1},
                {"id": next(id_), "name": "Bangor facility", "facility_id": 1},
                {"id": next(id_), "name": "Cape Canaveral", "facility_id": 2},
                {"id": next(id_), "name": "Cape Canaveral facility", "facility_id": 2},
                {"id": next(id_), "name": "Eagle Park facility", "facility_id": 3},
                {"id": next(id_), "name": "Electric Boat Kesselring Site Operation (EB", "facility_id": 4},
                {"id": next(id_), "name": "Fitchburg", "facility_id": 5},
                {"id": next(id_), "name": "Groton", "facility_id": 6},
                {"id": next(id_), "name": "Groton Airport (EB pilot)", "facility_id": 7},
                {"id": next(id_), "name": "Groton facility", "facility_id": 6},
                {"id": next(id_), "name": "Groton Subase", "facility_id": 8},
                {"id": next(id_), "name": "Groton Sub Base", "facility_id": 8},
                {"id": next(id_), "name": "HSI", "facility_id": 9},
                {"id": next(id_), "name": "HSI facility (Hawaii)", "facility_id": 9},
                {"id": next(id_), "name": "Huntington Ingalls Shipyard (HIS)", "facility_id": 16},
                {"id": next(id_), "name": "Kentucky facility", "facility_id": 10},
                {"id": next(id_), "name": "King's Bay facility", "facility_id": 11},
                {"id": next(id_), "name": "King's Highway facility", "facility_id": 12},
                {"id": next(id_), "name": "Kings Highway facility", "facility_id": 12},
                {"id": next(id_), "name": "Long Hill Rd", "facility_id": 13},
                {"id": next(id_), "name": "New London facility", "facility_id": 14},
                {"id": next(id_), "name": "Newport Engineering Office", "facility_id": 15},
                {"id": next(id_), "name": "Newport Engineering Office (NEO)", "facility_id": 15},
                {"id": next(id_), "name": "Newport News facility", "facility_id": 16},
                {"id": next(id_), "name": "Newport News Shipbuilding (NNS) facility", "facility_id": 16},
                {"id": next(id_), "name": "Newport News Shipyard", "facility_id": 16},
                {"id": next(id_), "name": "Newport News Shipyard (NNS)", "facility_id": 16},
                {"id": next(id_), "name": "Norfolk Naval Shipyard", "facility_id": 17},
                {"id": next(id_), "name": "Pennsylvania facility", "facility_id": 18},
                {"id": next(id_), "name": "Philadelphia", "facility_id": 19},
                {"id": next(id_), "name": "Philadelphia facility", "facility_id": 19},
                {"id": next(id_), "name": "Portsmouth Naval Shipyard", "facility_id": 20},
                {"id": next(id_), "name": "Puget Sound facility", "facility_id": 21},
                {"id": next(id_), "name": "Quonset Point facility", "facility_id": 22},
                {"id": next(id_), "name": "Quonset Point Facility", "facility_id": 22},
                {"id": next(id_), "name": "Shaw's Cove", "facility_id": 23},
                {"id": next(id_), "name": "Shaw's Cove facility", "facility_id": 23},
                {"id": next(id_), "name": "South Carolina", "facility_id": 24},
                {"id": next(id_), "name": "South Carolina (Goose Creek) facility", "facility_id": 24},
                {"id": next(id_), "name": "Sub Base", "facility_id": 8},
                {"id": next(id_), "name": "Washington Engineering Office (WEO)", "facility_id": 25},
                {"id": next(id_), "name": "Washington Engineering Office (WEO) facility", "facility_id": 25},
            ]
        )
    )


def _upgrade() -> None:
    _create_rawfacility()
    _insert_facility()
    _insert_rawfacility()


def _downgrade() -> None:
    _drop_rawfacility()
    _delete_facility()


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
