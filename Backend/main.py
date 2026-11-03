# from fastapi import FastAPI
# import pandas as pd
# import pydantic as BaseModel


# app = FastAPI()

# # CSV read karna
# df = pd.read_csv("Backend/data/Oil_Gas.csv")


# # Dataset basic information
# @app.get("/summary")
# def ROP_Summary():
#     shape = df.shape
#     columns = df.columns.tolist()
#     missing = df.isnull().sum().sum()

#     return {
#         "total_rows": shape[0],
#         "total_columns": shape[1],
#         "column_names": columns,
#         "total_missing_values": int(missing)
#     }

# # Total_Wells
# @app.get("/wells")
# def Total_Wells(skip: int = 0, limit: int = 10):
#     records = df.astype(object).where(pd.notna(df), None)
#     sliced_records = records.iloc[skip : skip + limit]
#     return {
#         "Total_Wells": sliced_records.to_dict(orient="records")
#     }
    
    
    
# # specific well data
# @app.get("/well/{well_id}")
# def get_well(well_id: str):
#     well = df[df["Well_ID"] == well_id]

#     if well.empty:
#         return {"message": "Well not found"}
#     # Missing values (NaN) ko JSON-compatible None mein convert karo
#     well = well.astype(object).where(pd.notna(well), None)
#     return well.to_dict(orient="records")


# # Well IDs list
# @app.get("/well_IDs")
# def Well_iDs():
#     Unique_wells = df.Well_ID.unique().tolist()
#     No_of_unique = df.Well_ID.nunique()
#     return{
#         "Unique_wells": Unique_wells,
#         "No_of_unique": No_of_unique
#     }
    
# # GET
# # 5. Well ko filters se search karna
# # Endpoint: /wells/filter?field_id=F01
# # Field ID ya doosre supported parameters se records filter karna.

# # Seekhoge: query parameters aur multiple Pandas conditions. 


   
    
#     # Production statistics
# @app.get("/production/stats")
# def Production_states_per_Day():
#     Max_Oil_production_rate = df["Oil_Rate_bpd"].max()
#     Average_production_rate = df["Oil_Rate_bpd"].mean()
#     Mini_Oil_production = df["Oil_Rate_bpd"].min()
    
#     Max_Gas_production = df["Gas_Rate_Mscf_d"].max()
#     Average_Gas_production_rate = df["Gas_Rate_Mscf_d"].mean()
#     Mini_Gas_production = df["Gas_Rate_Mscf_d"].min()
    
    
    
#     return {
#         "Maxmimum Oil Production Per Day ": Max_Oil_production_rate,
#         "Average Oil Production per day " : Average_production_rate,
#         "Minimum Oil production per day": Mini_Oil_production,
        
        
#         "Maximum Gas production per day": Max_Gas_production,
#         "Average Gas production per day": Average_Gas_production_rate,
#         "Minimum Gas production Per day" : Mini_Gas_production
        
#     }

# # 7. Field-wise production
# # Endpoint: /production/by-field
# # Har field ki production ko compare karne ke liye summary.

# # Seekhoge: groupby() aur aggregation.


            
# # Drilling data analysis
# @app.get("/drilling/stats")
# def Drilling_data():
#         Drilling_stats = df.describe().to_dict(orient="index")
        
#         return{
#             "Drilling stats": Drilling_stats
#         }
        
# #  Missing values report
# @app.get("/data-quality")
# def Missing_val_reports():
#     missing_values = df.isnull().sum()
#     missing_values = missing_values.astype(int).to_dict()
#     return {
#         "Missing values Reports": missing_values
#     } 
    


# # # Time-based production data
# @app.get("/production/trend")
# def Trends():
#     production_trends = df.sort_values(by="Timestamp",ascending=True)
#     production_trends = production_trends.astype(object).where(pd.notna(production_trends), None)
#     filt_data = production_trends.head(30).to_dict(orient="records")

#     return {
#         "Production Data filter": filt_data
#     }

from typing import Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI

app = FastAPI(title="Oil & Gas Analytics API")

# CSV read karna
df = pd.read_csv("Backend/data/Oil_Gas.csv")
if "Timestamp" in df.columns:
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

OIL = "Oil_Rate_bpd"
GAS = "Gas_Rate_Mscf_d"


# ---------------- helpers ----------------
def clean(d: pd.DataFrame):
    """DataFrame ko JSON-safe records mein badalna (NaN -> None, datetime -> str)."""
    d = d.copy()
    for c in d.columns:
        if pd.api.types.is_datetime64_any_dtype(d[c]):
            d[c] = d[c].dt.strftime("%Y-%m-%d %H:%M:%S")
    return d.astype(object).where(pd.notna(d), None).to_dict(orient="records")


def apply_filters(d, field_id=None, well_id=None, start=None, end=None):
    if field_id and "Field_ID" in d.columns:
        d = d[d["Field_ID"].astype(str) == field_id]
    if well_id and "Well_ID" in d.columns:
        d = d[d["Well_ID"].astype(str) == well_id]
    if start and "Timestamp" in d.columns:
        d = d[d["Timestamp"] >= pd.to_datetime(start)]
    if end and "Timestamp" in d.columns:
        d = d[d["Timestamp"] < pd.to_datetime(end) + pd.Timedelta(days=1)]
    return d


def num(x):
    return None if pd.isna(x) else float(x)


# ---------------- dataset ----------------
@app.get("/summary")
def ROP_Summary():
    shape = df.shape
    return {
        "total_rows": shape[0],
        "total_columns": shape[1],
        "column_names": df.columns.tolist(),
        "total_missing_values": int(df.isnull().sum().sum()),
    }


