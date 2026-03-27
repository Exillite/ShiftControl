from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.db.base import Base, TimestampMixin


class Object(Base, TimestampMixin):
    __tablename__ = "objects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))

    groups = relationship("Group", back_populates="object")
