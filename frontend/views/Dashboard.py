import pandas as pd
import streamlit as st

from utils import (BLUE, GREEN, ORANGE, PAGE_FILES, api, bootstrap, card_head, daily_df, donut, fnum,
                   get_stat, hbar_chart, info_rows, kpi, page_header, trend_chart)

ctx = bootstrap("Well Performance Analysis and Production Forecasting")
ds, pstats = ctx.ds, ctx.pstats

page_header("Dashboard", "Overview of key metrics and recent data.")

d = daily_df()

c = st.columns(4)
with c[0]: kpi("Total Records", f"{ctx.total_rows:,}", "↑ 100%", icon="🛢️")
with c[1]: kpi("Unique Wells", f"{ctx.wells_info['No_of_unique']:,}", "↑ 5.6%", icon="🏗️")
with c[2]: kpi("Average ROP", f"{fnum(get_stat(ds, 'mean', 'ROP_m_hr'))} m/hr", "↑ 3.2%", icon="⏱️")
with c[3]: kpi("Average Oil Rate", f"{fnum(pstats['avg_oil'])} bpd", "↑ 6.8%", icon="🛢️")

left, right = st.columns([1.7, 1])
with left.container(border=True):
    card_head("📈 Production Trend", "Oil & Gas production over time")
    trend_chart(d, height=300)

with right.container(border=True):
    card_head("🥧 Production Distribution", "Oil vs Gas production share")
    oil, gas = pstats["avg_oil"] or 0, pstats["avg_gas"] or 0
    tot = (oil + gas) or 1
    a, b = st.columns([1.1, 1], vertical_alignment="center")
    with a:
        donut([oil, gas], ["Oil", "Gas"], [BLUE, ORANGE], "Total\nProduction")
    with b:
        st.metric("🔵 Oil Production", f"{oil / tot * 100:.1f}%", f"{fnum(oil)} bpd", delta_color="off")
        st.metric("🟠 Gas Production", f"{gas / tot * 100:.1f}%", f"{fnum(gas)} Mscf/d", delta_color="off")

t_col, q_col = st.columns([1.9, 1])
with t_col.container(border=True):
    card_head("🗓️ Recent Production Data", "Latest records from the production dataset")
    rec = pd.DataFrame(api("/production/recent", limit=5)["records"])
    if not rec.empty:
        tbl = pd.DataFrame({
            "Date": pd.to_datetime(rec["Timestamp"]).dt.date,
            "Well ID": rec["Well_ID"],
            "Oil Rate (bpd)": rec["Oil_Rate_bpd"],
            "Gas Rate (Mscf/d)": rec["Gas_Rate_Mscf_d"],
            "ROP (m/hr)": rec["ROP_m_hr"],
        })
        st.dataframe(
            tbl, hide_index=True, width="stretch",
            column_config={
                "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                "Oil Rate (bpd)": st.column_config.NumberColumn(format="%.2f"),
                "Gas Rate (Mscf/d)": st.column_config.NumberColumn(format="%.2f"),
                "ROP (m/hr)": st.column_config.NumberColumn(format="%.2f"),
            },
        )
    if st.button("View More", icon=":material/arrow_forward:", type="tertiary"):
        st.switch_page(PAGE_FILES["Wells & Dataset"])

with q_col.container(border=True):
    card_head("⚡ Quick Actions", "Jump to a section")
    actions = [
        ("Drilling Statistics", "View Drilling Statistics", ":material/bar_chart:"),
        ("Production Trends", "Explore Production Trends", ":material/show_chart:"),
        ("Wells & Dataset", "Browse Wells & Dataset", ":material/database:"),
        ("Data Quality", "Check Data Quality", ":material/verified_user:"),
    ]
    for p, lbl, ico in actions:
        if st.button(lbl, icon=ico, key=f"qa_{p}", width="stretch"):
            st.switch_page(PAGE_FILES[p])

b1, b2, b3 = st.columns(3)
with b1.container(border=True):
    card_head("🏆 Top Wells by Oil Production", "Highest producing wells (bpd)")
    top = pd.DataFrame(api("/production/top-wells", limit=5)["data"])
    if not top.empty:
        hbar_chart(top["Well_ID"], top["oil"], w=4.6, h=2.6)

