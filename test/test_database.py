import unittest

import pandas as pd
from sqlalchemy import text

from craig.models import Database, connect_db


class TestDatabase(unittest.TestCase):
    def test_connect_db(self):
        with connect_db("sqlite://") as conn:
            res = conn.execute(text("SELECT 1"))
            value = res.fetchone()
            if not value:
                self.fail("No value returned")

        self.assertEqual(1, value[0])

    def test_database_execute(self):
        cases = [
            {
                "name": "select 1",
                "query": "SELECT 1",
                "want": pd.DataFrame({"1": [1]}),
            },
            {
                "name": "create table",
                "query": "CREATE TABLE test (id INTEGER)",
                "want": pd.DataFrame(),
            }
        ]

        db = Database(url="sqlite://")
        for case in cases:
            got = db.execute(case["query"])

            self.assertTrue(case["want"].equals(got), msg=f'case: {case["name"]}')

    def test_database_execute_throw_error(self):
        cases = [
            {
                "name": "table not exists",
                "query": "SELECT * FROM table_not_exists",
                "want": Exception,
            },
            {
                "name": "invalid query",
                "query": "SELECT * FROM",
                "want": Exception,
            },
            {
                "name": "empty query",
                "query": "",
                "want": ValueError,
            }
        ]

        db = Database(url="sqlite://")
        for case in cases:
            with self.assertRaises(case["want"], msg=f'case: {case["name"]}'):
                db.execute(case["query"])