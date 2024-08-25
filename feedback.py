from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr, validator, Field
from typing import Annotated, Optional
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging
import re

app = FastAPI()

# Create the tables in the database
models.Base.metadata.create_all(bind=engine)

# Pydantic model for request payload with email validation
class FeedbackRequest(BaseModel):
    feedback: str
    email: Optional[str] = None # Make the email field optional  
    
    # Ensures email is a valid email format
    @validator('email', always=True, pre=True)
    def validate_email(cls, v):
        if v is None or v=="":
            return v
        
        else:
            # Basic regex for email validation
            email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
            if not re.match(email_regex, v):
                raise ValueError("Invalid email address")
            return v

# Dependency to get the session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.post("/feedback")
async def submit_feedback(feedback_request: FeedbackRequest, db: db_dependency):

    try: 
        
        # Create a new feedback record
        new_feedback = models.UserFeedbacks(feedback=feedback_request.feedback, email=feedback_request.email)
        
        # Add to the session and commit to the database
        db.add(new_feedback)
        db.commit()
        db.refresh(new_feedback)

        return {
            "status": "success",
            "message": "Thank you for your feedback!"
        }
    
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your feedback.")
