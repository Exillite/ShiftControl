from datetime import datetime, date
from sqlalchemy import BigInteger, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.db.base import Base, TimestampMixin


class Shift(Base, TimestampMixin):
    __tablename__ = "shifts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    tg_chat_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    tg_message_id: Mapped[int] = mapped_column(BigInteger, nullable=True)

    group_id: Mapped[int] = mapped_column(Integer, nullable=True)

    message_send_at: Mapped[datetime] = mapped_column(DateTime)

    status: Mapped[str] = mapped_column(String(50))
    reason: Mapped[str | None] = mapped_column(String(255))

    shift_date: Mapped[date] = mapped_column(Date)

    employee_id: Mapped[int | None] = mapped_column(
        ForeignKey("employees.id"),
        nullable=True
    )

    # связь
    employee = relationship("Employee", back_populates="shifts")
