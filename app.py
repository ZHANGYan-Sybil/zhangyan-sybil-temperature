# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib","streamlit"]
# ///
"""
Assignment2 Interactive Version
Input-State-Response model (Week04 standard)
One control: select single month
One response: pure single-month daily temperature chart
Perfect axis alignment: Day1 flush left, last day flush right
Clean numeric x-axis (no overlapping text)
"""
import csv
from pathlib import Path
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import matplotlib.colors as mcolors

# ---------------- 常量配置 ----------------
# 每月真实天数（2026平年）
MONTH_DAYS = {1:31, 2:28, 3:31, 4:30, 5:31, 6:30}
MONTH_NAMES = {1:"Jan", 2:"Feb", 3:"Mar", 4:"Apr", 5:"May", 6:"Jun"}

# 温度渐变配色锚点（完全保留你的原版配色）
TEMP_COLOR_KEYPOINTS = [
    (13.4, "#4DB2FF"), (18, "#4DDEFF"), (21, "#81FFF9"),
    (24, "#6FFFCA"), (26, "#BFFF96"), (28, "#FFE75C"), (30.8, "#FFB35C"),
]

# 数据路径
DATA = Path(__file__).parent / "data" / "hko-daily-mean-temperature-2026.csv"

# ---------------- 工具函数 ----------------
def temperature_to_rgb(temp, keypoints):
    temps = [p[0] for p in keypoints]
    rgb = [mcolors.to_rgb(p[1]) for p in keypoints]
    if temp <= temps[0]: return rgb[0]
    if temp >= temps[-1]: return rgb[-1]
    for i in range(len(temps)-1):
        if temps[i] <= temp <= temps[i+1]:
            r = (temp - temps[i]) / (temps[i+1] - temps[i])
            return tuple(a*(1-r)+b*r for a, b in zip(rgb[i], rgb[i+1]))
    return rgb[0]

@st.cache_data
def load_rows():
    """读取合法温度数据"""
    kept = []
    with DATA.open(encoding="utf-8-sig", newline="") as f:
        for line in csv.reader(f):
            if line and line[0].isdigit():
                kept.append(line)
    return kept

# ---------------- Streamlit 交互核心（标准 Input-State-Response） ----------------
st.title("Hong Kong Daily Mean Temperature (2026)")
st.subheader("Single-Month Interactive Visualisation")

# Input：唯一控件 - 选择独立月份
selected_month = st.selectbox(
    "Select a single month to view daily temperature",
    options=list(MONTH_NAMES.keys()),
    format_func=lambda m: MONTH_NAMES[m]
)

# State：存储当前选中月份
current_month = selected_month
max_day = MONTH_DAYS[current_month]

# Response：仅筛选当前选中月份数据
month_data = []
for row in load_rows():
    _, mo, d, val, _ = row
    if int(mo) != current_month:
        continue
    if val == "***":
        continue
    month_data.append((int(d), float(val)))

# 构建渐变曲线
segments, seg_colors = [], []
for i in range(len(month_data)-1):
    p0, p1 = month_data[i], month_data[i+1]
    segments.append([p0, p1])
    avg_temp = (p0[1] + p1[1]) / 2
    seg_colors.append(temperature_to_rgb(avg_temp, TEMP_COLOR_KEYPOINTS))

# ---------------- 最终完美横轴：首尾顶格、纯数字刻度、无重叠 ----------------
fig, ax = plt.subplots(figsize=(12, 5))
if segments:
    lc = LineCollection(segments, colors=seg_colors, linewidths=2.5)
    ax.add_collection(lc)

# 强制首尾贴边，零留白
ax.set_xlim(1, max_day)

# 刻度：7天间隔 + 强制首尾显示，纯数字无文字
# 横轴刻度：固定 第1天、第10天、第20天、当月最后一天
tick_list = [1, 10, 20, max_day]

ax.set_xticks(tick_list)
ax.set_xticklabels([str(d) for d in tick_list])


# 纵轴配置
ax.set_ylim(12, 32)
ax.set_yticks(range(12, 33, 2))

# 图表美化
ax.set_title(f"Daily Mean Temperature – {MONTH_NAMES[current_month]} 2026")
ax.set_xlabel("Day")
ax.set_ylabel("Daily Mean Temperature (°C)")
ax.grid(color="#dddddd", linestyle="-", linewidth=0.6)
ax.axhline(y=18, color="#ff4444", linestyle="--", linewidth=1, alpha=0.35, label="Cold threshold: 18℃")
ax.axhline(y=28, color="#ff4444", linestyle="--", linewidth=1, alpha=0.35, label="Hot threshold: 28℃")
ax.legend(loc="upper right")
ax.set_axisbelow(True)
fig.tight_layout()

# 页面输出
st.pyplot(fig)
st.caption(f"Showing full daily temperature data for {MONTH_NAMES[current_month]} 2026")
