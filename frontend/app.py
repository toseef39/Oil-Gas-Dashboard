import streamlit as st

st.set_page_config(page_title="Oil & Gas Analytics System", page_icon="🛢️", layout="wide")

pages = [
    st.Page("views/Dashboard.py", title="Dashboard", icon=":material/home:", default=True, url_path="dashboard"),
    st.Page("views/1_Drilling_Statistics.py", title="Drilling Statistics", icon=":material/bar_chart:", url_path="drilling-statistics"),
    st.Page("views/2_Production_Trends.py", title="Production Trends", icon=":material/show_chart:", url_path="production-trends"),
    st.Page("views/3_Wells_Dataset.py", title="Wells & Dataset", icon=":material/database:", url_path="wells-dataset"),
    st.Page("views/4_Data_Quality.py", title="Data Quality", icon=":material/verified_user:", url_path="data-quality"),
]

with st.sidebar:
    st.markdown("### 💧 Oil & Gas")
    st.caption("Analytics System")

pg = st.navigation(pages)

# with st.sidebar:
#     st.divider()
#     st.caption("Powered by ⚡ FastAPI + Streamlit")

pg.run()

# import streamlit as st

# st.set_page_config(page_title="Oil & Gas Analytics System", page_icon="🛢️", layout="wide")

# pages = [
#     st.Page("views/Dashboard.py", title="Dashboard", default=True),
#     st.Page("views/1_Drilling_Statistics.py", title="Drilling Statistics"),
#     st.Page("views/2_Production_Trends.py", title="Production Trends"),
#     st.Page("views/3_Wells_Dataset.py", title="Wells & Dataset"),
#     st.Page("views/4_Data_Quality.py", title="Data Quality"),
# ]

# page = st.navigation(pages)
# page.run()