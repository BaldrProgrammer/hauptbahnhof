from typing import List
from bezdarsql.base import Base


class User(Base):
    __tablename__ = 'usres'

    id: int
    name: str
    username: str
    password: str
    role: str
    ulga: int
    tickets: List[int]
