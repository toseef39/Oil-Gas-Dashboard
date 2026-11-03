import pandas as pd
import streamlit as st

from utils import BLUE, GREEN, ORANGE, api, bootstrap, card_head, donut, hbar_chart, kpi, page_header

ctx = bootstrap("Data Quality")
total_rows, total_cols, completeness = ctx.total_rows, ctx.total_cols, ctx.completeness

page_header("Data Quality", "Check missing values, data completeness and overall dataset health.")

c = st.columns(4)
with c[0]: kpi("Total Rows", f"{total_rows:,}", icon="📄")
with c[1]: kpi("Total Columns", f"{total_cols}", icon="🧱")
with c[2]: kpi("Missing Values", f"{ctx.missing_total:,}", icon="💧")
with c[3]: kpi("Data Completeness", f"{completeness:.1f}%", icon="🛡️")

mv = pd.Series(api("/data-quality")["Missing values Reports"]).sort_values(ascending=False)
mv = mv[mv > 0]
top, others = mv.head(7), mv.iloc[7:].sum()
if others > 0:
    top = pd.concat([top, pd.Series({"Others": others})])
pct = (top / total_rows * 100).round(2)

L, R = st.columns([1, 1.2])
with L.container(border=True):
    card_head("Missing Values by Column", "Columns with the most gaps")
    tbl = pd.DataFrame({"Column": top.index, "Missing Values": top.values, "Percentage": pct.values})
    st.dataframe(
        tbl, hide_index=True, width="stretch",
        column_config={
            "Missing Values": st.column_config.NumberColumn(format="%d"),
            "Percentage": st.column_config.ProgressColumn(
                "Percentage", format="%.2f%%", min_value=0, max_value=float(max(pct.max(), 1))),
        },
    )
with R.container(border=True):
    card_head("Missing Values Chart", "Highest to lowest")
    if len(top):
        hbar_chart(top.index, top.values, w=6, h=3.2)
    else:
        st.success("Koi missing value nahi mili.")

I, D = st.columns([1.6, 1])
with I.container(border=True):
    card_head("🔎 Data Quality Insights", "Automatic health summary")
    quality = "good" if completeness >= 90 else "needs attention"
    worst = ", ".join(mv.head(3).index) if len(mv) else "none"
    (st.success if completeness >= 90 else st.warning)(
        f"Data completeness is **{completeness:.1f}%**, which is {quality}.")
    st.success(f"Most missing values are in: **{worst}**.")
    st.success(f"**{len(mv)}** of {total_cols} columns contain missing values.")
    st.success(f"Total cells checked: **{total_rows * total_cols:,}**.")

with D.container(border=True):
    card_head("Data Completeness", "Complete vs missing cells")
    a, b = st.columns([1.1, 1], vertical_alignment="center")
    with a:
        donut([completeness, 100 - completeness], ["Complete", "Missing"], [GREEN, ORANGE], f"{completeness:.1f}%")
    with b:
        st.metric("🟢 Complete Data", f"{completeness:.1f}%")
        st.metric("🟠 Missing Data", f"{100 - completeness:.1f}%")



# import pandas as pd
# import streamlit as st

# from utils import get_data, show_header

# show_header("Data Quality")

# summary = get_data("/summary")
# total_rows = summary["total_rows"]
# total_cols = summary["total_columns"]
# missing_total = summary["total_missing_values"]
# completeness = (1 - missing_total / (total_rows * total_cols)) * 100

# st.subheader("🛡️ Data Quality")
# st.caption("Check missing values, data completeness and overall dataset health.")

# # KPI cards
# col1, col2, col3, col4 = st.columns(4)
# col1.metric("Total Rows", f"{total_rows:,}")
# col2.metric("Total Columns", total_cols)
# col3.metric("Missing Values", f"{missing_total:,}")
# col4.metric("Data Completeness", f"{completeness:.1f}%")

# # Missing values by column
# missing = pd.Series(get_data("/data-quality")["Missing values Reports"])
# missing = missing[missing > 0].sort_values(ascending=False)

# st.subheader("Missing Values by Column")
# if len(missing) > 0:
#     table = pd.DataFrame({
#         "Column": missing.index,
#         "Missing Values": missing.values,
#         "Percentage": (missing.values / total_rows * 100).round(2),
#     })
#     st.dataframe(table, hide_index=True)
#     st.bar_chart(missing)
# else:
#     st.success("Koi missing value nahi mili.")

# # Insights
# st.subheader("🔎 Data Quality Insights")
# if completeness >= 90:
#     st.success(f"Data completeness is {completeness:.1f}%, which is good.")
# else:
#     st.warning(f"Data completeness is {completeness:.1f}%, which needs attention.")

# if len(missing) > 0:
#     st.info("Most missing values are in: " + ", ".join(missing.head(3).index))
# st.info(f"{len(missing)} of {total_cols} columns contain missing values.")
# st.info(f"Total cells checked: {total_rows * total_cols:,}")

# # Completeness
# st.subheader("Data Completeness")
# st.progress(min(completeness / 100, 1.0))
# col1, col2 = st.columns(2)
# col1.metric("Complete Data", f"{completeness:.1f}%")
# col2.metric("Missing Data", f"{100 - completeness:.1f}%")