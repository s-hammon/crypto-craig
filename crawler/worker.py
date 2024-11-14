import asyncio
from datetime import datetime
from typing import Callable

from sqlalchemy import Engine

from crawler.handlers import get_listings, to_db


MAX_RETRIES = 3


async def coin_job(engine: Engine):
    print(f"Fetching data at {datetime.now()}")
    response = get_listings()
    to_db(response, engine)
    print("data fetched and saved")


async def coin_worker(
    job: Callable, request_interval: float, max_iter: int = -1, **kwargs
):
    iterations = None
    if max_iter == 0:
        raise ValueError(
            "max_iter must be greater than 0 or set to default value of -1"
        )
    elif max_iter > 0:
        iterations = 0

    failures = 0
    print("starting worker")
    while iterations is None or iterations < max_iter:
        iterations = safe_increment(iterations)
        try:
            await job(**kwargs)
            failures = 0
        except Exception as e:
            print(f"Failed to fetch data: {e}")
            failures += 1
            if failures >= MAX_RETRIES:
                print("Max retries reached, exiting worker")
                raise Exception("Max retries reached")

        await asyncio.sleep(request_interval)


def safe_increment(iterations: int | None):
    if iterations is not None:
        iterations += 1
    return iterations
