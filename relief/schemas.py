from pydantic import BaseModel


class SReliefAdd(BaseModel):
    title: str
    description: str
    discount: int


class SReliefGet(BaseModel):
    id: int
    title: str
    description: str
    discount: int
