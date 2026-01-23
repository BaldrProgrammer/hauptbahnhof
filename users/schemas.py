from pydantic import BaseModel


class SUserReg(BaseModel):
    name: str
    username: str
    password: str
    role: str
    ulga: int


class SUserLog(BaseModel):
    username: str
    password: str


class SUserGet(BaseModel):
    id: int
    name: str
    username: str
    password: str
    role: str
    ulga: int
    tickets: str
