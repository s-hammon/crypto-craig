import uuid
from typing import List, Optional

from pydantic import BaseModel

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

