from app.repository.base import BaseRepository
from app.user.models import User


class UserRepository(BaseRepository):
    model = User
