from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func

from app.database import Base


class Transaction(Base):

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    amount = Column(Integer)

    type = Column(String)

    description = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
