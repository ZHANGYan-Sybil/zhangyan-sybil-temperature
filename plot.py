# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib"]
# ///
"""
Assignment2: Hong Kong Jan‑Jun 2026 daily mean temperature
Gradient‑colored line based on temperature value.
Only keep data Jan‑Jun, discard Jul‑Dec.
uv run plot.py
"""
import csv
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import matplotlib.colors as mcolors


FILE = "hko-daily-mean-temperature-2026.csv"
PICTURE = "hk-temp-jan-jun-2026.png"

HERE = Path(__file__).parent
DATA = HERE / "data" / FILE
OUT = HERE / "out"

# Temperature‑color anchor points (temp ℃ , hex color)
TEMP_COLOR_KEYPOINTS = [
    (13.4, "#4DB2FF"),
    (18, "#4DDEFF"),
    (21, "#81FFF9"),
    (24, "#6FFFCA"),
    (26, "#BFFF96"),
    (28, "#FFE75C"),
    (30.8, "#FFB35C"),
]

MONTH_DAYS = {
    1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
    7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
}


def rows(path):
    """Read csv, keep only lines starting with year digit."""
    kept = []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for line in csv.reader(handle):
            if line and line[0].isdigit():
                kept.append(line)
    return kept


def temperature_to_rgb(temp: float, keypoints):
    """
    Custom written function for assignment2.
    Map temperature value to interpolated RGB tuple (range 0‑1).
    """
    temps = [p[0] for p in keypoints]
    hex_colors = [p[1] for p in keypoints]
    rgb_list = [mcolors.to_rgb(h) for h in hex_colors]

    if temp <= temps[0]:
        return rgb_list[0]
    if temp >= temps[-1]:
        return rgb_list[-1]

    for i in range(len(temps) - 1):
        t0, t1 = temps[i], temps[i+1]
        c0, c1 = rgb_list[i], rgb_list[i+1]
        if t0 <= temp <= t1:
            ratio = (temp - t0) / (t1 - t0)
            r = c0[0] * (1 - ratio) + c1[0] * ratio
            g = c0[1] * (1 - ratio) + c1[1] * ratio
            b = c0[2] * (1 - ratio) + c1[2] * ratio
            return (r, g, b)
    return rgb_list[0]


def main():
    table = rows(DATA)
    points = []

    # loop over dataset (required loop for assignment2)
    for row in table:
        year_str, month_str, day_str, val_str, qual = row
        m = int(month_str)
        if m > 6:
            continue
        if val_str == "***":
            continue
        d = int(day_str)
        temp = float(val_str)
        x = m + d / MONTH_DAYS[m]
        points.append((x, temp))

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    print(f"Valid data points: {len(points)}")
    print(f"Temperature range: min={min(ys):.1f} ℃ , max={max(ys):.1f} ℃")

    # build segments for gradient‑colored LineCollection
    segments = []
    seg_colors = []
    for i in range(len(points) - 1):
        p0 = points[i]
        p1 = points[i+1]
        segments.append([p0, p1])
        avg_temp = (p0[1] + p1[1]) / 2
        seg_colors.append(temperature_to_rgb(avg_temp, TEMP_COLOR_KEYPOINTS))

    lc = LineCollection(segments, colors=seg_colors, linewidths=2.5)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.add_collection(lc)

    ax.set_xlim(0.8, 6.2)
    ax.set_xticks([1, 2, 3, 4, 5, 6])
    ax.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun"])

    ax.set_ylim(12, 32)
    ax.set_yticks([12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32])

    ax.set_title("Hong Kong Observatory: Daily Mean Temperature (Jan‑Jun 2026)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Daily Mean Temperature (°C)")

    ax.grid(color="#dddddd", linestyle="-", linewidth=0.6)
    ax.set_axisbelow(True)

    fig.tight_layout()
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / PICTURE, dpi=150)
    print(f"Saved picture: out/{PICTURE}")
    plt.show()


if __name__ == "__main__":
    main()
