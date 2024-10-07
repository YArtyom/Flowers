from sqlalchemy.orm import Session
from models import Customer, Product, Basket, BasketItem
from schemas import CustomerCreate, BasketItemOut
from auth import get_password_hash
from fastapi import HTTPException, status


def create_customer(db: Session, customer: CustomerCreate):
    hashed_password = get_password_hash(customer.password)
    db_customer = Customer(name=customer.name, mail=customer.mail, password=hashed_password)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


def get_products(db: Session):
    return db.query(Product).all()


# CRUD для корзины
def get_active_basket(db: Session, customer_id: int):
    return db.query(Basket).filter(Basket.customer_id == customer_id, Basket.active_status == True).first()


def create_basket(db: Session, customer_id: int):
    basket = Basket(customer_id=customer_id, price=0, active_status=True)
    db.add(basket)
    db.commit()
    db.refresh(basket)
    return basket


def add_item_to_basket(db: Session, basket: Basket, product_id: int, quantity: int):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    if product.quantity < quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough quantity in stock")
    basket_item = BasketItem(basket_id=basket.id, product_id=product_id, price=product.price, quantity=quantity)
    db.add(basket_item)
    basket.price += product.price * quantity
    db.commit()
    db.refresh(basket)

    return basket_item


def get_basket_items(db: Session, basket_id: int):
    return db.query(BasketItem).filter(BasketItem.basket_id == basket_id).all()


def remove_item_from_basket(db: Session, basket_item_id: int):
    item = db.query(BasketItem).filter(BasketItem.id == basket_item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    basket = item.basket
    basket.price -= item.price * item.quantity

    db.delete(item)
    db.commit()

    return item
