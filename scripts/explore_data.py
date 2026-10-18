# explore_data.py: prints the Stage 1 report on the real MetroPT-3 CSV (read-only).
# Part 1: row count, time range, and the gaps in seconds between timestamps.
# Run: uv run python scripts/explore_data.py "data\raw\MetroPT3(AirCompressor).csv"
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

from compressor_agent.load import read_csv_in_chunks

ROWS_PER_CHUNK = 100_000
BIG_GAP_SECONDS = 60


def main(csv_path: Path) -> None:
    row_count = 0
    first_time: pd.Timestamp | None = None
    previous_time: pd.Timestamp | None = None
    gap_counts: Counter[int] = Counter()

    for chunk in read_csv_in_chunks(csv_path, ROWS_PER_CHUNK):
        times = chunk["timestamp"]
        gaps = times.diff().dt.total_seconds().dropna()
        if previous_time is not None:
            gap_across_chunks = (times.iloc[0] - previous_time).total_seconds()
            gaps = pd.concat([pd.Series([gap_across_chunks]), gaps])
        gap_counts.update(gaps.astype(int).value_counts().to_dict())
        row_count += len(chunk)
        if first_time is None:
            first_time = times.iloc[0]
        previous_time = times.iloc[-1]

    print(f"rows: {row_count}")
    print(f"first timestamp: {first_time}   last timestamp: {previous_time}")
    if first_time is not None and previous_time is not None:
        print(f"span: {previous_time - first_time}")
    print(f"gaps measured: {sum(gap_counts.values())} (expected rows - 1 = {row_count - 1})")
    print("most common gaps (seconds: count):")
    for seconds, count in gap_counts.most_common(10):
        print(f"  {seconds:>6} s: {count}")
    big = {s: c for s, c in gap_counts.items() if s > BIG_GAP_SECONDS}
    print(f"gaps over {BIG_GAP_SECONDS} s: {sum(big.values())}")
    print(f"total time inside those gaps: {pd.Timedelta(seconds=sum(s * c for s, c in big.items()))}")
    print(f"smallest gap: {min(gap_counts)} s   largest gap: {max(gap_counts)} s")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
