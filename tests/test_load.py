# test_load.py: checks read_csv_in_chunks on a hand-made 5-row CSV.
# Known answers: chunks of 2, 2 and 1 rows; timestamps parsed as date-times;
# column names exactly as in the file, with the unnamed first one as source_row.
from pathlib import Path

import pandas as pd

from compressor_agent.load import read_csv_in_chunks

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
