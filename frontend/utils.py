from datetime import datetime
from types import SimpleNamespace

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import streamlit as st

API = "http://127.0.0.1:8000"

BLUE, ORANGE, GREEN, PURPLE = "#3B82F6", "#F59E0B", "#22C55E", "#8B5CF6"

PAGE_ICONS = {
    "Dashboard": "🏠",
    "Drilling Statistics": "📊",
    "Production Trends": "📈",
    "Wells & Dataset": "🗄️",
    "Data Quality": "🛡️",
}

# Page file paths (app.py ke relative) - st.switch_page ke liye
PAGE_FILES = {
    "Dashboard": "views/Dashboard.py",
    "Drilling Statistics": "views/1_Drilling_Statistics.py",
    "Production Trends": "views/2_Production_Trends.py",
    "Wells & Dataset": "views/3_Wells_Dataset.py",
    "Data Quality": "views/4_Data_Quality.py",
}


@st.cache_data(ttl=60, show_spinner=False)
def api(path: str, **params):
    params = {k: v for k, v in params.items() if v not in (None, "", "All")}
    r = requests.get(f"{API}{path}", params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def kpi(title, value, delta=None, tone="blue", icon="", spark=None):
    """Native st.metric card. spark = numbers ki list ho to chhota trend chart dikhta hai.
    'tone' sirf purani calls ke liye hai, ab use nahi hota."""
    if delta:
        delta = delta.replace("↑", "").strip()
    kwargs = {}
    if spark is not None and len(spark) > 1:
        kwargs = dict(chart_data=[float(x) for x in spark], chart_type="area")
    st.metric(label=f"{icon} {title}".strip(), value=value, delta=delta, border=True, **kwargs)


def card_head(title, sub=""):
    st.markdown(f"#### {title}")
    if sub:
        st.caption(sub)


def info_rows(rows):
    """rows = [(label, value), ...] -> chhoti table."""
    df = pd.DataFrame(rows, columns=["Metric", "Value"]).set_index("Metric")
    st.table(df)


def style_ax(ax):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color("#C9D5EA")
    ax.grid(axis="y", alpha=0.25)
    ax.tick_params(labelsize=8, length=0, colors="#4B5B78")


def new_fig(w, h):
    """Transparent background wali matplotlib figure (page ke saath blend hoti hai)."""
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    return fig, ax


def hist_chart(counts, edges, w=6, h=2.8):
    fig, ax = new_fig(w, h)
    ax.bar(edges[:-1], counts, width=np.diff(edges), align="edge", color=BLUE, edgecolor="white", linewidth=0.8)
    style_ax(ax)
    fig.tight_layout()
    st.pyplot(fig, width="stretch")
    plt.close(fig)


def hbar_chart(labels, values, w=5, h=2.6, color=BLUE):
    """Horizontal ranked bars (upar se neeche order barqarar rehta hai)."""
    labels, values = list(labels)[::-1], list(values)[::-1]
    fig, ax = new_fig(w, h)
    ax.barh(labels, values, color=color, height=0.62)
    top = max(values) if len(values) else 1
    for i, v in enumerate(values):
        ax.text(v + top * 0.01, i, f"{v:,.0f}", va="center", fontsize=8, color="#0B1B3A")
    style_ax(ax)
    ax.grid(False)
    ax.set_xticks([])
    ax.set_xlim(0, top * 1.18)
    fig.tight_layout()
    st.pyplot(fig, width="stretch")
    plt.close(fig)


def donut(values, labels, colors, center_text, height=150):
    """Donut chart. center_text mein '\n' se do lines ban jati hain."""
    df = pd.DataFrame({"label": labels, "value": [float(v) for v in values]})
    center = center_text.split("\n") if "\n" in center_text else center_text
    spec = {
        "height": height,
        "layer": [
            {"mark": {"type": "arc", "innerRadius": height * 0.30, "outerRadius": height * 0.46,
                      "cornerRadius": 3, "padAngle": 0.02},
             "encoding": {
                 "theta": {"field": "value", "type": "quantitative"},
                 "color": {"field": "label", "type": "nominal", "legend": None,
                           "scale": {"domain": list(labels), "range": list(colors)}},
                 "tooltip": [{"field": "label", "title": "Type"},
                             {"field": "value", "title": "Value", "format": ",.2f"}],
             }},
            {"mark": {"type": "text", "fontSize": 12, "fontWeight": "bold", "lineHeight": 14, "color": "#7B8AA5"},
             "encoding": {"text": {"value": center}}},
        ],
    }
    st.vega_lite_chart(df, spec, width="stretch")


def fnum(x, d=2):
    return "-" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:,.{d}f}"


