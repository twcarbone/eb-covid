import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.ext.declarative as sa_ext_decl
import sqlalchemy.orm as sa_orm
from config import Config

SHORT_STR = 100
LONG_STR = 500

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s_%(referred_column_0_name)s",
    "pk": "pk_%(table_name)s",
}

metadata_obj = sa.MetaData(naming_convention=convention)


class BaseModel:
    @sa_orm.declared_attr
    def __tablename__(cls):
        return cls.__name__


Engine_dev = sa.create_engine(url=Config.DB_URI_DEV, pool_pre_ping=True)
Session_dev = sa_orm.sessionmaker(bind=Engine_dev)

Engine_test = sa.create_engine(url=Config.DB_URI_TEST, pool_pre_ping=True)
Session_test = sa_orm.sessionmaker(bind=Engine_dev)

Engine_prod = sa.create_engine(url=Config.DB_URI_PROD, pool_pre_ping=True)
Session_prod = sa_orm.sessionmaker(bind=Engine_dev)

Metadata = sa.MetaData(naming_convention=convention)
DeclBase = sa_ext_decl.declarative_base(cls=BaseModel, metadata=Metadata)


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
    _covidcase = sa_orm.relationship("CovidCase", back_populates="_facility")


class Building(DeclBase, IDNameMixin):
    # Table args
    __tableargs__ = sa.UniqueConstraint("name")

    # Relationships
    _covidcase = sa_orm.relationship("CovidCase", back_populates="_building")


class Department(DeclBase, IDNameMixin):
    # Table args
    __tableargs__ = sa.UniqueConstraint("name")

    # Relationships
    _covidcase = sa_orm.relationship("CovidCase", back_populates="_department")


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
    _facility = sa_orm.relationship("Facility", back_populates="_covidcase")
    _building = sa_orm.relationship("Building", back_populates="_covidcase")
    _department = sa_orm.relationship("Department", back_populates="_covidcase")
