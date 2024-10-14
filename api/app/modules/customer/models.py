from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    mail = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    baskets = relationship("Basket", back_populates="customer", lazy='selectin')
    orders = relationship("Order", back_populates="customer", lazy='selectin')
