from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func

from app.database import Base


class Prediction(Base):

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    original_filename = Column(String)
    file_path = Column(String)
    result = Column(String)

    confidence = Column(Float)

    status = Column(String)
    error_message = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
