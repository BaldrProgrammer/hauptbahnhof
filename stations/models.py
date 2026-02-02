import dataclasses

from bezdarsql.base import Base, Column


@dataclasses.dataclass
class Station(Base):
    __tablename__ = 'stations'

    id: int = Column()
    title: str = Column()
    city: str = Column()
    region: str = Column()
    country: str = Column()
    address: str = Column()
    coordinates: str = Column()
    international_codes: str = Column()