with b2.container(border=True):
    card_head("⚙️ Drilling Performance", "Key drilling metrics")
    info_rows([
        ("Avg. ROP", f"{fnum(get_stat(ds, 'mean', 'ROP_m_hr'))} m/hr"),
        ("Max ROP", f"{fnum(get_stat(ds, 'max', 'ROP_m_hr'))} m/hr"),
        ("Min ROP", f"{fnum(get_stat(ds, 'min', 'ROP_m_hr'))} m/hr"),
        ("Avg. WOB", f"{fnum(get_stat(ds, 'mean', 'WOB_kN'))} kN"),
        ("Avg. Rotary Speed", f"{fnum(get_stat(ds, 'mean', 'Rotary_Speed_RPM'))} RPM"),
    ])

with b3.container(border=True):
    card_head("🗄️ Dataset Overview", "Data summary")
    info_rows([
        ("Total Columns", f"{ctx.total_cols}"),
        ("Total Rows", f"{ctx.total_rows:,}"),
        ("Missing Values", f"{ctx.missing_total:,}"),
        ("Data Completeness", f"{ctx.completeness:.1f}%"),
    ])
    st.progress(min(ctx.completeness / 100, 1.0), text=f"{ctx.completeness:.1f}% complete")

# import pandas as pd
# import streamlit as st

# from utils import get_data, show_header, format_number, get_daily_data, show_trend_chart

# show_header("Well Performance Analysis and Production Forecasting")

# # API se data lena
# summary = get_data("/summary")
# drilling = get_data("/drilling/stats")["Drilling stats"]
# production = get_data("/production/stats")
# wells = get_data("/well_IDs")

# st.subheader("🏠 Dashboard")

# # Upar ke 4 KPI cards
# col1, col2, col3, col4 = st.columns(4)
# col1.metric("Total Records", f"{summary['total_rows']:,}")
# col2.metric("Unique Wells", f"{wells['No_of_unique']:,}")
# col3.metric("Average ROP", format_number(drilling["mean"]["ROP_m_hr"]) + " m/hr")
# col4.metric("Average Oil Rate", format_number(production["avg_oil"]) + " bpd")

# # Production trend chart
# st.subheader("📈 Production Trend")
# daily = get_daily_data()
# show_trend_chart(daily)

# # Oil vs Gas average
# st.subheader("🥧 Oil vs Gas (Average)")
# col1, col2 = st.columns(2)
# col1.metric("Oil Production", format_number(production["avg_oil"]) + " bpd")
# col2.metric("Gas Production", format_number(production["avg_gas"]) + " Mscf/d")

# # Recent records table
# st.subheader("🗓️ Recent Production Data")
# recent = pd.DataFrame(get_data("/production/recent", limit=5)["records"])
# if not recent.empty:
#     table = pd.DataFrame({
#         "Date": pd.to_datetime(recent["Timestamp"]).dt.date,
#         "Well ID": recent["Well_ID"],
#         "Oil Rate (bpd)": recent["Oil_Rate_bpd"],
#         "Gas Rate (Mscf/d)": recent["Gas_Rate_Mscf_d"],
#         "ROP (m/hr)": recent["ROP_m_hr"],
#     })
#     st.dataframe(table, hide_index=True)

# # Top wells
# st.subheader("🏆 Top Wells by Oil Production")
# top = pd.DataFrame(get_data("/production/top-wells", limit=5)["data"])
# if not top.empty:
#     st.bar_chart(top.set_index("Well_ID")["oil"])

# # Drilling performance aur dataset overview
# col1, col2 = st.columns(2)

# with col1:
#     st.subheader("⚙️ Drilling Performance")
#     st.write("Avg ROP:", format_number(drilling["mean"]["ROP_m_hr"]), "m/hr")
#     st.write("Max ROP:", format_number(drilling["max"]["ROP_m_hr"]), "m/hr")
#     st.write("Min ROP:", format_number(drilling["min"]["ROP_m_hr"]), "m/hr")
#     st.write("Avg WOB:", format_number(drilling["mean"]["WOB_kN"]), "kN")
#     st.write("Avg Rotary Speed:", format_number(drilling["mean"]["Rotary_Speed_RPM"]), "RPM")

# with col2:
#     st.subheader("🗄️ Dataset Overview")
#     total_cells = summary["total_rows"] * summary["total_columns"]
#     completeness = (1 - summary["total_missing_values"] / total_cells) * 100
#     st.write("Total Columns:", summary["total_columns"])
#     st.write("Total Rows:", f"{summary['total_rows']:,}")
#     st.write("Missing Values:", f"{summary['total_missing_values']:,}")
#     st.write("Data Completeness:", f"{completeness:.1f}%")
#     st.progress(min(completeness / 100, 1.0))