import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="CarbonTrack",
    page_icon="🌱",
    layout="wide"
)

# =========================================================
# SESSION STATE
# =========================================================
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(
        columns=[
            "Time",
            "Voltage",
            "Current",
            "Power",
            "Energy",
            "CO2"
        ]
    )

if "total_energy" not in st.session_state:
    st.session_state.total_energy = 0.0

if "total_co2" not in st.session_state:
    st.session_state.total_co2 = 0.0


# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("🌱 CarbonTrack")
st.sidebar.caption("IoT-Based Carbon Footprint Monitoring")

st.sidebar.header("System Settings")

mode = st.sidebar.selectbox(
    "Operating Mode",
    ["Simulation Mode", "IoT Mode"]
)

emission_factor = st.sidebar.number_input(
    "Emission Factor (kg CO₂e/kWh)",
    min_value=0.0,
    value=0.60,
    step=0.01
)

electricity_tariff = st.sidebar.number_input(
    "Electricity Tariff (RM/kWh)",
    min_value=0.0,
    value=0.50,
    step=0.01
)

carbon_target = st.sidebar.number_input(
    "Daily Carbon Target (kg CO₂e)",
    min_value=0.1,
    value=10.0,
    step=0.5
)

refresh_interval = st.sidebar.slider(
    "Refresh Interval (seconds)",
    1,
    10,
    3
)

st.sidebar.divider()

if st.sidebar.button("Reset Monitoring Data"):
    st.session_state.history = st.session_state.history.iloc[0:0]
    st.session_state.total_energy = 0.0
    st.session_state.total_co2 = 0.0
    st.rerun()


# =========================================================
# SENSOR SIMULATION
# =========================================================
def simulate_sensor():

    voltage = np.random.normal(240, 2)

    current = np.random.uniform(0.5, 8.0)

    power_factor = np.random.uniform(0.85, 0.98)

    power = voltage * current * power_factor

    return voltage, current, power


# =========================================================
# HEADER
# =========================================================
st.title("🌱 CarbonTrack")

st.subheader(
    "IoT-Based Real-Time Carbon Footprint Monitoring Dashboard"
)

st.caption(
    "Real-time monitoring of electricity consumption and "
    "estimated carbon emissions"
)

st.divider()


# =========================================================
# DATA ACQUISITION
# =========================================================
if mode == "Simulation Mode":

    voltage, current, power = simulate_sensor()

else:

    # -----------------------------------------------------
    # Replace these values with MQTT / Firebase / ESP32 data
    # -----------------------------------------------------

    voltage = 240.0
    current = 2.5

    power = voltage * current

    st.info(
        "IoT Mode selected. Replace the placeholder values "
        "with ESP32/MQTT/Firebase sensor readings."
    )


# =========================================================
# ENERGY CALCULATION
# =========================================================

# Power is measured in Watts.
# Energy = Power × time

energy_increment = (
    power / 1000
) * (
    refresh_interval / 3600
)

st.session_state.total_energy += energy_increment


# =========================================================
# CARBON CALCULATION
# =========================================================

co2_increment = energy_increment * emission_factor

st.session_state.total_co2 += co2_increment


# =========================================================
# COST CALCULATION
# =========================================================

electricity_cost = (
    st.session_state.total_energy *
    electricity_tariff
)


# =========================================================
# STORE DATA
# =========================================================

new_record = pd.DataFrame({
    "Time": [datetime.now()],
    "Voltage": [voltage],
    "Current": [current],
    "Power": [power],
    "Energy": [st.session_state.total_energy],
    "CO2": [st.session_state.total_co2]
})

st.session_state.history = pd.concat(
    [
        st.session_state.history,
        new_record
    ],
    ignore_index=True
)


# =========================================================
# KPI DASHBOARD
# =========================================================

st.subheader("⚡ Real-Time Monitoring")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Voltage",
    f"{voltage:.1f} V"
)

col2.metric(
    "Current",
    f"{current:.2f} A"
)

col3.metric(
    "Power",
    f"{power:.0f} W"
)


col4, col5, col6 = st.columns(3)

col4.metric(
    "Energy Consumption",
    f"{st.session_state.total_energy:.4f} kWh"
)

col5.metric(
    "Carbon Emissions",
    f"{st.session_state.total_co2:.4f} kg CO₂e"
)

col6.metric(
    "Estimated Cost",
    f"RM {electricity_cost:.4f}"
)


st.divider()


# =========================================================
# CARBON STATUS
# =========================================================

st.subheader("🌍 Carbon Emission Status")

carbon_percentage = (
    st.session_state.total_co2 /
    carbon_target
) * 100

carbon_percentage = min(
    carbon_percentage,
    100
)

st.progress(
    carbon_percentage / 100
)

st.write(
    f"Carbon target used: "
    f"{st.session_state.total_co2:.3f} / "
    f"{carbon_target:.2f} kg CO₂e"
)


