import dataclasses
from typing import List
from bezdarsql.base import Base


@dataclasses.dataclass
class User(Base):
    __tablename__ = 'users'

    id: int
    name: str
    username: str
    password: str
    role: str
    ulga: int
    tickets: str
