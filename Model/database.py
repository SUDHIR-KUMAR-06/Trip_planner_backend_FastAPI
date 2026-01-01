from datetime import datetime, date
from enum import Enum as PyEnum
from typing import List, Optional

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    Date,
    DateTime,
    Float,
    Text,
    ForeignKey,
    Enum as SAEnum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session

# 1. SQLite database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./tripapp.db"

# 2. Create the database engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# 3. Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Base class for models
Base = declarative_base()


# ----- Enums -----
class TripStatus(PyEnum):
    OPEN = "open"
    CLOSED = "closed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TripRequestStatus(PyEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


# ----- Models -----
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    picture = Column(String(1024), nullable=True)
    provider = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    gender = Column(String(20), nullable=True)
    age = Column(Integer, nullable=True)
    location = Column(String(255), nullable=True)
    interests = Column(Text, nullable=True)  # JSON string or comma-separated list
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    trips = relationship("Trip", back_populates="creator", cascade="all, delete-orphan")
    trip_requests = relationship("TripRequest", back_populates="user", cascade="all, delete-orphan")


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    destination = Column(String(255), nullable=False)
    budget = Column(Float, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    female_allowed = Column(Boolean, default=True)
    male_count = Column(Integer, default=0)
    female_count = Column(Integer, default=0)
    status = Column(SAEnum(TripStatus), default=TripStatus.OPEN)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    itinerary = Column(Text, nullable=True)  # store as JSON string or plain text
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    creator = relationship("User", back_populates="trips")
    requests = relationship("TripRequest", back_populates="trip", cascade="all, delete-orphan")


class TripRequest(Base):
    __tablename__ = "trip_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)
    status = Column(SAEnum(TripRequestStatus), default=TripRequestStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="trip_requests")
    trip = relationship("Trip", back_populates="requests")


# 5. Dependency to get DB session (generator)
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----- CRUD helpers -----
def create_user(db: Session, *, name: str, email: str, **kwargs) -> User:
    user = User(name=name, email=email, **kwargs)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def update_user(db: Session, user_id: int, **kwargs) -> Optional[User]:
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    for k, v in kwargs.items():
        if hasattr(user, k):
            setattr(user, k, v)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True


# Trip CRUD
def create_trip(db: Session, *, destination: str, creator_id: int, **kwargs) -> Trip:
    trip = Trip(destination=destination, creator_id=creator_id, **kwargs)
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


def get_trip(db: Session, trip_id: int) -> Optional[Trip]:
    return db.query(Trip).filter(Trip.id == trip_id).first()


def list_trips(db: Session, skip: int = 0, limit: int = 100) -> List[Trip]:
    return db.query(Trip).offset(skip).limit(limit).all()


def update_trip(db: Session, trip_id: int, **kwargs) -> Optional[Trip]:
    trip = get_trip(db, trip_id)
    if not trip:
        return None
    for k, v in kwargs.items():
        if hasattr(trip, k):
            setattr(trip, k, v)
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


def delete_trip(db: Session, trip_id: int) -> bool:
    trip = get_trip(db, trip_id)
    if not trip:
        return False
    db.delete(trip)
    db.commit()
    return True


# TripRequest CRUD
def create_trip_request(db: Session, user_id: int, trip_id: int) -> TripRequest:
    tr = TripRequest(user_id=user_id, trip_id=trip_id)
    db.add(tr)
    db.commit()
    db.refresh(tr)
    return tr


def get_trip_request(db: Session, request_id: int) -> Optional[TripRequest]:
    return db.query(TripRequest).filter(TripRequest.id == request_id).first()


def list_requests_for_trip(db: Session, trip_id: int) -> List[TripRequest]:
    return db.query(TripRequest).filter(TripRequest.trip_id == trip_id).all()


def list_requests_for_user(db: Session, user_id: int) -> List[TripRequest]:
    return db.query(TripRequest).filter(TripRequest.user_id == user_id).all()


def update_trip_request_status(db: Session, request_id: int, status: TripRequestStatus) -> Optional[TripRequest]:
    tr = get_trip_request(db, request_id)
    if not tr:
        return None
    tr.status = status
    db.add(tr)
    db.commit()
    db.refresh(tr)
    return tr


# Create tables if they do not exist
Base.metadata.create_all(bind=engine)