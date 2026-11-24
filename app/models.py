from sqlalchemy import Column, Integer, String
from app.database import Base


class Employee(Base):

    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    surname = Column(String(100), nullable=False, index=True)
    room_number = Column(String(20), nullable=False)
    department = Column(String(100), nullable=False, index=True)
    computer_info = Column(String(255), nullable=False)
