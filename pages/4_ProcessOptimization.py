import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date

from config_equipment import utility_system, equipments
from models_energy import Process

def _parse_equips(equip_str):
    """Parse the device field into a list"""
    if not equip_str or str(equip_str).strip() == "":
        return ["<Unnamed device>"]
    parts = [p.strip() for p in str(equip_str).replace("，", ",").split(",") if p.strip()]
    return parts or ["<Unnamed device>"]

def _merged_total_hours(intervals):
    """Total duration of the union"""
    if not intervals:
        return 0.0
    ivs = sorted(intervals, key=lambda x: x[0])
    merged = []
    cs, ce = ivs[0]
    for s, e in ivs[1:]:
        if s <= ce:
            ce = max(ce, e)
        else:
            merged.append((cs, ce))
            cs, ce = s, e
    merged.append((cs, ce))
    return sum((e - s).total_seconds() / 3600 for s, e in merged)

def compute_parallel_saving_by_day(processes, energy_df, utility_cols):
    """
    - Parallel duration: The union length of all process time periods within a day (ignoring equipment constraints)
    - Fully parallel duration: When the same equipment cannot be concurrently operated → Add up the process durations of each equipment for the day; Optimized duration = The maximum value of the total durations of all equipment
    - Energy saving rate = 1 - (Fully parallel / Original parallel)
    - Utility system energy consumption: Cumulate (maximum - minimum) by da
    """
    if energy_df is None or energy_df.empty:
        return pd.DataFrame(), 0.0
    if not utility_cols:
        return pd.DataFrame(), 0.0

    df = energy_df.copy()
    if "time" not in df.columns:
        df.rename(columns={df.columns[0]: "time"}, inplace=True)
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    df["date"] = df["time"].dt.date

    by_day = {}
    for p in processes:
        if not hasattr(p, "start_time") or not hasattr(p, "end_time"):
            continue
        if p.start_time is None or p.end_time is None:
            continue
        d = p.process_date if isinstance(p.process_date, date) else getattr(p.process_date, "date", lambda: None)()
        if d is None:
            getattr(p.start_time, "date", lambda: None)()
        if d is None:
            continue
        by_day.setdefault(d, []).append(p)

    results, total_saving = [], 0.0

    for d, plist in by_day.items():
        if not plist:
            continue

        intervals = []
        for p in plist:
            s = pd.to_datetime(p.start_time, errors="coerce")
            e = pd.to_datetime(p.end_time, errors="coerce")
            if pd.isna(s) or pd.isna(e) or e <= s:
                continue
            intervals.append((s, e))
        if not intervals:
            continue
        original_hours = _merged_total_hours(intervals)

        # Fully Parallel: Devices with the same name cannot run concurrently → Calculate the total duration for each device and take the maximum value
        # Note: If a process uses multiple devices, its duration should be included in the total duration of each device
        equip_total_hours = {}
        for p in plist:
            s = pd.to_datetime(p.start_time, errors="coerce")
            e = pd.to_datetime(p.end_time, errors="coerce")
            if pd.isna(s) or pd.isna(e) or e <= s:
                continue
            dur_h = (e - s).total_seconds() / 3600
            for equip in _parse_equips(getattr(p, "equipments", "")):
                equip_total_hours[equip] = equip_total_hours.get(equip, 0.0) + dur_h
        optimized_hours = max(equip_total_hours.values()) if equip_total_hours else 0.0

        day_df = df[df["date"] == d]
        if day_df.empty:
            continue

        cols_utility = [c for c in utility_cols if c in day_df.columns]
        if not cols_utility:
            continue

        day_use_utility = day_df.groupby("date")[cols_utility].max() - day_df.groupby("date")[cols_utility].min()
        public_kwh = float(day_use_utility.sum(axis=1).iloc[0]) if not day_use_utility.empty else 0.0

        # Total plant energy consumption
        all_cols = [c for c in day_df.columns if any(c.startswith(e) for e in ["elec"])]
        day_use_total = day_df.groupby("date")[all_cols].max() - day_df.groupby("date")[all_cols].min() if all_cols else pd.DataFrame()
        total_kwh = float(day_use_total.sum(axis=1).iloc[0]) if not day_use_total.empty else 0.0

        # Energy-saving conversion
        if original_hours > 0:
            ratio = max(0.0, 1.0 - optimized_hours / original_hours)
            saving_kwh = public_kwh * ratio
            optimized_kwh = public_kwh - saving_kwh
        else:
            ratio, saving_kwh, optimized_kwh = 0.0, 0.0, public_kwh

        total_saving += saving_kwh
        public_ratio = (public_kwh / total_kwh * 100.0) if total_kwh > 0 else 0.0

        # record
        results.append({
            "date": d,
            "Original parallel duration(h)": round(original_hours, 2),
            "Total parallel duration(h)": round(optimized_hours, 2),
            "Total parallel duration(%)": round(ratio * 100.0, 2),
            "Energy consumption of public system(kWh)": round(public_kwh, 2),
            "Total plant energy consumption(kWh)": round(total_kwh, 2),
            "The proportion of public systems(%)": round(public_ratio, 2),
            "Save electricity(kWh)": round(saving_kwh, 2),
            "Optimized expected energy consumption(kWh)": round(optimized_kwh, 2)
        })

    return pd.DataFrame(results), float(total_saving)


