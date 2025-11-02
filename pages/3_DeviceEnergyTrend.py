import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="⚡ Device Energy Trend", layout="wide")
st.markdown("<h1 style='text-align:center;color:#003366;'>⚡ Device Daily Energy Trend</h1>", unsafe_allow_html=True)
st.caption("View daily energy consumption trend for selected devices.")

if "df" not in st.session_state:
    st.warning("Please load dataset from the main dashboard first.")
    st.stop()

df = st.session_state["df"]
selected_devices = st.session_state.get("selected_devices", [])
start_date = st.session_state.get("start_date", datetime(2024, 1, 1).date())
end_date = st.session_state.get("end_date", datetime(2024, 3, 31).date())

if not selected_devices:
    st.info("Please select one or more devices from the left sidebar on the main dashboard.")
    st.stop()

df["time"] = pd.to_datetime(df["time"], errors="coerce")
df["date"] = df["time"].dt.date
df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

# Daily energy consumption
try:
    daily_energy = df.groupby("date")[selected_devices].agg(lambda x: x.max() - x.min())
except KeyError:
    st.error("Selected devices not found in current dataset.")
    st.stop()

st.markdown(f"**📅 Period:** `{start_date}` → `{end_date}` | **Devices:** `{', '.join(selected_devices)}`")

fig, ax = plt.subplots(figsize=(9, 4))
daily_energy.plot(ax=ax)
ax.set_title("Daily Energy Consumption (Selected Devices)", fontsize=12, color="#003366")
ax.set_xlabel("Date")
ax.set_ylabel("Energy Usage (kWh / m³)")
ax.grid(True, linestyle="--", alpha=0.4)
ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=7)
st.pyplot(fig, use_container_width=True)

st.page_link("main.py", label="⬅️ Back to Dashboard", icon="🏠")
