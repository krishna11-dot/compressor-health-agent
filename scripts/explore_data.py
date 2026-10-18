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
    big_gaps: list[tuple[pd.Timestamp, float]] = []
    chunk_mins: list[pd.Series] = []
    chunk_maxs: list[pd.Series] = []
    chunk_nans: list[pd.Series] = []

    for chunk in read_csv_in_chunks(csv_path, ROWS_PER_CHUNK):
        times = chunk["timestamp"]
        previous_times = times.shift(1)
        if previous_time is not None:
            previous_times.iloc[0] = previous_time
        gaps = (times - previous_times).dt.total_seconds().dropna()
        gap_counts.update(int(gap) for gap in gaps)
        is_big = gaps > BIG_GAP_SECONDS
        big_gaps.extend(zip(previous_times[gaps.index][is_big], gaps[is_big]))
        values = chunk.drop(columns=["timestamp"])
        chunk_mins.append(values.min())
        chunk_maxs.append(values.max())
        chunk_nans.append(values.isna().sum())
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

    print("\n10 biggest gaps (reading before the gap, gap length):")
    for start, gap_seconds in sorted(big_gaps, key=lambda gap: gap[1], reverse=True)[:10]:
        print(f"  {start}  {pd.Timedelta(seconds=gap_seconds)}")
    print(f"\nbig gaps per month: {Counter(start.strftime('%Y-%m') for start, _ in big_gaps)}")

    print("\nper column: min, max, NaN count")
    summary = pd.DataFrame({
        "min": pd.concat(chunk_mins, axis=1).min(axis=1),
        "max": pd.concat(chunk_maxs, axis=1).max(axis=1),
        "nan": pd.concat(chunk_nans, axis=1).sum(axis=1),
    })
    print(summary.to_string())


if __name__ == "__main__":
    main(Path(sys.argv[1]))
