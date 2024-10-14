from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base

class BasketItem(Base):
    __tablename__ = 'basket_items'

    id = Column(Integer, primary_key=True, index=True)
    basket_id = Column(Integer, ForeignKey('baskets.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    price = Column(Float)
    quantity = Column(Integer)

    basket = relationship("Basket", back_populates="items", lazy='selectin')
    product = relationship("Product", back_populates="basket_items", lazy='selectin')
