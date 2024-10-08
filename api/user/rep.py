from Base import BaseRepository
from models import User


class UserRepository(BaseRepository):
    model = User
