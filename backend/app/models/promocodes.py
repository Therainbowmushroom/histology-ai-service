from sqlalchemy import Column, Integer, String
from app.database import Base

class Promocode(Base):

    __tablename__ = "promocodes"

    id = Column(Integer, primary_key=True)

    code = Column(String, unique=True)

    reward = Column(Integer)

    max_usages = Column(Integer)

    current_usages = Column(Integer, default=0)
