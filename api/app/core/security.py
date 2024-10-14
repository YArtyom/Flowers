from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.modules.customer.models import Customer
from sqlalchemy.future import select
from fastapi import Form

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="customers/token")

class OAuth2PasswordRequestFormName:
    def __init__(
        self,
        name: str = Form(...),
        password: str = Form(...),
        scope: str = Form(""),
        grant_type: str = Form(None),
        client_id: str = Form(None),
        client_secret: str = Form(None),
    ):
        self.name = name
        self.password = password
        self.scopes = scope.split()
        self.grant_type = grant_type
        self.client_id = client_id
        self.client_secret = client_secret
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def authenticate_customer_by_name(name: str, password: str, db: AsyncSession):
    result = await db.execute(select(Customer).where(Customer.name == name))
    customer = result.scalars().first()
    if not customer or not verify_password(password, customer.hashed_password):
        return None
    return customer


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_customer(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        name: str = payload.get("sub")
        if name is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    result = await db.execute(select(Customer).where(Customer.name == name))
    customer = result.scalars().first()
    if customer is None:
        raise credentials_exception
    return customer


async def authenticate_customer(mail: str, password: str, db: AsyncSession):
    result = await db.execute(select(Customer).where(Customer.mail == mail))
    customer = result.scalars().first()
    if not customer or not verify_password(password, customer.hashed_password):
        return None
    return customer
