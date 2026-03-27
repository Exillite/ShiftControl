from sqlalchemy import BigInteger, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from core.db.base import Base, TimestampMixin


class GroupAdmin(Base, TimestampMixin):
    __tablename__ = "group_admins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id")
    )

    tg_user_id: Mapped[int] = mapped_column(BigInteger)