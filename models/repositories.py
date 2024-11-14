import uuid
from datetime import datetime

from sqlalchemy import REAL, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from models.entities import ListingResponse


class Base(DeclarativeBase):
    pass


class Listing(Base):
    __tablename__ = "listings"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    updated_at: Mapped[str] = mapped_column(String(30))
    coin: Mapped[str] = mapped_column(String(30))
    supply: Mapped[float] = mapped_column(REAL)
    price: Mapped[float] = mapped_column(REAL)
    volume_24h: Mapped[float] = mapped_column(REAL)
    percent_1h: Mapped[float] = mapped_column(REAL)
    percent_24h: Mapped[float] = mapped_column(REAL)

    def __repr__(self):
        return f"Listing(id={self.id!r}, coin_id={self.coin!r}, price={self.price!r})"

    def __eq__(self, other):
        return self.id == other.id

    @classmethod
    def from_model(cls, model: ListingResponse):
        if not model.id:
            model.id = uuid.uuid4()

        return cls(
            id=str(model.id),
            updated_at=datetime.now().isoformat(),
            coin=model.coin.symbol,
            supply=model.circulating_supply,
            price=model.quote.price,
            volume_24h=model.quote.volume_24h,
            percent_1h=model.quote.percent_change_1h,
            percent_24h=model.quote.percent_change_24h,
        )
