import argparse
import asyncio

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    crawler_parser = subparsers.add_parser("crawler")
    crawler_parser.add_argument("--request-interval", type=int, default=3600)
    crawler_parser.add_argument("--max-iter", type=int, default=-1)
    
    craig_parser = subparsers.add_parser("craig")

    args = parser.parse_args()
    match args.command:
        case "crawler":
            from crawler.worker import coin_worker, coin_job
            asyncio.run(coin_worker(coin_job, args.request_interval, args.max_iter))
        case "craig":
            from craig.app import run
            run()


main()