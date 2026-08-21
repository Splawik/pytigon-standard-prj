import datetime
import os

import duckdb
import numpy as np
import pandas as pl
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Prepare test data"

    def handle(self, *args, **options):
        n = 1000000
        data_path = os.path.join(settings.DATA_PATH, settings.PRJ_NAME)

        start_time = datetime.datetime(1900, 1, 1)

        df = pl.DataFrame(
            {
                "date": [start_time + datetime.timedelta(j) for j in range(n)],
                "y1": np.random.rand(n),
                "y2": np.random.rand(n),
                "y3": 1.0 * np.random.rand(n),
            }
        )
        duckdb.sql(
            "COPY (SELECT * FROM df) TO '%s' (FORMAT PARQUET);"
            % os.path.join(data_path, "date_sample.parquet")
        )

        df = pl.DataFrame(
            {
                "year": [1900 + j for j in range(150)],
                "y1": 100 * np.random.rand(150),
                "y2": 100 * np.random.rand(150),
            }
        )
        duckdb.sql(
            "COPY (SELECT * FROM df) TO '%s' (FORMAT PARQUET);"
            % os.path.join(data_path, "year_sample.parquet")
        )

        df = pl.DataFrame(
            {
                "x": 100 * np.random.rand(100000),
                "y": 100 * np.random.rand(100000),
            }
        )
        duckdb.sql(
            "COPY (SELECT * FROM df) TO '%s' (FORMAT PARQUET);"
            % os.path.join(data_path, "int_sample.parquet")
        )