@app.get("/wells")
def Total_Wells(skip: int = 0, limit: int = 10):
    return {"Total_Wells": clean(df.iloc[skip: skip + limit])}


@app.get("/well/{well_id}")
def get_well(well_id: str):
    well = df[df["Well_ID"] == well_id]
    if well.empty:
        return {"message": "Well not found"}
    return clean(well)


@app.get("/well_IDs")
def Well_iDs():
    return {
        "Unique_wells": df.Well_ID.unique().tolist(),
        "No_of_unique": int(df.Well_ID.nunique()),
    }


@app.get("/filters/options")
def filter_options():
    def uniq(col):
        return sorted(df[col].dropna().astype(str).unique().tolist()) if col in df.columns else []

    return {
        "fields": uniq("Field_ID"),
        "well_types": uniq("Well_Type"),
        "well_ids": uniq("Well_ID"),
        "depth_min": num(df["Depth_m"].min()) if "Depth_m" in df.columns else 0,
        "depth_max": num(df["Depth_m"].max()) if "Depth_m" in df.columns else 0,
        "date_min": str(df["Timestamp"].min().date()) if "Timestamp" in df.columns else None,
        "date_max": str(df["Timestamp"].max().date()) if "Timestamp" in df.columns else None,
    }


# Endpoint: /wells/filter?field_id=F01
@app.get("/wells/filter")
def filter_wells(
    field_id: Optional[str] = None,
    well_type: Optional[str] = None,
    search: Optional[str] = None,
    min_depth: Optional[float] = None,
    max_depth: Optional[float] = None,
    skip: int = 0,
    limit: int = 10,
):
    d = df
    if field_id:
        d = d[d["Field_ID"].astype(str) == field_id]
    if well_type:
        d = d[d["Well_Type"].astype(str).isin(well_type.split(","))]
    if min_depth is not None:
        d = d[d["Depth_m"] >= min_depth]
    if max_depth is not None:
        d = d[d["Depth_m"] <= max_depth]
    if search:
        s = search.lower()
        mask = d["Well_ID"].astype(str).str.lower().str.contains(s, na=False)
        if "Field_ID" in d.columns:
            mask |= d["Field_ID"].astype(str).str.lower().str.contains(s, na=False)
        d = d[mask]
    return {"total": int(len(d)), "records": clean(d.iloc[skip: skip + limit])}


# ---------------- production ----------------
@app.get("/production/stats")
def Production_states_per_Day():
    return {
        "max_oil": num(df[OIL].max()),
        "avg_oil": num(df[OIL].mean()),
        "min_oil": num(df[OIL].min()),
        "max_gas": num(df[GAS].max()),
        "avg_gas": num(df[GAS].mean()),
        "min_gas": num(df[GAS].min()),
    }


# Field-wise production
@app.get("/production/by-field")
def production_by_field(
    field_id: Optional[str] = None,
    well_id: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
):
    d = apply_filters(df, field_id, well_id, start, end)
    g = d.groupby("Field_ID").agg(
        oil_avg=(OIL, "mean"), oil_total=(OIL, "sum"),
        gas_avg=(GAS, "mean"), gas_total=(GAS, "sum"),
    ).reset_index()
    return {
        "fields": clean(g),
        "overall": {
            "oil_total": float(d[OIL].sum()), "gas_total": float(d[GAS].sum()),
            "oil_avg": num(d[OIL].mean()), "gas_avg": num(d[GAS].mean()),
        },
    }


# Daily average trend (chart ke liye)
@app.get("/production/daily")
def production_daily(
    field_id: Optional[str] = None,
    well_id: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
):
    d = apply_filters(df, field_id, well_id, start, end).dropna(subset=["Timestamp"])
    g = d.groupby(d["Timestamp"].dt.date)[[OIL, GAS]].mean().reset_index()
    g.columns = ["date", "oil", "gas"]
    g["date"] = g["date"].astype(str)
    return {"data": clean(g)}


# Latest records (table ke liye)
@app.get("/production/recent")
def production_recent(
    field_id: Optional[str] = None,
    well_id: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    limit: int = 5,
):
    d = apply_filters(df, field_id, well_id, start, end)
    d = d.sort_values("Timestamp", ascending=False).head(limit)
    return {"records": clean(d)}


@app.get("/production/top-wells")
def top_wells(limit: int = 5):
    g = df.groupby("Well_ID")[OIL].mean().nlargest(limit).reset_index()
    g.columns = ["Well_ID", "oil"]
    return {"data": clean(g)}


# Time-based production data
@app.get("/production/trend")
def Trends(limit: int = 30):
    d = df.sort_values(by="Timestamp", ascending=True)
    if limit > 0:
        d = d.head(limit)
    return {"Production Data filter": clean(d)}


# ---------------- drilling ----------------
@app.get("/drilling/stats")
def Drilling_data():
    stats = df.describe()
    stats = stats.astype(object).where(pd.notna(stats), None)
    return {"Drilling stats": stats.to_dict(orient="index")}


@app.get("/drilling/distribution")
def drilling_distribution(column: str = "ROP_m_hr", bins: int = 10):
    if column not in df.columns:
        return {"message": "Column not found"}
    s = pd.to_numeric(df[column], errors="coerce").dropna()
    counts, edges = np.histogram(s, bins=bins)
    return {"column": column, "counts": counts.tolist(), "edges": [float(e) for e in edges]}


# ---------------- data quality ----------------
@app.get("/data-quality")
def Missing_val_reports():
    return {"Missing values Reports": df.isnull().sum().astype(int).to_dict()}



