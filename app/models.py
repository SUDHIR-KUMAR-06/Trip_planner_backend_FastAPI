from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    picture = Column(String, nullable=True)
    provider = Column(String)
    bio = Column(String)
    gender = Column(String)
    age = Column(Integer)
    location = Column(String)

    #Relationship
    trips = relationship("Trip", back_populates="creator")

class Trip(Base):
    __tablename__ = "trips"
    
    id = Column(Integer, primary_key=True, index=True)
    destination = Column(String, nullable=False)
    budget = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    female_allowed = Column(Boolean, default=False)
    male_count = Column(Integer, default=0)
    female_count = Column(Integer, default=0)
    status = Column(String, default="upcoming")
    itinerary = Column(String)
    creator_id = Column(Integer, ForeignKey("users.id"))
    
    #Relationship
    creator = relationship("User",back_populates="trips")
    