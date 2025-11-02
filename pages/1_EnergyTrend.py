import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates

DATA_PATH = r"E:\homework\9001\9001-final\energy_data_2024.xlsx"

st.set_page_config(page_title="📈 Energy Trend", layout="wide")
st.markdown("<h1 style='text-align:center;color:#003366;'>📈 Daily Energy Consumption Trend</h1>", unsafe_allow_html=True)
st.caption("Energy variation analysis within selected period")

if "df" in st.session_state:
    df = st.session_state["df"]
    start_date = st.session_state.get("start_date", datetime(2024, 1, 1))
    end_date = st.session_state.get("end_date", datetime(2024, 3, 31))
    energy_filter = st.session_state.get("energy_filter", ["elec"])
    system_type = st.session_state.get("system_type", "all_equipments")

elif os.path.exists(DATA_PATH):
    df = pd.read_excel(DATA_PATH)
    df.rename(columns={df.columns[0]: "time"}, inplace=True)
    df["time"] = pd.to_datetime(df["time"])
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 3, 31)
    energy_filter = ["elec"]
    system_type = "all_equipments"
    st.info("💾 Loaded data from local file instead of session.")
else:
    st.error("No dataset found. Please upload data in the main dashboard first.")
    st.stop()

df["time"] = pd.to_datetime(df["time"], errors="coerce")
df["date"] = df["time"].dt.date

energy_cols = [col for col in df.columns if any(col.startswith(e) for e in energy_filter)]
if not energy_cols:
    st.error("No matching energy columns found. Please check your selected energy types.")
    st.stop()

if isinstance(start_date, datetime):
    start_date = start_date.date()
if isinstance(end_date, datetime):
    end_date = end_date.date()


df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

daily_energy = df.groupby("date")[energy_cols].max() - df.groupby("date")[energy_cols].min()
daily_energy["total_energy"] = daily_energy.sum(axis=1)

st.markdown(f"**🗓 Selected Period:** `{start_date}` → `{end_date}`")
st.markdown(f"**🔋 Energy Type:** `{', '.join(energy_filter)}` | **🏭 System Type:** `{system_type}`")

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(daily_energy.index, daily_energy["total_energy"], marker='o', color="#007acc")
num_points = len(daily_energy)
interval = max(1, num_points // 7)
ax.xaxis.set_major_locator(mdates.DayLocator(interval=interval))
fig.autofmt_xdate(rotation=30)
ax.set_xlabel("Date")
ax.set_ylabel("Energy Consumption")
ax.set_title("Daily Energy Consumption Trend")
ax.grid(True, linestyle="--", alpha=0.5)
st.pyplot(fig)

st.page_link("main.py", label="⬅️ Back to Dashboard", icon="🏠")