from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import engine, get_db, Base
from .import models

#create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/test-db")
def test_db(db: Session = Depends(get_db)):
    #Test database connection
    users=db.query(models.User).all()
    return {"user_count": len(users)}