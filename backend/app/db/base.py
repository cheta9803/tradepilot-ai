from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.users.models import User
from app.watchlist.models import Watchlist