from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    mail = Column(String, unique=True, index=True)
    password = Column(String)
    profile_picture = Column(String)

    baskets = relationship("Basket", back_populates="customer")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    description = Column(String)
    quantity = Column(Integer)
    product_picture = Column(String)


class Basket(Base):
    __tablename__ = "baskets"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(String)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    price = Column(Float)
    active_status = Column(Boolean, default=True)

    customer = relationship("Customer", back_populates="baskets")
    items = relationship("BasketItem", back_populates="basket")


class BasketItem(Base):
    __tablename__ = "basket_items"

    id = Column(Integer, primary_key=True, index=True)
    basket_id = Column(Integer, ForeignKey("baskets.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    price = Column(Float)
    quantity = Column(Integer)

    basket = relationship("Basket", back_populates="items")
    product = relationship("Product")
