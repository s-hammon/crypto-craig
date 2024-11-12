import asyncio
import unittest

from sqlalchemy.util import counter

from crawler.app import coin_worker

class TestCoinWorker(unittest.TestCase):
    def test_coin_worker_schedule(self):
        counter = 0
        async def job():
            print("simulating job")
            nonlocal counter
            counter += 1
        
        asyncio.run(coin_worker(job, 0.1, 2))

        self.assertEqual(2, counter)


    def test_coin_worker_fail(self):
        async def job():
            print("simulating job")
            raise ValueError("job failed")

        with self.assertRaises(Exception):
            asyncio.run(coin_worker(job, 0.1))
