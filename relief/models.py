import dataclasses
from bezdarsql.base import Base, Column


@dataclasses.dataclass
class Relief(Base):
    __tablename__ = 'reliefs'

    id: int = Column(autoincrement=True)
    title: str = Column()
    description: str = Column()
    discount: int = Column()
