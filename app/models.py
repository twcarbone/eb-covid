import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.ext.declarative as sa_ext_decl
import sqlalchemy.orm as sa_orm
from config import Config

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s_%(referred_column_0_name)s",
    "pk": "pk_%(table_name)s",
}

metadata_obj = sa.MetaData(naming_convention=convention)


def _create_engine(server, database, **kwargs):
    return sa.create_engine(...)


class Base:
    @sa_orm.declared_attr
    def __tablename__(cls):
        return cls.__name__


Engine = _create_engine(server="foo", database="bar")
Session = sa_orm.sessionmaker(bind=Engine)
Metadata = sa.MetaData(naming_convention=convention)
DeclBase = sa_ext_decl.declarative_base(cls=Base, metadata=Metadata)


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

    name = sa.Column(sa.String(Config.DB_SHRT_STRING), nullable=False)


@sa_orm.declarative_mixin
class CreatedOnMixin:
    """
    Mixin class providing the following mapped columns:
     * createdon (defaults to time at creation)
    """

    createdon = sa.Column(sa.DateTime(), server_default=sa.func.now())
