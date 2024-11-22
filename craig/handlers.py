from datetime import datetime
from functools import lru_cache
from typing import Sequence, Tuple

from sqlalchemy import Row, func, select
from sqlalchemy.orm import Session

from models.repositories import Listing


@lru_cache(maxsize=128)
def get_coin_history(
    session: Session, coin: str, rng: datetime
) -> Sequence[Row[Tuple[Listing]]]:
    if not coin:
        raise ValueError("Coin is empty")

    with session:
        stmt = (
            select(Listing)
            .where(Listing.coin.is_(coin))
            .where(Listing.updated_at > rng)
        )
        result = session.execute(stmt).all()

    return result


@lru_cache(maxsize=128)
def get_listing_by_coin(session: Session, coin: str) -> Listing | None:
    if not coin:
        raise ValueError("Coin is empty")

    with session:
        stmt = (
            select(Listing)
            .where(Listing.coin.is_(coin))
            .order_by(Listing.updated_at.desc())
            .limit(1)
        )
        result = session.scalar(stmt)

    return result


@lru_cache(maxsize=128)
def get_select_listings(session: Session) -> Sequence[Row[Tuple[Listing]]]:
    coins = ["BTC", "ETH", "LINK", "AAVE", "DOGE"]
    with session:
        subq = (
            select(Listing.coin, func.max(Listing.updated_at).label("max_updated_at"))
            .where(Listing.coin.in_(coins))
            .group_by(Listing.coin)
            .subquery()
        )

        stmt = select(Listing).join(
            subq,
            (Listing.coin == subq.c.coin)
            & (Listing.updated_at == subq.c.max_updated_at),
        )

        result = session.execute(stmt).all()

    return result
