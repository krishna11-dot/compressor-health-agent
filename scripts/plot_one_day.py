# plot_one_day.py: draws one day of one CSV column as a PNG (read-only, dev only).
# Reading is done by load.read_one_day; this file only prints a few facts and draws.
# Run: uv run python scripts/plot_one_day.py "<csv>" TP3 2020-03-13 "<png path>"
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # draw straight to a file, no window
import matplotlib.pyplot as plt

from compressor_agent.load import read_one_day

ROWS_PER_CHUNK = 100_000


def plot_one_day(csv_path: Path, column: str, day: str, png_path: Path) -> None:
    one_day = read_one_day(csv_path, day, ROWS_PER_CHUNK)
    largest_gap = one_day["timestamp"].diff().dt.total_seconds().max()
    print(f"{day}: {len(one_day)} readings, {column} min {one_day[column].min()} "
          f"max {one_day[column].max()}, largest gap {largest_gap:.0f} s")

    figure, axes = plt.subplots(figsize=(14, 4))
    axes.plot(one_day["timestamp"], one_day[column], linewidth=0.5)
    axes.set_title(f"{column} on {day} (raw readings, about one every 10 s)")
    axes.set_xlabel("time of day (as recorded, no timezone conversion)")
    axes.set_ylabel(f"{column} (unit: see data/signals.json)")
    figure.savefig(png_path, dpi=120, bbox_inches="tight")
    print(f"saved {png_path}")


if __name__ == "__main__":
    plot_one_day(Path(sys.argv[1]), sys.argv[2], sys.argv[3], Path(sys.argv[4]))
