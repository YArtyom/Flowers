from sqlalchemy import Column, Integer, ForeignKey, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Basket(Base):
    __tablename__ = 'baskets'

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    price = Column(Float, default=0.0)
    active_status = Column(Boolean, default=True)

    customer = relationship("Customer", back_populates="baskets", lazy='selectin')
    items = relationship("BasketItem", back_populates="basket", lazy='selectin')
