from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.core.database import Base

class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    vehicle_type = Column(String, nullable=False)
    distance_km = Column(Float, nullable=False)
    emission_kg = Column(Float, nullable=False)
