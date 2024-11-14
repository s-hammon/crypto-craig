import unittest
import uuid

from models.entities import (
    CMCResponse,
    Coin, 
    ListingResponse, 
    Quote, 
)
from models.repositories import Listing


class TestListing(unittest.TestCase):
    def test_from_model(self):
        coin = Coin(id=1, name="Bitcoin", symbol="BTC", slug="bitcoin")
        quote = Quote(
            price=10000.0, 
            volume_24h=100000.0, 
            percent_change_1h=0.0, 
            percent_change_24h=0.0,
            market_cap=1000000.0
        )

        id = uuid.uuid4()
        want = Listing(
            id=str(id),
            updated_at="2021-01-01T00:00:00", 
            coin="BTC", 
            supply=1000000.0, 
            price=10000.0, 
            volume_24h=100000.0, 
            percent_1h=0.0, 
            percent_24h=0.0
        )

        model = ListingResponse(id=id, coin=coin, quote=quote, circulating_supply=1000000.0)
        got = Listing.from_model(model)

        self.assertEqual(got, want)


class TestCMCResponse(unittest.TestCase):
    def test_transform_response(self):
        json_data = {
            "data": [
                {
                    "id": 1,
                    "name": "Bitcoin",
                    "symbol": "BTC",
                    "slug": "bitcoin",
                    "cmc_rank": 5,
                    "num_market_pairs": 500,
                    "circulating_supply": 16950100,
                    "total_supply": 16950100,
                    "max_supply": 21000000,
                    "last_updated": "2018-06-02T22:51:28.209Z",
                    "date_added": "2013-04-28T00:00:00.000Z",
                    "tags": [
                        "mineable"
                    ],
                    "quote": {
                        "USD": {
                            "price": 9283.92,
                            "volume_24h": 7155680000,
                            "volume_change_24h": -0.152774,
                            "percent_change_1h": -0.152774,
                            "percent_change_24h": 0.518894,
                            "percent_change_7d": 0.986573,
                            "market_cap": 852164659250.2758,
                            "market_cap_dominance": 51,
                            "fully_diluted_market_cap": 952835089431.14,
                            "last_updated": "2018-08-09T22:53:32.000Z"
                        },
                        "BTC": {
                            "price": 1,
                            "volume_24h": 772012,
                            "volume_change_24h": 0,
                            "percent_change_1h": 0,
                            "percent_change_24h": 0,
                            "percent_change_7d": 0,
                            "market_cap": 17024600,
                            "market_cap_dominance": 12,
                            "fully_diluted_market_cap": 952835089431.14,
                            "last_updated": "2018-08-09T22:53:32.000Z"
                        }
                    }
                },
                {
                    "id": 1027,
                    "name": "Ethereum",
                    "symbol": "ETH",
                    "slug": "ethereum",
                    "num_market_pairs": 6360,
                    "circulating_supply": 16950100,
                    "total_supply": 16950100,
                    "max_supply": 21000000,
                    "last_updated": "2018-06-02T22:51:28.209Z",
                    "date_added": "2013-04-28T00:00:00.000Z",
                    "tags": [
                        "mineable"
                    ],
                    "quote": {
                        "USD": {
                            "price": 1283.92,
                            "volume_24h": 7155680000,
                            "volume_change_24h": -0.152774,
                            "percent_change_1h": -0.152774,
                            "percent_change_24h": 0.518894,
                            "percent_change_7d": 0.986573,
                            "market_cap": 158055024432,
                            "market_cap_dominance": 51,
                            "fully_diluted_market_cap": 952835089431.14,
                            "last_updated": "2018-08-09T22:53:32.000Z"
                        },
                        "ETH": {
                            "price": 1,
                            "volume_24h": 772012,
                            "volume_change_24h": -0.152774,
                            "percent_change_1h": 0,
                            "percent_change_24h": 0,
                            "percent_change_7d": 0,
                            "market_cap": 17024600,
                            "market_cap_dominance": 12,
                            "fully_diluted_market_cap": 952835089431.14,
                            "last_updated": "2018-08-09T22:53:32.000Z"
                        }
                    }
                }
            ],
            "status": {
                "timestamp": "2018-06-02T22:51:28.209Z",
                "error_code": 0,
                "error_message": "",
                "elapsed": 10,
                "credit_count": 1
            }
        }

        want = CMCResponse(
            data=[
                ListingResponse(
                    id=None,
                    coin=Coin(id=1, name="Bitcoin", symbol="BTC", slug="bitcoin"),
                    quote=Quote(
                        price=9283.92,
                        volume_24h=7155680000,
                        percent_change_1h=-0.152774,
                        percent_change_24h=0.518894,
                        market_cap=852164659250.2758
                    ),
                    circulating_supply=16950100
                ),
                ListingResponse(
                    id=None,
                    coin=Coin(id=1027, name="Ethereum", symbol="ETH", slug="ethereum"),
                    quote=Quote(
                        price=1283.92,
                        volume_24h=7155680000,
                        percent_change_1h=-0.152774,
                        percent_change_24h=0.518894,
                        market_cap=158055024432
                    ),
                    circulating_supply=16950100
                )
            ],
            status={
                "timestamp": "2018-06-02T22:51:28.209Z",
                "error_code": 0,
                "error_message": "",
                "elapsed": 10,
                "credit_count": 1
            }
        )

        got = CMCResponse.from_json(json_data)

        self.assertEqual(got, want)