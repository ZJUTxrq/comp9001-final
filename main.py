# ============================================
# Intelligent Energy Consumption Diagnosis System for Green Drug Manufacturing (Main Program)
# Left parameter bar + Large screen visualization layout on the right
# ============================================
import os
from typing import List
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from models_energy import Energy
from config_equipment import equip_dic, utility_system, equipments

st.set_page_config(page_title="Drug Green Manufacturing Energy Consumption System", layout="wide")

st.markdown("""
<style>
    h1 {color:#003366;text-align:center;font-weight:800;padding-bottom:10px;}
    .card {background-color:white;padding:15px 25px;border-radius:12px;
           box-shadow:2px 2px 10px rgba(0,0,0,0.1);text-align:center;}
    .metric {font-size:28px;color:#007acc;font-weight:700;}
    .small {font-size:14px;color:#888;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🏭 Drug Green Manufacturing Energy Consumption System</h1>", unsafe_allow_html=True)
st.caption("Multi-energy visualization platform based on Streamlit")
plt.rcParams['font.family'] = 'Segoe UI Emoji'  # Windows

# Hide the default Streamlit page selector.
st.set_page_config(
    page_title="Energy Dashboard",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject CSS to hide the "Main / Pages" navigation bar on the left side.
hide_pages_css = """
    <style>
    section[data-testid="stSidebarNav"] {display: none;}
    section[data-testid="stSidebarHeader"] {display: none;}
    </style>
"""
st.markdown(hide_pages_css, unsafe_allow_html=True)


# Time analysis function
def parse_time(value):
    if pd.isna(value):
        return None
    for fmt in ["%Y-%m-%d %I:%M:%S %p", "%Y/%m/%d %I:%M:%S %p",
                "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"]:
        try:
            return datetime.strptime(str(value), fmt)
        except Exception:
            continue
    return pd.to_datetime(value, errors="coerce")


def filter_by_date(records_or_df, start_date, end_date):
    """Unified filtering function, compatible with Energy object list and DataFrame"""
    if isinstance(records_or_df, list) and all(hasattr(r, "timestamp") for r in records_or_df):
        filtered = [r for r in records_or_df if start_date <= r.timestamp.date() <= end_date]
        df = pd.DataFrame([vars(r) for r in filtered])
        df["time"] = pd.to_datetime(df["timestamp"])
        df.drop(columns=["timestamp"], inplace=True, errors="ignore")
        return df
    else:
        df = records_or_df.copy()
        df["time"] = pd.to_datetime(df["time"], errors="coerce")
        return df[(df["time"].dt.date >= start_date) & (df["time"].dt.date <= end_date)]


# Fixed path
DATA_PATH = r"E:\homework\9001\9001-final\energy_data_2024.xlsx"

# layout
left, right = st.columns([1.1, 3.2], gap="large")

# ========== Left control bar ==========
with left:
    with st.expander("⚙️ Parameter Setting", expanded=True):
        st.markdown("#### 📂 Data Source")

        # Read from the local directory first
        if os.path.exists(DATA_PATH):
            df = pd.read_excel(DATA_PATH)
            st.session_state["df"] = df
            st.success(f" Data loaded automatically from: `{os.path.basename(DATA_PATH)}`")
            try:
                energy_records: List[Energy] = [
                    Energy(timestamp=row["time"], **{k: v for k, v in row.items() if k != "time"})
                    for _, row in df.iterrows()
                ]
                st.session_state["energy_data"] = energy_records
            except Exception as e:
                st.warning(f"Energy class conversion skipped due to: {e}")
        else:
            uploaded_file = st.file_uploader("📤 Upload the energy consumption data file（Excel）", type=["xlsx"])
            if uploaded_file is not None:
                df = pd.read_excel(uploaded_file)
                st.session_state["df"] = df
                st.success("File uploaded successfully and stored in session.")
            elif "df" in st.session_state:
                df = st.session_state["df"]
                st.info("Using previously loaded dataset from session.")
            else:
                st.error("No data found. Please upload an Excel file or ensure the default path exists.")
                st.stop()

        # choose date
        st.markdown("#### 📅 Select Date Range")
        start_date = st.date_input("Start Date", datetime(2024, 1, 1))
        end_date = st.date_input("End Date", datetime(2024, 3, 31))

        # Energy type selection
        st.markdown("#### 🔍 Choose Energy Type")
        energy_filter = st.multiselect(
            "Select energy category",
            ["elec", "water", "steam", "gas"],
            default=["elec"]
        )

        # System type selection
        st.markdown("#### 🏭 Choose System Type")
        system_type = st.radio(
            "Select system category",
            ["all_equipments", "utility_system", "equipments"],
            index=0,
            horizontal=True
        )

        # Restriction logic: The workshop equipment can only be powered by electricity
        if system_type == "equipments" and any(e != "elec" for e in energy_filter):
            st.warning("Workshop equipments only support electricity — reset to 'elec'.")
            energy_filter = ["elec"]

        # choose equipment
        st.markdown("#### ⚡ Select Devices (Preview Area)")


        def update_selected_devices():
            """The callback function that is triggered automatically when multiselect changes"""
            if "device_selector" in st.session_state:
                st.session_state["selected_devices"] = st.session_state["device_selector"]


        if "df" in st.session_state:
            df = st.session_state["df"]
            df["time"] = pd.to_datetime(df["time"], errors="coerce")
            # Automatic identification of energy columns
            energy_cols = [col for col in df.columns if any(col.startswith(e) for e in energy_filter)]

            if energy_cols:
                # Initialization: Default values are provided when the page is first loaded.
                if "device_selector" not in st.session_state:
                    st.session_state["device_selector"] = energy_cols[:5]
                if "selected_devices" not in st.session_state:
                    st.session_state["selected_devices"] = energy_cols[:5]

                # Control Definition
                st.multiselect(
                    "Choose one or multiple devices:",
                    options=energy_cols,
                    default=st.session_state["device_selector"],
                    key="device_selector",
                    on_change=update_selected_devices,
                    help="Scroll to select devices; the right panel will update automatically."
                )

            else:
                st.info("No matching device columns found for selected energy type.")
        else:
            st.info("Please upload data first to choose devices.")

        # Aggregation cycle selection
        st.markdown("#### ⏱️ Select Aggregation Period")
        period = st.radio(
            "Aggregation period:",
            ["Daily", "Weekly", "Monthly"],
            horizontal=True,
            index=0,
            key="aggregation_period"
        )

        # Save the global state
        st.session_state["start_date"] = start_date
        st.session_state["end_date"] = end_date
        st.session_state["energy_filter"] = energy_filter
        st.session_state["system_type"] = system_type

        st.markdown("---")
        st.info("**Tip:** The system will automatically load the data file from your local directory if it exists.")

        # Export button
        if "df" in st.session_state:
            df = st.session_state["df"]
            # Filter time range
            df["time"] = pd.to_datetime(df["time"], errors="coerce")
            df = df[(df["time"].dt.date >= start_date) & (df["time"].dt.date <= end_date)]
            # Filter columns
            energy_cols = [col for col in df.columns if any(col.startswith(e) for e in energy_filter)]
            export_df = df[["time"] + energy_cols]

            if st.button("📁 Generate Export File", key="btn_export_excel"):
                export_df.to_excel("filtered_energy_data.xlsx", index=False)
                with open("filtered_energy_data.xlsx", "rb") as f:
                    st.download_button(
                        label="⬇️ Download Excel File",
                        data=f,
                        file_name="filtered_energy_data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
        else:
            st.warning("No data loaded yet. Please upload data in the main dashboard.")

        # Entry of the Process Optimization Subsystem
        st.markdown("---")
        st.markdown("### 🧩 Process Optimization Subsystem")

        st.info("""
        This subsystem allows workers to upload process schedules,  
        merge them for parallel execution, and calculate reduced public energy usage
        (Only considering the battery power because of the increased usage and higher price).
        """)

        if st.button("🚀 **Enter Process Scheduling Optimization System**", use_container_width=True):
            st.switch_page("pages/4_ProcessOptimization.py")

# ========== The right display area ==========
with right:
    # Load data from session_state first
    if "df" in st.session_state:
        df = st.session_state["df"]
    elif os.path.exists(DATA_PATH):
        df = pd.read_excel(DATA_PATH)
        st.session_state["df"] = df
        st.info(f"Loaded data automatically from {os.path.basename(DATA_PATH)}")
    else:
        st.error("No data available. Please upload a file or make sure the local file exists.")
        st.stop()

    # handle data
    df.rename(columns={df.columns[0]: "time"}, inplace=True)
    df["time"] = df["time"].apply(parse_time)

    # filter time
    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    df = df[(df["time"] >= start_ts) & (df["time"] <= end_ts)]

    # filter energy type
    prefixes = [e for e in ["elec", "water", "steam", "gas"] if e in energy_filter]
    energy_cols = [col for col in df.columns if any(col.startswith(p) for p in prefixes)]

    if not energy_cols:
        st.error("No matching energy columns found. Please check your Excel headers.")
        st.stop()

    # Daily energy consumption calculation (daily maximum value - minimum value)
    df["date"] = df["time"].dt.date
    daily_energy = df.groupby("date")[energy_cols].max() - df.groupby("date")[energy_cols].min()
    daily_energy["total_energy"] = daily_energy.sum(axis=1)

    # statistical index
    total_energy = daily_energy["total_energy"].sum()
    avg_daily = daily_energy["total_energy"].mean()
    sum_energy = daily_energy.drop(columns=["total_energy"]).sum().sort_values(ascending=False)
    top_equip = sum_energy.idxmax()
    top_val = sum_energy.max()
    top_name = equip_dic.get(top_equip, top_equip)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='card'><div class='small'>Total Energy Consumption</div>"
                    f"<div class='metric'>{total_energy:.1f}</div>"
                    f"<div class='small'>Unit: kWh or m³</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='card'><div class='small'>Average Daily Consumption</div>"
                    f"<div class='metric'>{avg_daily:.1f}</div>"
                    f"<div class='small'>Average within selected range</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='card'><div class='small'>Top Consuming Device</div>"
                    f"<div class='metric'>{top_name}</div>"
                    f"<div class='small'>Energy used: {top_val:.2f}</div></div>", unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### 📊 Visualization Overview")
    # ================= 左右两列主布局 =================
    col1, col2 = st.columns([1.2, 1])

    # Left side: Trend chart
    with col1:
        st.markdown("#### 📈 Daily Energy Trend (Preview)")

        fig1, ax1 = plt.subplots(figsize=(6, 2.2))
        ax1.plot(daily_energy.index, daily_energy.sum(axis=1), color="#1E88E5", linewidth=2)
        ax1.set_title("Daily Energy Trend (Preview)", fontsize=10, color="#003366")
        ax1.set_xlabel("")
        ax1.set_ylabel("")
        ax1.set_xticks([])
        ax1.set_yticks([])
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)
        ax1.spines["bottom"].set_visible(False)
        ax1.spines["left"].set_visible(False)
        ax1.grid(True, linestyle="--", alpha=0.25)

        st.pyplot(fig1, use_container_width=True)

    # ===== Right side: Energy Consumption Preview =====
    with col2:
        st.markdown("#### 📊 Energy Overview (Preview)")

        if isinstance(sum_energy, pd.DataFrame):
            sum_energy_plot = sum_energy["total_energy"].sort_values(ascending=False)
        else:
            sum_energy_plot = sum_energy.sort_values(ascending=False)

        top10 = sum_energy_plot.head(10)
        top5 = sum_energy_plot.head(5)

        # Two small graphs: bar chart + pie chart
        bar_col, pie_col = st.columns([1.2, 1])
        with bar_col:
            fig_bar, ax_bar = plt.subplots(figsize=(3.5, 2.2))
            top10.plot(kind="barh", color="#42A5F5", ax=ax_bar)
            ax_bar.invert_yaxis()
            ax_bar.set_title("Top Devices", fontsize=9, color="#003366")
            ax_bar.axis("off")
            st.pyplot(fig_bar, use_container_width=True)

        with pie_col:
            fig_pie, ax_pie = plt.subplots(figsize=(3, 2.2))
            ax_pie.pie(top5, labels=None, autopct=None, startangle=140, colors=plt.cm.Paired.colors)
            ax_pie.set_title("Energy Share", fontsize=9, color="#003366")
            st.pyplot(fig_pie, use_container_width=True)

    btn_col1, btn_col2 = st.columns([1.2, 1])

    with btn_col1:
        if st.button("📈 Click to view trend details", key="btn_trend"):
            st.switch_page("pages/1_EnergyTrend.py")

    with btn_col2:
        if st.button("📊 Click to view comparison details", key="btn_compare"):
            st.switch_page("pages/2_EnergyComparison.py")

    st.markdown("---")

    # On the right side, it shows the daily energy consumption trend of the equipment.
    st.markdown("#### ⚡ Device Daily Energy Trend (Preview)")

    if "df" not in st.session_state or "selected_devices" not in st.session_state:
        st.info("Please select one or more devices from the left sidebar first.")
    else:
        df = st.session_state["df"]
        selected_devices = st.session_state["selected_devices"]
        start_date = st.session_state.get("start_date")
        end_date = st.session_state.get("end_date")

        if selected_devices:
            df["time"] = pd.to_datetime(df["time"], errors="coerce")
            df["date"] = df["time"].dt.date
            df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
            # Calculate daily energy consumption
            daily_energy = df.groupby("date")[selected_devices].agg(lambda x: x.max() - x.min())

            preview_devices = selected_devices[:5]
            fig_device, ax_device = plt.subplots(figsize=(2.2, 1.4))
            daily_energy[preview_devices].plot(ax=ax_device, linewidth=0.3)
            ax_device.set_title("")
            ax_device.set_xlabel("")
            ax_device.set_ylabel("")
            ax_device.set_xticks([])
            ax_device.set_yticks([])
            ax_device.legend().set_visible(False)
            for spine in ax_device.spines.values():
                spine.set_visible(False)

            ax_device.grid(True, linestyle="--", alpha=0.25)
            st.pyplot(fig_device, use_container_width=False)

        else:
            st.info("No devices selected.")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption("View detailed daily energy trend for selected devices in a separate page.")
    with col2:
        if st.button("📈 Open Trend Page", key="btn_device_trend", use_container_width=True):
            st.switch_page("pages/3_DeviceEnergyTrend.py")

    # data preview
    st.subheader("📋 Data Preview")

    # Read the selection in the left sidebar from the session_state
    if "df" not in st.session_state:
        st.error("Please load dataset in the main dashboard first.")
        st.stop()

    df = st.session_state["df"]
    start_date = st.session_state.get("start_date")
    end_date = st.session_state.get("end_date")
    energy_filter = st.session_state.get("energy_filter", ["elec"])
    # filter time range
    df = filter_by_date(st.session_state.get("energy_data", st.session_state["df"]), start_date, end_date)

    # filter energy type
    energy_cols = [col for col in df.columns if any(col.startswith(e) for e in energy_filter)]
    if not energy_cols:
        st.warning("No matching energy columns found for current selection.")
        st.stop()

    # Select the aggregation period
    period = st.session_state.get("aggregation_period", "Daily")
    if period == "Daily":
        df["date"] = df["time"].dt.date
        df_grouped = df.groupby("date")[energy_cols].agg(lambda x: x.max() - x.min()).reset_index()
        df_grouped.rename(columns={"date": "Date"}, inplace=True)

    elif period == "Weekly":
        df["week_start"] = df["time"].dt.to_period("W").apply(lambda r: r.start_time.date())
        df_grouped = df.groupby("week_start")[energy_cols].agg(lambda x: x.max() - x.min()).reset_index()
        df_grouped.rename(columns={"week_start": "Week Start"}, inplace=True)

    else:  # Monthly
        df["month"] = df["time"].dt.to_period("M").apply(lambda r: r.start_time.date())
        df_grouped = df.groupby("month")[energy_cols].agg(lambda x: x.max() - x.min()).reset_index()
        df_grouped.rename(columns={"month": "Month"}, inplace=True)

    # display result
    st.markdown(f"**Period:** `{period}` | **Energy Type:** `{', '.join(energy_filter)}`")

    st.dataframe(df_grouped.head(15), use_container_width=True)
    st.caption(f"📊 Total {len(df_grouped)} {period.lower()} records × {len(df_grouped.columns)} columns")
