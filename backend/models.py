from sqlalchemy import Column, Integer, Float, DateTime
from datetime import datetime, timezone
from .database import Base

class Calculation(Base):
    __tablename__ = "calculations"

    id = Column(Integer, primary_key=True, index=True)
    floor = Column(Integer, nullable=False)
    total_floors = Column(Integer, nullable=False)
    rooms = Column(Integer, nullable=False)
    total_area = Column(Float, nullable=False)
    living_area = Column(Float, nullable=False)
    
    price_per_meter = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
