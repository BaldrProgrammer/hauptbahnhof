from pydantic import BaseModel


class SUserReg(BaseModel):
    id: int
    name: str
    username: str
    password: str
    role: str
    ulga: int
