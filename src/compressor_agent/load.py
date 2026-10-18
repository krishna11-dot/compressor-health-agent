# load.py: reads the MetroPT-3 CSV from disk in chunks, so the large file never
# has to fit in memory at once. Column names stay exactly as in the file, except
# the unnamed first column, which is renamed source_row (its meaning is unknown).
from collections.abc import Iterator
from pathlib import Path

import pandas as pd

PANDAS_NAME_FOR_UNNAMED_FIRST_COLUMN = "Unnamed: 0"
SOURCE_ROW = "source_row"
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def read_csv_in_chunks(csv_path: Path, rows_per_chunk: int) -> Iterator[pd.DataFrame]:
    reader = pd.read_csv(
        csv_path,
        chunksize=rows_per_chunk,
        parse_dates=["timestamp"],
        date_format=TIMESTAMP_FORMAT,
    )
    for chunk in reader:
        first_column = chunk.columns[0]
        if first_column != PANDAS_NAME_FOR_UNNAMED_FIRST_COLUMN:
            raise ValueError(f"expected an unnamed first column, got {first_column!r}")
        yield chunk.rename(columns={first_column: SOURCE_ROW})
