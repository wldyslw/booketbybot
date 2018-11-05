from sqlalchemy import Column, Integer, String, DateTime, Boolean, create_engine
from sqlalchemy.orm import validates, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Subscriber(Base):
    __tablename__ = 'subscribers'

    id = Column(String, primary_key=True)
    subs_type = Column(String)

    @validates('subs_type')
    def validate_subs_type(self, key, adress):
        assert adress in ['disabled', 'silent', 'normal']
        return adress

    def __repr__(self):
        return f"<Subscriber(id={self.id}, subs_type={self.subs_type})>"

class StatusMessage(Base):
    __tablename__ = 'status_messages'

    timestamp = Column(DateTime, primary_key=True)
    code = Column(String)


def init_session(db_type, db_path):
    connection = f"{db_type}:////{db_path}"
    engine = create_engine(connection, echo=True)
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    return Session()