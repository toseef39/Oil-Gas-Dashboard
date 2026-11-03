import pandas as pd
import streamlit as st

from utils import api, bootstrap, card_head, kpi, page_header

ctx = bootstrap("Wells & Dataset")
opts = ctx.opts

page_header("Wells & Dataset", "Explore well data, search and filter records.")


def _clear():
    st.session_state.update({"w_search": "", "w_field": "All Fields", "w_type": "All Types", "w_page": 1})


with st.container(border=True):
    s, f1, f2, clr = st.columns([3, 1, 1, 0.6], vertical_alignment="bottom")
    search = s.text_input("Search", placeholder="Search by Well ID, Field ID or any keyword...",
                          icon=":material/search:", key="w_search")
    field = f1.selectbox("Field", ["All Fields"] + opts["fields"], key="w_field")
    wtype = f2.selectbox("Well Type", ["All Types"] + opts["well_types"], key="w_type")
    clr.button("Clear", icon=":material/close:", on_click=_clear, width="stretch")

c = st.columns(4)
with c[0]: kpi("Total Wells", f"{ctx.wells_info['No_of_unique']:,}", icon="🛢️")
with c[1]: kpi("Total Records", f"{ctx.total_rows:,}", icon="📄")
with c[2]: kpi("Fields", f"{len(opts['fields'])}", icon="🗂️")
with c[3]: kpi("Well Types", f"{len(opts['well_types'])}", icon="🧩")

A, B = st.columns([1, 3.2])
dmin, dmax = int(opts["depth_min"] or 0), int(opts["depth_max"] or 0)
with A.container(border=True):
    card_head("Advanced Filters")
    depth = st.slider("Depth Range (m)", dmin, max(dmax, dmin + 1), (dmin, max(dmax, dmin + 1)))
    st.button("Apply Filters", icon=":material/filter_alt:", width="stretch")
    st.button("Reset", icon=":material/restart_alt:", on_click=_clear, width="stretch", key="reset2")

PER = 10
if "w_page" not in st.session_state:
    st.session_state["w_page"] = 1

res = api(
    "/wells/filter",
    search=search,
    field_id=None if field == "All Fields" else field,
    well_type=None if wtype == "All Types" else wtype,
    min_depth=depth[0],
    max_depth=depth[1],
    skip=(st.session_state["w_page"] - 1) * PER,
    limit=PER,
)
total = res["total"]
pages = max(1, -(-total // PER))
st.session_state["w_page"] = min(st.session_state["w_page"], pages)

with B.container(border=True):
    card_head("Wells Data", f"{total:,} records match your filters")
    recs = pd.DataFrame(res["records"])
    if not recs.empty:
        cols = [c for c in ["Well_ID", "Field_ID", "Well_Type", "Depth_m", "Oil_Rate_bpd", "Gas_Rate_Mscf_d"] if c in recs]
        show = recs[cols].copy()
        for col in ["Depth_m", "Oil_Rate_bpd", "Gas_Rate_Mscf_d"]:
            if col in show:
                show[col] = pd.to_numeric(show[col], errors="coerce")
        cfg = {
            "Well_ID": "Well ID", "Field_ID": "Field ID", "Well_Type": "Well Type",
            "Depth_m": st.column_config.NumberColumn("Depth (m)", format="%.0f"),
        }
        if "Oil_Rate_bpd" in show:
            cfg["Oil_Rate_bpd"] = st.column_config.ProgressColumn(
                "Oil Rate (bpd)", format="%.2f", min_value=0, max_value=float(max(show["Oil_Rate_bpd"].max(), 1)))
        if "Gas_Rate_Mscf_d" in show:
            cfg["Gas_Rate_Mscf_d"] = st.column_config.ProgressColumn(
                "Gas Rate (Mscf/d)", format="%.2f", min_value=0, max_value=float(max(show["Gas_Rate_Mscf_d"].max(), 1)))
        st.dataframe(show, hide_index=True, width="stretch", column_config=cfg)
    else:
        st.info("Koi record nahi mila.")

    p0 = (st.session_state["w_page"] - 1) * PER
    n1, n2, n3, n4 = st.columns([3, 0.8, 1, 0.8], vertical_alignment="center")
    n1.caption(f"Showing {p0 + 1 if total else 0}-{min(p0 + PER, total)} of {total:,} records")
    if n2.button("Prev", icon=":material/chevron_left:", disabled=st.session_state["w_page"] <= 1, width="stretch"):
        st.session_state["w_page"] -= 1
        st.rerun()
    n3.markdown(f"Page **{st.session_state['w_page']}** / {pages}")
    if n4.button("Next", icon=":material/chevron_right:", icon_position="right",
                 disabled=st.session_state["w_page"] >= pages, width="stretch"):
        st.session_state["w_page"] += 1
        st.rerun()



# import pandas as pd
# import streamlit as st

# from utils import get_data, show_header

# show_header("Wells & Dataset")

# options = get_data("/filters/options")
# summary = get_data("/summary")
# wells = get_data("/well_IDs")

# st.subheader("🗄️ Wells & Dataset")
# st.caption("Explore well data, search and filter records.")

# # Filters
# col1, col2, col3 = st.columns([3, 1, 1])
# search = col1.text_input("Search", placeholder="Search by Well ID, Field ID or any keyword...")
# field = col2.selectbox("Field", ["All Fields"] + options["fields"])
# well_type = col3.selectbox("Well Type", ["All Types"] + options["well_types"])

# depth_min = int(options["depth_min"] or 0)
# depth_max = int(options["depth_max"] or 0)
# depth = st.slider("Depth Range (m)", depth_min, max(depth_max, depth_min + 1), (depth_min, max(depth_max, depth_min + 1)))

# # KPI cards
# col1, col2, col3, col4 = st.columns(4)
# col1.metric("Total Wells", f"{wells['No_of_unique']:,}")
# col2.metric("Total Records", f"{summary['total_rows']:,}")
# col3.metric("Fields", len(options["fields"]))
# col4.metric("Well Types", len(options["well_types"]))

# # Pagination
# PER_PAGE = 10
# if "page" not in st.session_state:
#     st.session_state["page"] = 1

# result = get_data(
#     "/wells/filter",
#     search=search,
#     field_id=None if field == "All Fields" else field,
#     well_type=None if well_type == "All Types" else well_type,
#     min_depth=depth[0],
#     max_depth=depth[1],
#     skip=(st.session_state["page"] - 1) * PER_PAGE,
#     limit=PER_PAGE,
# )

# total = result["total"]
# total_pages = max(1, -(-total // PER_PAGE))
# if st.session_state["page"] > total_pages:
#     st.session_state["page"] = total_pages

# # Table
# st.subheader("Wells Data")
# st.caption(f"{total:,} records match your filters")

# records = pd.DataFrame(result["records"])
# if not records.empty:
#     wanted = ["Well_ID", "Field_ID", "Well_Type", "Depth_m", "Oil_Rate_bpd", "Gas_Rate_Mscf_d"]
#     wanted = [c for c in wanted if c in records]
#     st.dataframe(records[wanted], hide_index=True)
# else:
#     st.info("Koi record nahi mila.")

# # Prev / Next buttons
# col1, col2, col3 = st.columns([1, 1, 1])
# if col1.button("Prev", disabled=st.session_state["page"] <= 1):
#     st.session_state["page"] -= 1
#     st.rerun()
# col2.write(f"Page {st.session_state['page']} / {total_pages}")
# if col3.button("Next", disabled=st.session_state["page"] >= total_pages):
#     st.session_state["page"] += 1
#     st.rerun()