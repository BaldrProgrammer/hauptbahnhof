from pydantic import BaseModel


class STrain(BaseModel):
    id: str
    name: str
    schedule: list[list[str]]
    model: str
    delay: int
