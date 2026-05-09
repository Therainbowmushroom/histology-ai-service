from sqlalchemy import Column, Integer, ForeignKey
from app.database import Base

class PromocodeUsage(Base):

    __tablename__ = "promocode_usages"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    promocode_id = Column(Integer, ForeignKey("promocodes.id"))
