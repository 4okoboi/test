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
    dividends_sum = sqlalchemy.Column(sqlalchemy.Integer)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    telegram_id = sqlalchemy.Column(sqlalchemy.BigInteger)
    total_coins = sqlalchemy.Column(sqlalchemy.Integer)
    email = sqlalchemy.Column(sqlalchemy.String)
    status = sqlalchemy.Column(sqlalchemy.String)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if 'password' not in c.name}


class Token(SqlAlchemyBase):
    __tablename__ = 'tokens'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True, unique=True)
    price = sqlalchemy.Column(sqlalchemy.Integer, unique=True)
    status = sqlalchemy.Column(sqlalchemy.String)
    transaction_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey('transactions.id'))
    holder_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey('users.id'))
    time_bought = sqlalchemy.Column(sqlalchemy.String)
    dividend_sum = sqlalchemy.Column(sqlalchemy.Integer)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    transaction = relationship("Transaction")
    user = relationship('User')


class Transaction(SqlAlchemyBase):
    __tablename__ = 'transactions'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    creator_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey('users.id'))
    summ = sqlalchemy.Column(sqlalchemy.Integer)
    type = sqlalchemy.Column(sqlalchemy.String)
    status = sqlalchemy.Column(sqlalchemy.String)

    user = relationship('User')
