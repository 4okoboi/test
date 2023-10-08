import sqlalchemy
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session, relationship
import sqlalchemy.ext.declarative as dec
from sqlalchemy import ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash

SqlAlchemyBase = dec.declarative_base()
__factory = None


def global_init(connection_string):
    global __factory

    if __factory:
        return

    conn_str = connection_string
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()


class User(SqlAlchemyBase):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    username = sqlalchemy.Column(sqlalchemy.String)
    balance = sqlalchemy.Column(sqlalchemy.Integer)
    frozen_balance = sqlalchemy.Column(sqlalchemy.Integer)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    telegram_id = sqlalchemy.Column(sqlalchemy.BigInteger)
    email = sqlalchemy.Column(sqlalchemy.String)
    role = sqlalchemy.Column(sqlalchemy.String)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if 'password' not in c.name}


class Packet(SqlAlchemyBase):
    __tablename__ = 'packets'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    time = sqlalchemy.Column(sqlalchemy.Integer)
    min_sum = sqlalchemy.Column(sqlalchemy.Integer)
    max_sum = sqlalchemy.Column(sqlalchemy.Integer)
    is_every_day_withdrawal = sqlalchemy.Column(sqlalchemy.Boolean)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Investment(SqlAlchemyBase):
    __tablename__ = 'investments'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey('users.id'))
    packet_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey('packets.id'))
    sum = sqlalchemy.Column(sqlalchemy.Integer)
    day_left = sqlalchemy.Column(sqlalchemy.Integer)
    status = sqlalchemy.Column(sqlalchemy.String)
    dividends = sqlalchemy.Column(sqlalchemy.Integer)

    user = relationship('User')
    packet = relationship('Packet')

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Transaction(SqlAlchemyBase):
    __tablename__ = 'transactions'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey('users.id'))
    summ = sqlalchemy.Column(sqlalchemy.Integer)
    type = sqlalchemy.Column(sqlalchemy.String)
    status = sqlalchemy.Column(sqlalchemy.String)
    payment_data = sqlalchemy.Column(sqlalchemy.Integer)
    time_created = sqlalchemy.Column(sqlalchemy.Integer)
    time_commited = sqlalchemy.Column(sqlalchemy.Integer)
    time_finished = sqlalchemy.Column(sqlalchemy.Integer)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    user = relationship('User')
