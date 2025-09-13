import io
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

# ------------------------------
# App Title & Config
# ------------------------------
st.set_page_config(page_title="MBTI Top 10 by Country", layout="wide")
st.title("📊 MBTI 유형별 상위 10개 국가 시각화")
st.caption("업로드한 CSV를 바탕으로 각 MBTI 유형 비율이 가장 높은 국가 TOP 10을 Altair로 인터랙티브하게 보여줍니다.")

# ------------------------------
# File Upload
# ------------------------------
uploaded = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])  # e.g. countriesMBTI_16types.csv
st.write(":information_source: CSV에는 국가명 컬럼과 16개 MBTI 컬럼(INTJ, INTP, …, ESFP)이 포함되어야 합니다.")

MBTI_TYPES = [
    "INTJ","INTP","ENTJ","ENTP",
    "INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ",
    "ISTP","ISFP","ESTP","ESFP",
]

@st.cache_data(show_spinner=False)
def load_csv(file) -> pd.DataFrame:
    # Try a couple of encodings just in case
    if file is None:
        return pd.DataFrame()
    content = file.read()
    for enc in ("utf-8", "cp949", "utf-8-sig"):
        try:
            return pd.read_csv(io.BytesIO(content), encoding=enc)
        except Exception:
            continue
    # Fallback: let pandas guess
    return pd.read_csv(io.BytesIO(content))

@st.cache_data(show_spinner=False)
def detect_columns(df: pd.DataFrame):
    # Country-like column
    country_col = None
    for c in df.columns:
        cl = str(c).strip().lower()
        if "country" in cl or "nation" in cl or "국가" in cl or "나라" in cl:
            country_col = c
            break
    if country_col is None:
        # fallback: first non-numeric column
        obj_cols = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
        country_col = obj_cols[0] if obj_cols else df.columns[0]

    # MBTI columns (case-insensitive exact token match or contains)
    col_map = {}
    for c in df.columns:
        cu = str(c).strip().upper()
        for t in MBTI_TYPES:
            if cu == t or cu.startswith(t) or f" {t}" in cu or t in cu:
                col_map.setdefault(t, c)
                break
    mbti_cols = [col_map[t] for t in MBTI_TYPES if t in col_map]
    return country_col, mbti_cols

@st.cache_data(show_spinner=False)
def clean_and_long(df: pd.DataFrame, country_col: str, mbti_cols: list[str]):
    if df.empty:
        return df, pd.DataFrame(), 1.0

    dfc = df.copy()

    # Strip string whitespace
    for c in dfc.columns:
        if pd.api.types.is_string_dtype(dfc[c]):
            dfc[c] = dfc[c].astype(str).str.strip()

    # Coerce MBTI columns to numeric, remove % and commas
    for c in mbti_cols:
        dfc[c] = (
            dfc[c]
            .astype(str)
            .str.replace("%", "", regex=False)
            .str.replace(",", "", regex=False)
        )
        dfc[c] = pd.to_numeric(dfc[c], errors="coerce")

    # Determine scale (0~1 vs 0~100)
    totals = dfc[mbti_cols].sum(axis=1, skipna=True)
    finite_totals = totals.replace([np.inf, -np.inf], np.nan).dropna()
    expected_scale = 100.0 if (not finite_totals.empty and finite_totals.median() > 1.5) else 1.0

    # If values look like 0~100, convert to 0~1 for consistent formatting
    if expected_scale == 100.0:
        for c in mbti_cols:
            dfc[c] = dfc[c] / 100.0

    # Long-form
    long_df = dfc.melt(
        id_vars=[country_col],
        value_vars=mbti_cols,
        var_name="Type",
        value_name="Value",
    ).dropna(subset=["Value"]) 

    # Normalize type labels to canonical
    # (If original col had like 'INTJ %', map back to 'INTJ')
    canon_map = {}
    for c in mbti_cols:
        cu = str(c).strip().upper()
        key = None
        for t in MBTI_TYPES:
            if cu == t or cu.startswith(t) or t in cu:
                key = t
                break
        canon_map[c] = key if key else c
    long_df["Type"] = long_df["Type"].map(canon_map).fillna(long_df["Type"])    

    # Safety: clip to [0,1]
    long_df["Value"] = long_df["Value"].clip(lower=0, upper=1)

    return dfc, long_df, 1.0  # we standardized to 0~1

