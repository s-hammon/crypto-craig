import requests
import os

from sqlalchemy import Engine
from sqlalchemy.orm import Session

from models.entities import CMCResponse
from models.repositories import Listing


CMC_PRO_API_KEY = os.environ.get("CMC_PRO_API_KEY")
CMC_PRO_BASE_URL = "https://pro-api.coinmarketcap.com/v1"


def get_listings() -> CMCResponse:
    url = f"{CMC_PRO_BASE_URL}/cryptocurrency/listings/latest"
    headers = _cmc_headers()
    print(f"fetching data from {url}")

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return CMCResponse.from_json(response.json())


def to_db(response: CMCResponse, engine: Engine) -> None:
    """
    TODO: see if we can abstract engine away from here (I mean, I think we are...)
    """
    objs = [Listing.from_model(data) for data in response.data]
    with Session(engine) as session:
        session.add_all(objs)
        session.commit()


def _cmc_headers():
    return {
        "Accept": "application/json",
        "X-CMC_PRO_API_KEY": CMC_PRO_API_KEY,
    }
