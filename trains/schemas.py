from pydantic import BaseModel


class STrain(BaseModel):
    id: str
    name: str
    schedule: str
    model: str
