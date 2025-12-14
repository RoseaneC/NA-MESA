import datetime as dt
from sqlalchemy import Column, DateTime, String, Text

from .db import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, index=True)
    state = Column(String, nullable=False, default="MENU")
    context = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime, default=dt.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow, nullable=False
    )