@st.cache_data(show_spinner=False)
def topk_by_type(long_df: pd.DataFrame, type_name: str, k: int = 10, country_col: str = "Country"):
    sdf = long_df[long_df["Type"] == type_name].copy()
    sdf = sdf.sort_values("Value", ascending=False).head(k)
    # Keep order in chart
    sdf["Country_ordered"] = pd.Categorical(sdf[country_col], categories=sdf[country_col].tolist(), ordered=True)
    return sdf

@st.cache_data(show_spinner=False)
def topk_all_types(long_df: pd.DataFrame, k: int = 10, country_col: str = "Country"):
    # For each type, take top-k
    out = (
        long_df.sort_values(["Type", "Value"], ascending=[True, False])
        .groupby("Type", group_keys=False)
        .head(k)
        .copy()
    )
    return out

# ------------------------------
# Main UI
# ------------------------------
if uploaded is None:
    st.info("예시: countriesMBTI_16types.csv와 같은 형식의 파일을 업로드하면 그래프가 생성됩니다.")
    st.stop()

raw_df = load_csv(uploaded)
if raw_df.empty:
    st.error("CSV를 읽을 수 없습니다. 파일 형식/인코딩을 확인해주세요.")
    st.stop()

country_col, mbti_cols = detect_columns(raw_df)
if len(mbti_cols) < 16:
    st.warning(f"감지된 MBTI 컬럼 수: {len(mbti_cols)} (예상 16) — 컬럼명을 확인해주세요.")

clean_df, long_df, _ = clean_and_long(raw_df, country_col, mbti_cols)

# Sidebar controls
st.sidebar.header("설정")
sel_type = st.sidebar.selectbox("MBTI 유형 선택", MBTI_TYPES)
top_k = st.sidebar.slider("TOP K", min_value=5, max_value=20, value=10, step=1)

# ------------------------------
# Tab layout
# ------------------------------
tab1, tab2 = st.tabs(["단일 유형", "모든 유형(소분할)"])

with tab1:
    st.subheader(f"🔎 {sel_type} 비율이 높은 국가 TOP {top_k}")
    sdf = topk_by_type(long_df.rename(columns={country_col: "Country"}), sel_type, top_k, country_col="Country")

    if sdf.empty:
        st.warning("선택한 유형 데이터가 비어 있습니다.")
    else:
        chart = (
            alt.Chart(sdf)
            .mark_bar()
            .encode(
                x=alt.X("Value:Q", title="비율", axis=alt.Axis(format=".0%")),
                y=alt.Y("Country_ordered:N", title="국가", sort=None),
                tooltip=[
                    alt.Tooltip("Country_ordered:N", title="국가"),
                    alt.Tooltip("Value:Q", title="비율", format=".2%"),
                ],
            )
            .properties(height=420)
            .interactive()
        )
        st.altair_chart(chart, use_container_width=True)

with tab2:
    st.subheader(f"🧩 모든 MBTI 유형별 TOP {top_k} 국가 (Facet)")
    all_top = topk_all_types(long_df.rename(columns={country_col: "Country"}), top_k, country_col="Country")

    # keep order per facet (Altair sorts within facets by value automatically via '-x')
    chart_all = (
        alt.Chart(all_top)
        .mark_bar()
        .encode(
            x=alt.X("Value:Q", title="비율", axis=alt.Axis(format=".0%")),
            y=alt.Y("Country:N", title="국가", sort='-x'),
            tooltip=[
                alt.Tooltip("Type:N", title="유형"),
                alt.Tooltip("Country:N", title="국가"),
                alt.Tooltip("Value:Q", title="비율", format=".2%"),
            ],
            column=alt.Column("Type:N", title="유형", sort=MBTI_TYPES),
        )
        .resolve_scale(x='independent', y='independent')
        .properties(height=220)
        .interactive()
    )
    st.altair_chart(chart_all, use_container_width=True)

# ------------------------------
# Data preview & download
# ------------------------------
with st.expander("데이터 미리보기"):
    st.dataframe(clean_df.head(30))

st.download_button(
    label="정리된 Long-Form 데이터 다운로드 (CSV)",
    data=long_df.to_csv(index=False).encode("utf-8-sig"),
    file_name="mbti_long.csv",
    mime="text/csv",
)

st.caption("ⓘ 값이 0~100%로 주어진 경우 자동으로 0~1 스케일로 변환하여 표시합니다. 음수/100% 초과값은 0~1 범위로 클리핑합니다.")
