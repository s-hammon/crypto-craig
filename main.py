import os
import argparse
import asyncio

from sqlalchemy import create_engine

TURSO_DATABASE_URL = os.environ.get("DB_URL")
TURSO_AUTH_TOKEN_DISCORD_CLIENT = os.environ.get(
    "TURSO_AUTH_TOKEN_DISCORD_CLIENT", "MISSING_TURSO_AUTH_TOKEN"
)
DB_URL = f"sqlite+{TURSO_DATABASE_URL}/?authToken={TURSO_AUTH_TOKEN_DISCORD_CLIENT}&secure=true"


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    crawler_parser = subparsers.add_parser("crawler")
    crawler_parser.add_argument("--request-interval", type=int, default=3600)
    crawler_parser.add_argument("--max-iter", type=int, default=-1)

    craig_parser = subparsers.add_parser("craig")
    craig_parser.add_argument("--debug", action="store_true", default=False)

    args = parser.parse_args()
    match args.command:
        case "crawler":
            from crawler.worker import coin_worker, coin_job

            asyncio.run(
                coin_worker(
                    coin_job,
                    args.request_interval,
                    args.max_iter,
                    engine=create_engine(DB_URL),
                )
            )
        case "craig":
            from craig.app import run

            run(create_engine(DB_URL), args.debug)


main()
