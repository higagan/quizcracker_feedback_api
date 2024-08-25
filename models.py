from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from database import Base

# Define the Feedback model
class UserFeedbacks(Base):
    __tablename__ = 'feedback'

    id = Column(Integer, primary_key=True, index=True)
    feedback = Column(String, index=True)
    email = Column(String, nullable=True)
    
