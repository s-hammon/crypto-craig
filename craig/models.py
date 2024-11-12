import uuid
from datetime import datetime
from contextlib import contextmanager
from typing import List, Optional

import pandas as pd
from pydantic import BaseModel
from sqlalchemy import (
    REAL,
    String, 
    create_engine, 
    text, 
)
from sqlalchemy.exc import ResourceClosedError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


@contextmanager
def connect_db(url: str):
    if not url:
        raise ValueError("Database URL is empty")

    conn = None
    try:
        conn = create_engine(url, connect_args={"check_same_thread": False}).connect()
        conn.execution_options(isolation_level="AUTOCOMMIT")
        yield conn
    finally:
        if conn:
            conn.close()


class Coin(BaseModel):
    id: int
    name: str
    symbol: str
    slug: str


class Quote(BaseModel):
    price: float
    volume_24h: float
    percent_change_1h: float
    percent_change_24h: float
    market_cap: float


class ListingResponse(BaseModel):
    id: Optional[uuid.UUID] = None
    coin: Coin
    quote: Quote
    circulating_supply: float


class CMCResponse(BaseModel):
    data: List[ListingResponse]
    status: dict

    @classmethod
    def from_json(cls, response: dict):
        return cls(**transform_response(response))


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
            percent_24h=model.quote.percent_change_24h
        )


def transform_response(response: dict):
    return {
        "data": [
            {
                "coin": {
                    "id": resp["id"],
                    "name": resp["name"],
                    "symbol": resp["symbol"],
                    "slug": resp["slug"]
                },
                "quote": {
                    "price": resp["quote"]["USD"]["price"],
                    "volume_24h": resp["quote"]["USD"]["volume_24h"],
                    "percent_change_1h": resp["quote"]["USD"]["percent_change_1h"],
                    "percent_change_24h": resp["quote"]["USD"]["percent_change_24h"],
                    "market_cap": resp["quote"]["USD"]["market_cap"]
                },
                "circulating_supply": resp["circulating_supply"],
            }
            for resp in response["data"]
        ],
        "status": response["status"]
    }


class Database(BaseModel):
    url: str

    def execute(self, query: str) -> pd.DataFrame:
        if not query:
            raise ValueError("Query is empty")

        try:
            sql = text(query)
            with connect_db(self.url) as conn:
                try:
                    df = pd.read_sql(sql, conn)
                    return df
                except ResourceClosedError:
                    return pd.DataFrame()
                except Exception as e:
                    raise e

        except Exception as e:
            raise e