import os

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
from config_equipment import equip_dic

st.set_page_config(page_title="📊 Energy Comparison", layout="wide")
st.markdown("<h1 style='text-align:center;color:#003366;'>📊 Average Energy Consumption Comparison</h1>", unsafe_allow_html=True)
st.caption("Top devices ranked by total energy usage within selected period")

DATA_PATH = r"E:\homework\9001\9001-final\energy_data_2024.xlsx"

if "df" in st.session_state:
    df = st.session_state["df"]
    start_date = st.session_state.get("start_date", datetime(2024, 1, 1))
    end_date = st.session_state.get("end_date", datetime(2024, 3, 31))
    energy_filter = st.session_state.get("energy_filter", ["elec"])
    system_type = st.session_state.get("system_type", "all_equipments")
    st.info("Using dataset from main dashboard session.")
elif os.path.exists(DATA_PATH):
    df = pd.read_excel(DATA_PATH)
    df.rename(columns={df.columns[0]: "time"}, inplace=True)
    df["time"] = pd.to_datetime(df["time"])
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 3, 31)
    energy_filter = ["elec"]
    system_type = "all_equipments"
    st.success(f"📂 Loaded local file: `{os.path.basename(DATA_PATH)}`")
else:
    st.error("No dataset found. Please upload data in the main dashboard first.")
    st.stop()

df["time"] = pd.to_datetime(df["time"], errors="coerce")
df["date"] = df["time"].dt.date

if isinstance(start_date, datetime):
    start_date = start_date.date()
if isinstance(end_date, datetime):
    end_date = end_date.date()

energy_cols = [col for col in df.columns if any(col.startswith(e) for e in energy_filter)]
if not energy_cols:
    st.error("No matching energy columns found. Please check your selected energy types.")
    st.stop()

df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
daily_energy = df.groupby("date")[energy_cols].max() - df.groupby("date")[energy_cols].min()

daily_sum = daily_energy.sum().sort_values(ascending=False)

st.markdown(f"**🗓 Selected Period:** `{start_date}` → `{end_date}`")
st.markdown(f"**🔋 Energy Type:** `{', '.join(energy_filter)}` | **🏭 System Type:** `{system_type}`")

renamed = daily_sum.rename(index=lambda x: equip_dic.get(x, x))
top15 = renamed.head(15)
top8 = renamed.head(8)

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

# Left side: Horizontal bar chart (Top 15)
top15 = top15[top15 > 0]
top15.plot(kind="barh", color="#42A5F5", ax=axes[0])
axes[0].invert_yaxis()
axes[0].set_title("Top 15 Devices by Total Energy Consumption", fontsize=12, color="#003366")
axes[0].set_xlabel("Energy Usage (kWh / m³)")
axes[0].grid(True, linestyle="--", alpha=0.4)

# Right side: Pie chart (Top 8)
explode = [0.03] * len(top8)
wedges, texts, autotexts = axes[1].pie(
    top8,
    autopct="%1.1f%%",
    startangle=140,
    colors=plt.cm.Paired.colors,
    pctdistance=0.8,
    explode=explode,
)

kw = dict(arrowprops=dict(arrowstyle="-", color="gray", lw=0.5),
          bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.7),
          zorder=0, va="center")

for i, p in enumerate(wedges):
    ang = (p.theta2 - p.theta1)/2. + p.theta1
    y = np.sin(np.deg2rad(ang))
    x = np.cos(np.deg2rad(ang))
    horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
    connectionstyle = f"angle,angleA=0,angleB={ang}"
    kw["arrowprops"].update({"connectionstyle": connectionstyle})
    axes[1].annotate(
        top8.index[i],
        xy=(x, y),
        xytext=(1.2*np.sign(x), 1.2*y),
        horizontalalignment=horizontalalignment,
        fontsize=7,
        **kw
    )

axes[1].set_title("Energy Consumption Share (Top 8)", fontsize=12, color="#003366")

plt.tight_layout()
st.pyplot(fig)

st.page_link("main.py", label="⬅️ Back to Dashboard", icon="🏠")