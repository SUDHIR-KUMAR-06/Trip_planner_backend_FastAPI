from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. SQLite database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./tripapp.db"

# 2. Create the database engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# 3. Session factory
SessionLocal= sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Base class for models
Base = declarative_base()

# 5. Dependency to get DB session
def get_db():   
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()