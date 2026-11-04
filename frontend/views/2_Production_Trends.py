import pandas as pd
import streamlit as st

from utils import BLUE, ORANGE, api, bootstrap, card_head, daily_df, fnum, kpi, page_header, trend_chart

ctx = bootstrap("Production Trends")
opts = ctx.opts

d_min = pd.to_datetime(opts["date_min"]).date() if opts["date_min"] else None
d_max = pd.to_datetime(opts["date_max"]).date() if opts["date_max"] else None

page_header("Production Trends", "Oil & Gas production over time and field comparison.")

with st.container(border=True):
    f1, f2, f3, f4, f5 = st.columns([1, 1, 1, 1, 0.7], vertical_alignment="bottom")
    start = f1.date_input("Start Date", d_min, key="pt_start")
    end = f2.date_input("End Date", d_max, key="pt_end")
    field = f3.selectbox("Field", ["All Fields"] + opts["fields"], key="pt_field")
    well = f4.selectbox("Well ID", ["All Wells"] + opts["well_ids"], key="pt_well")
    f5.button("Apply", icon=":material/filter_alt:", width="stretch")

flt = dict(
    field_id=None if field == "All Fields" else field,
    well_id=None if well == "All Wells" else well,
    start=str(start) if start else None,
    end=str(end) if end else None,
)
byf = api("/production/by-field", **flt)
ov = byf["overall"]
d = daily_df(**flt)
oil_spark = d["oil"].tolist() if not d.empty else None
gas_spark = d["gas"].tolist() if not d.empty else None

c = st.columns(4)
with c[0]: kpi("Total Oil (bpd)", f"{ov['oil_total']:,.0f}", "↑ 6.8%", icon="🛢️", spark=oil_spark)
with c[1]: kpi("Total Gas (Mcf/d)", f"{ov['gas_total']:,.0f}", "↑ 5.2%", icon="🔥", spark=gas_spark)
with c[2]: kpi("Avg. Oil Rate (bpd)", f"{fnum(ov['oil_avg'])}", "↑ 4.1%", icon="📈", spark=oil_spark)
with c[3]: kpi("Avg. Gas Rate (Mcf/d)", f"{fnum(ov['gas_avg'])}", "↑ 3.7%", icon="📉", spark=gas_spark)

L, R = st.columns([1.8, 1])
with L.container(border=True):
    card_head("📈 Production Trend (All Wells)" if well == "All Wells" else f"📈 Production Trend ({well})",
              "Oil & Gas rates over the selected period")
    trend_chart(d, height=320)

with R.container(border=True):
    card_head("Production by Field", "Average rate per field")
    bf = pd.DataFrame(byf["fields"])
    if not bf.empty:
        chart = bf.set_index("Field_ID")[["oil_avg", "gas_avg"]].rename(
            columns={"oil_avg": "Oil (bpd)", "gas_avg": "Gas (Mscf/d)"})
        st.bar_chart(chart, color=[BLUE, ORANGE], stack=False, height=320)
    else:
        st.info("No Data Found.")

T, F = st.columns([3, 1])
with T.container(border=True):
    card_head("🗓️ Recent Production Data", "Latest records for the current selection")
    rec = pd.DataFrame(api("/production/recent", limit=8, **flt)["records"])
    if not rec.empty:
        st.dataframe(
            pd.DataFrame({
                "Date": pd.to_datetime(rec["Timestamp"]).dt.date,
                "Well ID": rec["Well_ID"],
                "Field ID": rec.get("Field_ID"),
                "Oil Rate (bpd)": rec["Oil_Rate_bpd"],
                "Gas Rate (Mscf/d)": rec["Gas_Rate_Mscf_d"],
                "ROP (m/hr)": rec["ROP_m_hr"],
            }),
            hide_index=True, width="stretch",
            column_config={
                "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                "Oil Rate (bpd)": st.column_config.NumberColumn(format="%.2f"),
                "Gas Rate (Mscf/d)": st.column_config.NumberColumn(format="%.2f"),
                "ROP (m/hr)": st.column_config.NumberColumn(format="%.2f"),
            },
        )

with F.container(border=True):
    card_head("🔎 Active Filters", "Current selection")
    st.markdown(f"**Field:** {field}  \n**Well ID:** {well}  \n**Range:** {start} → {end}")

    def _reset():
        for k, v in {"pt_field": "All Fields", "pt_well": "All Wells", "pt_start": d_min, "pt_end": d_max}.items():
            st.session_state[k] = v

    st.button("Reset Filters", icon=":material/restart_alt:", on_click=_reset, width="stretch")



# import pandas as pd
# import streamlit as st

# from utils import get_data, show_header, format_number, get_daily_data, show_trend_chart

# show_header("Production Trends")

# options = get_data("/filters/options")

# st.subheader("📈 Production Trends")
# st.caption("Oil & Gas production over time and field comparison.")

# # Default dates
# date_min = pd.to_datetime(options["date_min"]).date() if options["date_min"] else None
# date_max = pd.to_datetime(options["date_max"]).date() if options["date_max"] else None

# # Filters
# col1, col2, col3, col4 = st.columns(4)
# start = col1.date_input("Start Date", date_min)
# end = col2.date_input("End Date", date_max)
# field = col3.selectbox("Field", ["All Fields"] + options["fields"])
# well = col4.selectbox("Well ID", ["All Wells"] + options["well_ids"])

# filters = {
#     "field_id": None if field == "All Fields" else field,
#     "well_id": None if well == "All Wells" else well,
#     "start": str(start) if start else None,
#     "end": str(end) if end else None,
# }

# by_field = get_data("/production/by-field", **filters)
# overall = by_field["overall"]

# # KPI cards
# col1, col2, col3, col4 = st.columns(4)
# col1.metric("Total Oil (bpd)", f"{overall['oil_total']:,.0f}")
# col2.metric("Total Gas (Mcf/d)", f"{overall['gas_total']:,.0f}")
# col3.metric("Avg Oil Rate (bpd)", format_number(overall["oil_avg"]))
# col4.metric("Avg Gas Rate (Mcf/d)", format_number(overall["gas_avg"]))

# # Trend chart
# st.subheader("Production Trend")
# daily = get_daily_data(**filters)
# show_trend_chart(daily)

# # Field comparison
# st.subheader("Production by Field")
# fields = pd.DataFrame(by_field["fields"])
# if not fields.empty:
#     chart = fields.set_index("Field_ID")[["oil_avg", "gas_avg"]]
#     chart = chart.rename(columns={"oil_avg": "Oil (bpd)", "gas_avg": "Gas (Mscf/d)"})
#     st.bar_chart(chart)
# else:
#     st.info("Is selection ke liye data nahi mila.")

# # Recent data
# st.subheader("🗓️ Recent Production Data")
# recent = pd.DataFrame(get_data("/production/recent", limit=8, **filters)["records"])
# if not recent.empty:
#     table = pd.DataFrame({
#         "Date": pd.to_datetime(recent["Timestamp"]).dt.date,
#         "Well ID": recent["Well_ID"],
#         "Field ID": recent["Field_ID"],
#         "Oil Rate (bpd)": recent["Oil_Rate_bpd"],
#         "Gas Rate (Mscf/d)": recent["Gas_Rate_Mscf_d"],
#         "ROP (m/hr)": recent["ROP_m_hr"],
#     })
#     st.dataframe(table, hide_index=True)