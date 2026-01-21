from typing import List

from pydantic import BaseModel


class SUserReg(BaseModel):
    id: int
    name: str
    username: str
    password: str
    role: str
    ulga: int


class SUserGet(BaseModel):
    id: int
    name: str
    username: str
    password: str
    role: str
    ulga: int
    tickets: List[int]
