# explore_data.py: prints the Stage 1 report on the real MetroPT-3 CSV (read-only).
# It reads the file once, in chunks: row count, time range, gaps, biggest gaps,
# per-column min/max/NaN, source_row steps, distinct 0/1 values, missing % per day.
# Run: uv run python scripts/explore_data.py "data\raw\MetroPT3(AirCompressor).csv"
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

from compressor_agent.load import read_csv_in_chunks

ROWS_PER_CHUNK = 100_000
BIG_GAP_SECONDS = 60
NOMINAL_INTERVAL_SECONDS = 10  # PLAN.md decision 1
READINGS_PER_FULL_DAY = 86_400 // NOMINAL_INTERVAL_SECONDS  # 8,640
# Columns whose min was 0 and max was 1 in step 1.3a (not yet called on/off).
COLUMNS_SEEN_BETWEEN_0_AND_1 = ["COMP", "DV_eletric", "Towers", "MPG", "LPS",
                                "Pressure_switch", "Oil_level", "Caudal_impulses"]


def main(csv_path: Path) -> None:
    row_count = 0
    first_time: pd.Timestamp | None = None
    previous_time: pd.Timestamp | None = None
    previous_source_row: float | None = None
    source_row_steps_not_10 = 0
    gap_counts: Counter[int] = Counter()
    big_gaps: list[tuple[pd.Timestamp, float]] = []
    readings_per_day: Counter[str] = Counter()
    distinct_values: dict[str, set[float]] = {c: set() for c in COLUMNS_SEEN_BETWEEN_0_AND_1}
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
        readings_per_day.update(times.dt.strftime("%Y-%m-%d"))

        source_rows = chunk["source_row"]
        previous_source_rows = source_rows.shift(1)
        if previous_source_row is not None:
            previous_source_rows.iloc[0] = previous_source_row
        steps = (source_rows - previous_source_rows).dropna()
        source_row_steps_not_10 += int((steps != 10).sum())
        previous_source_row = float(source_rows.iloc[-1])

        for column in COLUMNS_SEEN_BETWEEN_0_AND_1:
            distinct_values[column].update(float(v) for v in chunk[column].unique())
        values = chunk.drop(columns=["timestamp"])
        chunk_mins.append(values.min())
        chunk_maxs.append(values.max())
        chunk_nans.append(values.isna().sum())
        row_count += len(chunk)
        if first_time is None:
            first_time = times.iloc[0]
        previous_time = times.iloc[-1]

    if first_time is None or previous_time is None:
        print("no rows read")
        return
    print(f"rows: {row_count}")
    print(f"first timestamp: {first_time}   last timestamp: {previous_time}")
    print(f"span: {previous_time - first_time}")
    print(f"gaps measured: {sum(gap_counts.values())} (expected rows - 1 = {row_count - 1})")
    print("most common gaps (seconds: count):")
    for seconds, count in gap_counts.most_common(10):
        print(f"  {seconds:>6} s: {count}")
    big_total_seconds = sum(gap_seconds for _, gap_seconds in big_gaps)
    print(f"gaps over {BIG_GAP_SECONDS} s: {len(big_gaps)}")
    print(f"total time inside those gaps: {pd.Timedelta(seconds=big_total_seconds)}")
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

    print(f"\nsource_row steps that are not exactly 10: {source_row_steps_not_10}")
    print("distinct values in columns seen between 0 and 1:")
    for column, seen in distinct_values.items():
        print(f"  {column:<16} {len(seen)} distinct: {sorted(seen)[:5]}")

    print_missing_by_day(readings_per_day, first_time, previous_time)
    span_seconds = (previous_time - first_time).total_seconds()
    expected_over_span = span_seconds / NOMINAL_INTERVAL_SECONDS + 1
    gap_based = sum(g / NOMINAL_INTERVAL_SECONDS - 1 for _, g in big_gaps)
    print("\ncross-check, missing readings over the whole file:")
    print(f"  span-based (expected {expected_over_span:.0f} - rows {row_count}): "
          f"{expected_over_span - row_count:.0f}")
    print(f"  gap-based (gaps over {BIG_GAP_SECONDS} s, gap/10 - 1 each):     {gap_based:.0f}")


