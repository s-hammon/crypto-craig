import os
import argparse
import asyncio

from sqlalchemy import create_engine

TURSO_DATABASE_URL = os.environ.get("DB_URL")
TURSO_AUTH_TOKEN = os.environ.get("TURSO_AUTH_TOKEN")
TURSO_AUTH_TOKEN_DISCORD_CLIENT = os.environ.get(
    "TURSO_AUTH_TOKEN_DISCORD_CLIENT", "MISSING_TURSO_AUTH_TOKEN"
)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    crawler_parser = subparsers.add_parser("crawler")
    crawler_parser.add_argument("--request-interval", type=int, default=3600)
    crawler_parser.add_argument("--max-iter", type=int, default=-1)

    crawler_job = crawler_parser.add_subparsers(
        dest="job", description="Run the crawler once as a standalone job."
    )
    job_parser = crawler_job.add_parser("job")
    job_parser.add_argument(
        "--extra-param", type=str, help="Optional parameter for job"
    )

    craig_parser = subparsers.add_parser("craig")
    craig_parser.add_argument("--debug", action="store_true", default=False)

    args = parser.parse_args()
    match args.command:
        case "crawler":
            from crawler.worker import coin_job
            DB_URL = f"sqlite+{TURSO_DATABASE_URL}/?authToken={TURSO_AUTH_TOKEN}&secure=true"

            # if job, run worker.coin_job
            if args.job:
                asyncio.run(coin_job(create_engine(DB_URL)))
                return

            from crawler.worker import coin_worker

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
            DB_URL = f"sqlite+{TURSO_DATABASE_URL}/?authToken={TURSO_AUTH_TOKEN_DISCORD_CLIENT}&secure=true"

            run(create_engine(DB_URL), args.debug)


main()
