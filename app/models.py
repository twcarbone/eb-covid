import typing as typ

import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.ext.declarative as sa_ext_decl
import sqlalchemy.inspection as sa_inspect
import sqlalchemy.orm as sa_orm

import log
from config import Config

logger = log.logging.getLogger("EBCovid.models")

SHORT_STR = 100
LONG_STR = 500

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s_%(referred_column_0_name)s",
    "pk": "pk_%(table_name)s",
}

Metadata = sa.MetaData(naming_convention=convention)


@sa_ext_decl.as_declarative(metadata=Metadata)
class DeclBase:
    @sa_orm.declared_attr
    def __tablename__(cls):
        return cls.__name__

    @classmethod
    def one_or_create(cls: "DeclBase", ssn: sa_orm.Session, **kwargs) -> "DeclBase":
        """
        Query for *cls* by *kwargs*. If a record is found, return the record. If no
        records are found, attempts to commit a new record with *kwargs* and return the
        new record. Records that violate any constraints are not committed.
        """
        row = ssn.query(cls).filter_by(**kwargs).one_or_none()
        if row is None:
            row = cls(**kwargs)
            ssn.add(row)
            try:
                ssn.commit()
                logger.debug(f"Created {row}")
            except sa_exc.SQLAlchemyError:
                ssn.rollback()
                logger.warning(f"Cannot commit {row}")
        else:
            logger.debug(f"Found {row}")
        return row

    @classmethod
    def pk_column_name(cls: "DeclBase") -> str:
        """
        Return the primary key column name of *cls*.
        """
        return sa_inspect.inspect(cls).primary_key[0].name

    def __repr__(self: "DeclBase") -> str:
        """
        E.x. `<TableName id=1, column='something', anothercolumn='something else'>`
        """
        classname: str = type(self).__name__
        columns: list[str] = self.__table__.columns.keys()
        columns.insert(0, columns.pop(columns.index(type(self).pk_column_name())))  # Primary key appears first
        column_kvs: str = ", ".join([f"{c}={getattr(self, c)!r}" for c in columns])
        return f"<{classname} {column_kvs}>"


Engine_dev = sa.create_engine(url=Config.DB_URI_DEV, pool_pre_ping=True)
Session_dev = sa_orm.sessionmaker(bind=Engine_dev)

Engine_test = sa.create_engine(url=Config.DB_URI_TEST, pool_pre_ping=True)
Session_test = sa_orm.sessionmaker(bind=Engine_dev)

Engine_prod = sa.create_engine(url=Config.DB_URI_PROD, pool_pre_ping=True)
Session_prod = sa_orm.sessionmaker(bind=Engine_dev)

_dbenv_session_map = {"dev": Session_dev, "test": Session_test, "prod": Session_prod}


def ssn_from_dbenv(dbenv: str) -> sa_orm.Session:
    """
    Return an open `Session` based on *dbenv* (dev, test, prod).
    """
    return _dbenv_session_map.get(dbenv, Session_dev)()


@sa_orm.declarative_mixin
class IDMixin:
    """
    Mixin class providing the following mapped columns:
     * id
    """

    id = sa.Column(sa.Integer(), primary_key=True)


@sa_orm.declarative_mixin
class IDNameMixin(IDMixin):
    """
    Mixin class providing the following mapped columns:
     * id
     * name
    """

    name = sa.Column(sa.String(SHORT_STR), nullable=False)


@sa_orm.declarative_mixin
class CreatedOnMixin:
    """
    Mixin class providing the following mapped columns:
     * createdon (defaults to time at creation)
    """

    createdon = sa.Column(sa.DateTime(), server_default=sa.func.now())


#
#


class User(DeclBase, IDMixin, CreatedOnMixin):
    # Table args

    # Columns
    firstname = sa.Column(sa.String(SHORT_STR), nullable=False)
    middlename = sa.Column(sa.String(SHORT_STR))
    lastname = sa.Column(sa.String(SHORT_STR), nullable=False)
    email = sa.Column(sa.String(SHORT_STR), nullable=False, unique=True)

    # Relationships
    _password = sa_orm.relationship("Password", back_populates="_user", uselist=False, cascade="all, delete-orphan")
    _apitoken = sa_orm.relationship("APIToken", back_populates="_user", uselist=False, cascade="all, delete-orphan")


class Password(DeclBase):
    # Table args

    # Columns
    user_id = sa.Column(sa.Integer(), sa.ForeignKey("User.id"), primary_key=True, nullable=False)
    hash = sa.Column(sa.String(128), nullable=False)
    salt = sa.Column(sa.String(5), nullable=False)

    # Relationships
    _user = sa_orm.relationship("User", back_populates="_password")


class APIToken(DeclBase, CreatedOnMixin):
    # Table args

    # Columns
    user_id = sa.Column(sa.Integer(), sa.ForeignKey("User.id"), primary_key=True, nullable=False)
    token = sa.Column(sa.String(32), nullable=False)
    expiration = sa.Column(sa.DateTime(), nullable=False)

    # Relationships
    _user = sa_orm.relationship("User", back_populates="_apitoken")


#
#


class Facility(DeclBase, IDNameMixin):
    # Table args
    __tableargs__ = sa.UniqueConstraint("name")

    # Relationships
    _covidcases = sa_orm.relationship("CovidCase", back_populates="_facility")


class Building(DeclBase, IDNameMixin):
    # Table args
    __tableargs__ = sa.UniqueConstraint("name")

    # Relationships
    _covidcases = sa_orm.relationship("CovidCase", back_populates="_building")


class Department(DeclBase, IDNameMixin):
    # Table args
    __tableargs__ = sa.UniqueConstraint("name")

    # Relationships
    _covidcases = sa_orm.relationship("CovidCase", back_populates="_department")


class CovidCase(DeclBase, IDMixin):
    # Table args

    # Columns
    facility_id = sa.Column(sa.Integer(), sa.ForeignKey("Facility.id"))
    building_id = sa.Column(sa.Integer(), sa.ForeignKey("Building.id"))
    department_id = sa.Column(sa.Integer(), sa.ForeignKey("Department.id"))
    last_work_date = sa.Column(sa.Date())
    test_date = sa.Column(sa.Date())
    post_date = sa.Column(sa.Date())

    # Relationships
    _facility = sa_orm.relationship("Facility", back_populates="_covidcases")
    _building = sa_orm.relationship("Building", back_populates="_covidcases")
    _department = sa_orm.relationship("Department", back_populates="_covidcases")
