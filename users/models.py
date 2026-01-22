import dataclasses
from typing import Set
from bezdarsql.base import Base, Column


@dataclasses.dataclass
class User(Base):
    __tablename__ = 'users'

    id: int = Column(autoincrement=True)
    name: str = Column()
    username: str = Column()
    password: str = Column()
    role: str = Column()
    ulga: int = Column()
    tickets: str = Column()