def print_missing_by_day(readings_per_day: Counter[str],
                         first_time: pd.Timestamp, last_time: pd.Timestamp) -> None:
    all_days = list(pd.date_range(first_time.normalize(), last_time.normalize()).strftime("%Y-%m-%d"))
    first_day, last_day = all_days[0], all_days[-1]
    # A day is full when the data covers it from 00:00:00; only the last day is cut short.
    first_day_is_full = first_time == first_time.normalize()
    full_days = all_days[:-1] if first_day_is_full else all_days[1:-1]
    print(f"\nmissing % per day (1 - readings / {READINGS_PER_FULL_DAY}, clipped at 0)")
    print(f"  first day {first_day} ({'full' if first_day_is_full else 'partial'}, "
          f"from {first_time.time()}): {readings_per_day[first_day]} readings")
    print(f"  last day  {last_day} (partial, to {last_time.time()}): "
          f"{readings_per_day[last_day]} readings")
    over_full = [d for d in full_days if readings_per_day[d] > READINGS_PER_FULL_DAY]
    print(f"  full days: {len(full_days)}   days over {READINGS_PER_FULL_DAY} readings: "
          f"{len(over_full)}   max readings in a day: {max(readings_per_day[d] for d in full_days)}")
    missing_pct = pd.Series(
        {d: max(0.0, 100 * (1 - readings_per_day[d] / READINGS_PER_FULL_DAY)) for d in full_days}
    )
    print(f"  first day missing %: {missing_pct[first_day]:.1f}" if first_day_is_full else "")
    # Each bucket includes its upper edge: 0-5% means 0 <= missing <= 5.
    buckets = pd.cut(missing_pct, bins=[-1, 5, 25, 75, 100],
                     labels=["0-5%", "5-25%", "25-75%", "75-100%"])
    print("  full days by missing %:")
    print(buckets.value_counts(sort=False).to_string())
    zero_days = [d for d in full_days if missing_pct[d] == 0]
    print(f"  days with 0% missing ({len(zero_days)}): {', '.join(zero_days)}")
    print(f"  mean missing % over full days: {missing_pct.mean():.1f}")
    print(f"  median missing % over full days: {missing_pct.median():.1f}")
    clipped_sum = sum(max(0, READINGS_PER_FULL_DAY - readings_per_day[d]) for d in full_days)
    print(f"  missing readings summed over full days (clipped): {clipped_sum}")


def plot_one_day(csv_path: Path, column: str, day: str, png_path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")  # draw straight to a file, no window
    import matplotlib.pyplot as plt

    day_chunks = []
    for chunk in read_csv_in_chunks(csv_path, ROWS_PER_CHUNK):
        day_chunks.append(chunk[chunk["timestamp"].dt.strftime("%Y-%m-%d") == day])
    one_day = pd.concat(day_chunks)
    gaps = one_day["timestamp"].diff().dt.total_seconds()
    big = one_day[gaps > BIG_GAP_SECONDS]
    print(f"{day}: {len(one_day)} readings, {column} min {one_day[column].min()} "
          f"max {one_day[column].max()}, gaps over {BIG_GAP_SECONDS} s: {len(big)}")
    for _, row in big.iterrows():
        print(f"  gap ending {row['timestamp']}: {gaps[row.name]:.0f} s")

    figure, axes = plt.subplots(figsize=(14, 4))
    axes.plot(one_day["timestamp"], one_day[column], linewidth=0.5)
    axes.set_title(f"{column} on {day} (raw readings, about one every 10 s)")
    axes.set_xlabel("time of day (as recorded, no timezone conversion)")
    axes.set_ylabel(f"{column} (unit: see UCI page)")
    figure.savefig(png_path, dpi=120, bbox_inches="tight")
    print(f"saved {png_path}")


if __name__ == "__main__":
    if len(sys.argv) == 5:  # csv_path column day png_path
        plot_one_day(Path(sys.argv[1]), sys.argv[2], sys.argv[3], Path(sys.argv[4]))
    else:
        main(Path(sys.argv[1]))
