import dataclasses

from bezdarsql.base import Base, Column


@dataclasses.dataclass
class Train(Base):
    __tablename__ = 'trains'

    id: str = Column()
    name: str = Column()
    schedule: str = Column()
