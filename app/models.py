from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, String, Text, Numeric, ForeignKey, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int | None] = mapped_column(BigInteger, unique=True, index=True, nullable=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    state: Mapped[str] = mapped_column(String(64), default='START')

    paid: Mapped[bool] = mapped_column(Boolean, default=False)
    access_active: Mapped[bool] = mapped_column(Boolean, default=False)
    license_key: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    license_expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    mt5_account_number: Mapped[str | None] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Payment(Base):
    __tablename__ = 'payments'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_code: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), index=True)
    telegram_username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    plan: Mapped[str] = mapped_column(String(50))
    amount_usd: Mapped[float] = mapped_column(Numeric(10, 2))
    network: Mapped[str] = mapped_column(String(50))
    wallet_address: Mapped[str] = mapped_column(Text)
    tx_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    proof_file_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default='PENDING') # PENDING, APPROVED, REJECTED
    user_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
