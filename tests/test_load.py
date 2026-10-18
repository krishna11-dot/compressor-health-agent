# test_load.py: checks load.py on small hand-made CSVs with known answers.
# read_csv_in_chunks: chunks of 2, 2, 1; date-times; exact names, first one source_row.
# read_one_day: keeps only that day's rows, including across a chunk boundary.
from pathlib import Path

import pandas as pd

from compressor_agent.load import read_csv_in_chunks, read_one_day

HEADER = ",timestamp,TP2,COMP"
ROWS = [f"{i * 10},2020-02-01 00:00:{i * 10:02d},0.5,1.0" for i in range(5)]


def test_read_csv_in_chunks(tmp_path: Path) -> None:
    csv_path = tmp_path / "tiny.csv"
    csv_path.write_text("\n".join([HEADER, *ROWS]) + "\n")

    chunks = list(read_csv_in_chunks(csv_path, rows_per_chunk=2))

    assert [len(chunk) for chunk in chunks] == [2, 2, 1]
    for chunk in chunks:
        assert list(chunk.columns) == ["source_row", "timestamp", "TP2", "COMP"]
        assert pd.api.types.is_datetime64_any_dtype(chunk["timestamp"])


def test_read_one_day_keeps_only_that_day(tmp_path: Path) -> None:
    csv_path = tmp_path / "two_days.csv"
    rows = ["0,2020-02-01 23:59:50,0.5,1.0", "10,2020-02-02 00:00:00,0.6,1.0",
            "20,2020-02-02 00:00:10,0.7,0.0", "30,2020-02-03 00:00:00,0.8,0.0"]
    csv_path.write_text("\n".join([HEADER, *rows]) + "\n")

    one_day = read_one_day(csv_path, "2020-02-02", rows_per_chunk=2)

    assert list(one_day["source_row"]) == [10, 20]