# New process entry (form) - All keys must be unique
# ===== 页面标题 =====
st.markdown("## ✏️ Add New Process Record")

product_process_map = {
    "ganoderma lucidum spore powder": ["sieving", "inner packing", "external packing", "Linked packaging"],
    "Ironwood Maple Bark Granules": ["weigh-batching hopper", "One-step granulation", "inner packing", "external packing", "Linked packaging"],
    "American Ginseng Granules": ["weigh-batching hopper", "One-step granulation", "inner packing", "external packing", "Linked packaging"],
    "Ganoderma lucidum spore powder capsule": ["weigh-batching hopper", "One-step granulation", "Capsule filling", "inner packing", "external packing", "Linked packaging"],
    "Ganoderma lucidum spore powder tablets": ["weigh-batching hopper", "wet granulation", "tabletting", "lagging cover", "inner packing", "external packing", "Linked packaging"]
}

col_a, col_b = st.columns(2)
with col_a:
    product_type = st.selectbox(
        "product name",
        list(product_process_map.keys()),
        key="select_product_type"
    )

with col_b:
    process_options = product_process_map[product_type]
    process_name = st.selectbox(
        "process name",
        process_options,
        key=f"select_process_{product_type}"
    )

# form :other choice
with st.form("add_process_form", clear_on_submit=True):
    st.write("### 🧾 Fill in Process Details")

    col1, col2, col3 = st.columns(3)

    with col1:
        process_date = st.date_input("process date", value=date(2024, 1, 4), key="inp_process_date")
        size = st.text_input("specification", placeholder="2*15*16", key="inp_size")
        number = st.number_input("batch number", min_value=1, step=1, key="inp_number")

    with col2:
        investnumber = st.number_input("input", min_value=0.0, step=0.1, key="inp_invest")
        worker_number = st.number_input("Number of positions", min_value=1, step=1, key="inp_workers")
        pronumber = st.number_input("production quantity", min_value=0.0, step=0.1, key="inp_output")

    with col3:
        # Automatically list all device options
        device_options = sorted(list(set(utility_system + equipments)))
        equip_selected = st.selectbox(
            "equipment number",
            options=device_options,
            index=0,
            key="select_equips",
            help="Please select the equipment corresponding to this process."
        )

    start_time = st.time_input("start time", value=datetime.strptime("08:00", "%H:%M").time(), key="inp_start")
    end_time = st.time_input("end time", value=datetime.strptime("17:00", "%H:%M").time(), key="inp_end")

    submitted = st.form_submit_button("✅ add process", key="btn_add_process")

    if submitted:
        # Calculate the duration of the process
        start_dt = datetime.combine(process_date, start_time)
        end_dt = datetime.combine(process_date, end_time)
        duration = (end_dt - start_dt).total_seconds() / 3600

        # Create a Process instance and temporarily store the session
        process = Process(
            process_date=process_date,
            product_type=product_type,
            process_name=process_name,
            size=size,
            number=number,
            investnumber=investnumber,
            worker_number=worker_number,
            pronumber=pronumber,
            start_time=start_dt,
            end_time=end_dt,
            equipments=equip_selected,
            process_time=duration
        )

        st.session_state.setdefault("processes", [])
        st.session_state["processes"].append(process)
        st.success(
            f"process【{process_name}】have been added！\n\n"
            f"date：{process_date} | time：{duration:.2f} h | equipment：{equip_selected}"
        )


