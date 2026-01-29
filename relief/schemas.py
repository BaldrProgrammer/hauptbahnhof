from pydantic import BaseModel


class SReliefAdd(BaseModel):
    name: str
    username: str
    description: str
    discount: int


class SReliefGet(BaseModel):
    id: int
    name: str
    username: str
    description: str
    discount: int