def get_stat(ds, stat, col):
    return (ds.get(stat) or {}).get(col)


def page_header(title, sub):
    st.subheader(f"{PAGE_ICONS[title]} {title}")
    st.caption(sub)


def daily_df(**filters):
    d = pd.DataFrame(api("/production/daily", **filters)["data"])
    if d.empty:
        return d
    d["date"] = pd.to_datetime(d["date"])
    if len(d) > 150:  # chart saaf rakhne ke liye weekly average
        d = d.set_index("date").resample("W").mean().reset_index()
    return d


def trend_chart(d, height=300):
    """Interactive oil/gas line chart (Streamlit native)."""
    if d.empty:
        st.info("Is selection ke liye data nahi mila.")
        return
    chart = d.set_index("date").rename(columns={"oil": "Oil Rate (bpd)", "gas": "Gas Rate (Mscf/d)"})
    st.line_chart(chart[["Oil Rate (bpd)", "Gas Rate (Mscf/d)"]], color=[BLUE, ORANGE], height=height)


def bootstrap(subtitle: str) -> SimpleNamespace:
    """Har page ke shuru mein: title dikhao, API check karo, common data wapas do."""
    try:
        summary = api("/summary")
        connected = True
    except Exception:
        summary, connected = {}, False

    with st.container(border=True):
        left, right = st.columns([3, 1], vertical_alignment="center")
        with left:
            st.markdown("## 🛢️ Oil & Gas Analytics System")
            st.caption(subtitle)
        with right:
            if connected:
                st.badge("API Connected", icon=":material/check_circle:", color="green")
            else:
                st.badge("API Disconnected", icon=":material/error:", color="red")
            # st.caption(f"Last Updated: {datetime.now().strftime('%d %b %Y %I:%M %p')}")

    if not connected:
        st.error(f"FastAPI server nahi mil raha ({API}). Pehle backend chalayen: `uvicorn Backend.main:app --reload`")
        st.stop()

    total_rows, total_cols = summary["total_rows"], summary["total_columns"]
    missing_total = summary["total_missing_values"]
    completeness = (1 - missing_total / (total_rows * total_cols)) * 100 if total_rows else 0
    return SimpleNamespace(
        summary=summary,
        opts=api("/filters/options"),
        ds=api("/drilling/stats")["Drilling stats"],
        pstats=api("/production/stats"),
        wells_info=api("/well_IDs"),
        total_rows=total_rows,
        total_cols=total_cols,
        missing_total=missing_total,
        completeness=completeness,
    )

# import requests
# import pandas as pd
# import streamlit as st

# API = "http://127.0.0.1:8000"


# def get_data(path, **params):
#     """API se data lata hai. Khali values filter se hata deta hai."""
#     clean = {}
#     for key, value in params.items():
#         if value is not None and value != "" and value != "All":
#             clean[key] = value

#     response = requests.get(API + path, params=clean, timeout=30)
#     response.raise_for_status()
#     return response.json()


# def show_header(subtitle):
#     """Har page ke shuru mein title dikhata hai aur API check karta hai."""
#     st.title("🛢️ Oil & Gas Analytics System")
#     st.caption(subtitle)

#     try:
#         get_data("/summary")
#         st.success("API Connected")
#     except Exception:
#         st.error("FastAPI server nahi mila. Pehle backend chalayen: uvicorn Backend.main:app --reload")
#         st.stop()


# def format_number(value, decimals=2):
#     """Number ko sundar format mein dikhata hai."""
#     if value is None:
#         return "-"
#     return f"{value:,.{decimals}f}"


# def get_daily_data(**filters):
#     """Daily oil/gas production ka DataFrame wapas deta hai."""
#     result = get_data("/production/daily", **filters)
#     data = pd.DataFrame(result["data"])
#     if not data.empty:
#         data["date"] = pd.to_datetime(data["date"])
#     return data


# def show_trend_chart(data):
#     """Oil aur gas ka line chart."""
#     if data.empty:
#         st.info("Is selection ke liye data nahi mila.")
#         return
#     chart = data.set_index("date")
#     chart = chart.rename(columns={"oil": "Oil Rate (bpd)", "gas": "Gas Rate (Mscf/d)"})
#     st.line_chart(chart[["Oil Rate (bpd)", "Gas Rate (Mscf/d)"]])