if carbon_percentage < 50:

    st.success(
        "🟢 Carbon emissions are currently LOW."
    )

elif carbon_percentage < 80:

    st.warning(
        "🟡 Carbon emissions are MODERATE."
    )

else:

    st.error(
        "🔴 High carbon emissions detected!"
    )


# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📊 Energy Analytics",
        "🌱 Carbon Analytics",
        "📋 Historical Data",
        "📈 Sustainability"
    ]
)


# =========================================================
# ENERGY ANALYTICS
# =========================================================

with tab1:

    st.subheader(
        "Real-Time Power Consumption"
    )

    if len(st.session_state.history) > 1:

        power_chart = (
            st.session_state.history[
                ["Time", "Power"]
            ]
            .set_index("Time")
        )

        st.line_chart(
            power_chart
        )

    else:

        st.info(
            "Waiting for additional sensor data..."
        )


    st.subheader(
        "Energy Consumption"
    )

    if len(st.session_state.history) > 1:

        energy_chart = (
            st.session_state.history[
                ["Time", "Energy"]
            ]
            .set_index("Time")
        )

        st.area_chart(
            energy_chart
        )


# =========================================================
# CARBON ANALYTICS
# =========================================================

with tab2:

    st.subheader(
        "Carbon Emission Trend"
    )

    if len(st.session_state.history) > 1:

        carbon_chart = (
            st.session_state.history[
                ["Time", "CO2"]
            ]
            .set_index("Time")
        )

        st.line_chart(
            carbon_chart
        )


    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Total CO₂e",
            f"{st.session_state.total_co2:.4f} kg"
        )

    with col2:

        carbon_rate = (
            power / 1000
        ) * emission_factor

        st.metric(
            "Current Carbon Rate",
            f"{carbon_rate:.3f} kg CO₂e/hour"
        )


# =========================================================
# HISTORICAL DATA
# =========================================================

with tab3:

    st.subheader(
        "Monitoring Records"
    )

    display_data = (
        st.session_state.history.copy()
    )

    display_data["Voltage"] = (
        display_data["Voltage"]
        .astype(float)
        .round(2)
    )

    display_data["Current"] = (
        display_data["Current"]
        .astype(float)
        .round(3)
    )

    display_data["Power"] = (
        display_data["Power"]
        .astype(float)
        .round(2)
    )

    display_data["Energy"] = (
        display_data["Energy"]
        .astype(float)
        .round(5)
    )

    display_data["CO2"] = (
        display_data["CO2"]
        .astype(float)
        .round(5)
    )

    st.dataframe(
        display_data,
        use_container_width=True
    )


    csv = display_data.to_csv(
        index=False
    ).encode("utf-8")


    st.download_button(
        label="📥 Download CSV Report",
        data=csv,
        file_name="carbontrack_data.csv",
        mime="text/csv"
    )


# =========================================================
# SUSTAINABILITY ANALYSIS
# =========================================================

with tab4:

    st.subheader(
        "🌿 Sustainability Indicators"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Energy Used",
        f"{st.session_state.total_energy:.3f} kWh"
    )

    col2.metric(
        "CO₂ Generated",
        f"{st.session_state.total_co2:.3f} kg"
    )

    col3.metric(
        "Target",
        f"{carbon_target:.1f} kg"
    )


    st.subheader(
        "Carbon Reduction Recommendations"
    )

    if power > 1500:

        st.warning(
            "⚠️ High electrical demand detected."
        )

        st.write(
            """
            Recommendations:

            • Switch off unnecessary electrical equipment  
            • Reduce simultaneous high-power loads  
            • Improve appliance energy efficiency  
            • Consider renewable energy integration  
            • Investigate abnormal energy consumption
            """
        )

    elif power > 800:

        st.info(
            "Energy consumption is moderate."
        )

        st.write(
            """
            Consider reducing unnecessary electrical loads
            to further lower carbon emissions.
            """
        )

    else:

        st.success(
            "Energy consumption is currently efficient."
        )


# =========================================================
# SYSTEM INFORMATION
# =========================================================

st.divider()

with st.expander(
    "ℹ️ About CarbonTrack"
):

    st.write(
        """
        **CarbonTrack** is an IoT-based monitoring platform
        designed to estimate the carbon footprint associated
        with electrical energy consumption.

        The proposed IoT architecture is:

        **Electrical Load → Energy Sensor → ESP32 → Wi-Fi →
        MQTT/Cloud → Streamlit Dashboard**

        Carbon emissions are estimated using:

        CO₂e = Energy Consumption × Emission Factor

        The emission factor should be configured according
        to the electricity grid and reporting methodology
        applicable to the deployment location.
        """
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "CarbonTrack | IoT-Based Real-Time Carbon Footprint "
    "Monitoring System"
)


# =========================================================
# AUTO REFRESH
# =========================================================

time.sleep(refresh_interval)

st.rerun()
