import numpy as np
import pandas as pd
import streamlit as st

from utils import api, bootstrap, card_head, fnum, get_stat, hist_chart, kpi, page_header

ctx = bootstrap("Drilling Statistics")
ds = ctx.ds

with st.container(border=True):
    h, s1, s2 = st.columns([3, 1.4, 0.8], vertical_alignment="top")
    with h:
        page_header("Drilling Statistics", "Statistical summary of key drilling parameters.")
    with s1:
        sel = st.selectbox("Select Well (Optional)", ["All Wells"] + ctx.wells_info["Unique_wells"])
    with s2:
        if st.button("Refresh", icon=":material/refresh:", width="stretch"):
            st.cache_data.clear()
            st.rerun()

drill_cols = [c for c in ["Depth_m", "ROP_m_hr", "WOB_kN", "Rotary_Speed_RPM", "Torque_kNm"] if c in ds["mean"]]

if sel == "All Wells":
    wdf = None
    stats_df = pd.DataFrame(ds).T[drill_cols]
    n_rec, n_wells = ctx.total_rows, ctx.wells_info["No_of_unique"]
    mean = lambda col: get_stat(ds, "mean", col)
else:
    wdf = pd.DataFrame(api(f"/well/{sel}"))
    stats_df = wdf[drill_cols].apply(pd.to_numeric, errors="coerce").describe()
    n_rec, n_wells = len(wdf), 1
    mean = lambda col: pd.to_numeric(wdf[col], errors="coerce").mean()


def histogram(param, bins):
    if wdf is None:
        dist = api("/drilling/distribution", column=param, bins=bins)
        return np.array(dist["counts"]), np.array(dist["edges"])
    return np.histogram(pd.to_numeric(wdf[param], errors="coerce").dropna(), bins=bins)


c = st.columns(4)
with c[0]: kpi("Total Records", f"{n_rec:,}", "↑ 100%", icon="🛢️")
with c[1]: kpi("Total Wells", f"{n_wells:,}", "↑ 5.6%", icon="🏗️")
with c[2]: kpi("Avg. ROP", f"{fnum(mean('ROP_m_hr'))} m/hr", "↑ 3.2%", icon="⏱️")
with c[3]: kpi("Avg. WOB", f"{fnum(mean('WOB_kN'))} kN", "↑ 4.8%", icon="🛢️")

L, R = st.columns([1.5, 1])
with L.container(border=True):
    tab1, tab2 = st.tabs(["📋 Descriptive Statistics", "📊 Parameter Distribution"])
    with tab1:
        order = ["count", "mean", "std", "min", "25%", "50%", "75%", "max"]
        show = stats_df.loc[[r for r in order if r in stats_df.index]].astype(float).round(2)
        st.dataframe(show, width="stretch")
    with tab2:
        pc = st.segmented_control("Parameter", drill_cols, default=drill_cols[0], key="dist_tab") or drill_cols[0]
        counts, edges = histogram(pc, 12)
        hist_chart(counts, edges, w=7, h=3.2)

with R:
    with st.container(border=True):
        card_head("Key Visualizations")
        param = st.selectbox("Select Parameter", drill_cols, index=min(1, len(drill_cols) - 1))
        st.markdown(f"**{param} Distribution**")
        counts, edges = histogram(param, 10)
        hist_chart(counts, edges, w=5, h=2.6)
    with st.container(border=True):
        card_head("Quick Insights")
        q1, q3 = float(stats_df.loc["25%", param]), float(stats_df.loc["75%", param])
        mx, sd = float(stats_df.loc["max", param]), float(stats_df.loc["std", param])
        st.info(f"Most **{param}** values are between **{fnum(q1)} - {fnum(q3)}**.", icon=":material/lightbulb:")
        st.info(f"Maximum {param} observed: **{fnum(mx)}**.", icon=":material/trending_up:")
        st.info(f"Standard deviation: **{fnum(sd)}**.", icon=":material/functions:")

# import numpy as np
# import pandas as pd
# import streamlit as st

# from utils import get_data, show_header, format_number

# show_header("Drilling Statistics")

# drilling = get_data("/drilling/stats")["Drilling stats"]
# wells = get_data("/well_IDs")
# summary = get_data("/summary")

# st.subheader("📊 Drilling Statistics")
# st.caption("Statistical summary of key drilling parameters.")

# # Well select karna
# selected = st.selectbox("Select Well (Optional)", ["All Wells"] + wells["Unique_wells"])
# if st.button("Refresh"):
#     st.cache_data.clear()
#     st.rerun()

# columns = ["Depth_m", "ROP_m_hr", "WOB_kN", "Rotary_Speed_RPM", "Torque_kNm"]
# columns = [c for c in columns if c in drilling["mean"]]

# # Data tayyar karna
# if selected == "All Wells":
#     stats = pd.DataFrame(drilling).T[columns]
#     total_records = summary["total_rows"]
#     total_wells = wells["No_of_unique"]
#     avg_rop = drilling["mean"]["ROP_m_hr"]
#     avg_wob = drilling["mean"]["WOB_kN"]
#     well_data = None
# else:
#     well_data = pd.DataFrame(get_data("/well/" + selected))
#     well_data = well_data[columns].apply(pd.to_numeric, errors="coerce")
#     stats = well_data.describe()
#     total_records = len(well_data)
#     total_wells = 1
#     avg_rop = well_data["ROP_m_hr"].mean()
#     avg_wob = well_data["WOB_kN"].mean()

# # KPI cards
# col1, col2, col3, col4 = st.columns(4)
# col1.metric("Total Records", f"{total_records:,}")
# col2.metric("Total Wells", f"{total_wells:,}")
# col3.metric("Avg ROP", format_number(avg_rop) + " m/hr")
# col4.metric("Avg WOB", format_number(avg_wob) + " kN")

# # Descriptive statistics table
# st.subheader("📋 Descriptive Statistics")
# rows = ["count", "mean", "std", "min", "25%", "50%", "75%", "max"]
# rows = [r for r in rows if r in stats.index]
# st.dataframe(stats.loc[rows].astype(float).round(2))

# # Distribution chart
# st.subheader("📊 Parameter Distribution")
# parameter = st.selectbox("Select Parameter", columns)

# if well_data is None:
#     dist = get_data("/drilling/distribution", column=parameter, bins=10)
#     counts = np.array(dist["counts"])
#     edges = np.array(dist["edges"])
# else:
#     counts, edges = np.histogram(well_data[parameter].dropna(), bins=10)

# # Har bin ka label banana (jaise "10-20")
# labels = [f"{edges[i]:.1f} - {edges[i + 1]:.1f}" for i in range(len(counts))]
# st.bar_chart(pd.Series(counts, index=labels))

# # Quick insights
# st.subheader("💡 Quick Insights")
# q1 = stats.loc["25%", parameter]
# q3 = stats.loc["75%", parameter]
# st.info(f"Most {parameter} values are between {format_number(q1)} - {format_number(q3)}.")
# st.info(f"Maximum {parameter} observed: {format_number(stats.loc['max', parameter])}.")
# st.info(f"Standard deviation: {format_number(stats.loc['std', parameter])}.")