# Current process schedule
st.markdown("### 📋 Current Process List")
if st.session_state.get("processes"):
    data = [{
        "Process Date": p.process_date.strftime("%Y-%m-%d"),
        "Process Name": p.process_name,
        "Product name": p.product_type,
        "size": p.size,
        "batch number": p.number,
        "input": p.investnumber,
        "Number of positions": p.worker_number,
        "production quantity": p.pronumber,
        "start time": p.start_time.strftime("%H:%M"),
        "end time": p.end_time.strftime("%H:%M"),
        "equipment": p.equipments,
        "time(h)": round(p.process_time, 2)
    } for p in st.session_state["processes"]]

    df_process = pd.DataFrame(data)
    st.dataframe(df_process, use_container_width=True)

    delete_index = st.number_input("🗑️ Enter the sequence number of the process to be deleted (starting from 1)", min_value=0, step=1, key="inp_del_idx")
    if st.button("Delete Process", key="btn_delete_process"):
        if 0 < delete_index <= len(st.session_state["processes"]):
            deleted = st.session_state["processes"].pop(delete_index - 1)
            st.warning(f"Deleted process【{deleted.process_name}】")
        else:
            st.info("Please enter the correct number")
else:
    st.info("The process has not been entered yet. Please fill in the information above")

# Process optimization scheduling + Energy-saving analysis
if st.session_state.get("processes"):
    st.markdown("### ⚙️ Optimization Result")

    if st.button("🚀 Start optimizing the scheduling", key="btn_run_opt"):
        processes = sorted(st.session_state["processes"], key=lambda p: p.start_time)

        # ===== nergy-saving analysis of public systems(important!)
        energy_df = st.session_state.get("df", None)
        df_saving, total_saving_kwh = compute_parallel_saving_by_day(
            processes,
            energy_df,
            utility_system
        )

        # Original parallel duration: Union; Optimized: Maximum total duration of devices (same names cannot be parallel)
        if not df_saving.empty:
            total_original = df_saving["Original parallel duration(h)"].sum()
            total_optimized = df_saving["Total parallel duration(h)"].sum()
            total_ratio = (1 - total_optimized / total_original) * 100 if total_original > 0 else 0

            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Original parallel duration (h)", f"{total_original:.2f}")
            with c2:
                st.metric("Total parallel duration (h)", f"{total_optimized:.2f}")
            with c3:
                st.metric("time saving (%)", f"{total_ratio:.1f}%")

            st.markdown("### Energy-saving Analysis of Public Systems (by Day)")
            st.dataframe(df_saving, use_container_width=True)
            st.success(f"Estimate the total energy savings: {total_saving_kwh:.2f} kWh")

            # Gantt Chart: Fully Parallel
            st.markdown("### 📊 Gantt Chart —  Fully Parallel")
            start_min = min(p.start_time for p in processes)
            # Calculate the total duration of each device for this day
            day = df_saving.iloc[0]["date"]
            plist_day = [p for p in processes if (p.process_date if isinstance(p.process_date, date) else p.process_date.date()) == day]
            equip_hours = {}
            for p in plist_day:
                dur_h = (pd.to_datetime(p.end_time) - pd.to_datetime(p.start_time)).total_seconds() / 3600
                for eq in _parse_equips(getattr(p, "equipments", "")):
                    equip_hours[eq] = equip_hours.get(eq, 0.0) + dur_h

            df_parallel = pd.DataFrame([{
                "Task": f"equipment：{eq}",
                "Start": start_min,
                "Finish": start_min + pd.to_timedelta(h, unit="h"),
                "Type": "Fully parallel"
            } for eq, h in equip_hours.items()])

            if not df_parallel.empty:
                fig2 = px.timeline(df_parallel, x_start="Start", x_end="Finish", y="Task", color="Type")
                fig2.update_yaxes(autorange="reversed")
                fig2.update_layout(height=420, xaxis_title="time", yaxis_title="Equipment (same equipment cannot be used concurrently)")
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("There are no visible equipment loads available for viewing on that day")
        else:
            st.warning("Unable to match the energy consumption data of the public system or there are no valid processes on that day")
