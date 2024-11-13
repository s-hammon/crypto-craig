import requests
import os

from sqlalchemy.orm import Session

from craig.app import new_engine
from craig.models import CMCResponse, Listing


TURSO_AUTH_TOKEN = os.environ.get("TURSO_AUTH_TOKEN", "MISSING_TURSO_AUTH_TOKEN")


engine = new_engine(TURSO_AUTH_TOKEN)

CMC_PRO_API_KEY = os.environ.get("CMC_PRO_API_KEY")
CMC_PRO_BASE_URL = "https://pro-api.coinmarketcap.com/v1"


def get_listings() -> CMCResponse:
    url = f"{CMC_PRO_BASE_URL}/cryptocurrency/listings/latest"
    headers = _cmc_headers()
    print(f"fetching data from {url} with headers: {headers}")

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return CMCResponse.from_json(response.json())


def to_db(response: CMCResponse) -> None:
    objs = [ Listing.from_model(data) for data in response.data ]
    with Session(engine) as session:
        session.add_all(objs)
        session.commit()

def _cmc_headers():
    return {
        "Accept": "application/json",
        "X-CMC_PRO_API_KEY": CMC_PRO_API_KEY,
    }
