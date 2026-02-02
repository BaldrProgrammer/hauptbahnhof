from pydantic import BaseModel


class SStation(BaseModel):
    id: str
    title: str
    city: str
    region: str
    country: str
    address: str
    coordinates: str
    international_codes: str
