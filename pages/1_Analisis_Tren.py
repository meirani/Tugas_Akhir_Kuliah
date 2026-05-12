import streamlit as st
import pandas as pd
import plotly.express as px
from components import show_footer, local_css

# ===============================
# CONFIG & CSS & HEADER
# ===============================
st.set_page_config(page_title="Analisis Tren DBD", layout="wide", page_icon="📊")

local_css("style.css")

st.markdown(
    """
<div class="hero-container" style="padding-bottom: 0;">
    <div class="hero-badge">Eksplorasi Data Historis</div>
    <span class="title-highlight" style="font-size: 2.4rem;">Analisis Tren Historis Kasus DBD</span>
    <span class="title-secondary">Kecamatan di DKI Jakarta · Periode 2010–2025</span>
</div>
""",
    unsafe_allow_html=True,
)

st.divider()


import glob

# ===============================
# DATA
# ===============================
def load_semua_data():
    semua_file = sorted(glob.glob("data/*.csv"))
    
    if not semua_file:
        st.error("Tidak ada file CSV ditemukan di folder data/")
        st.stop()
    
    semua_df = []
    for file in semua_file:
        try:
            df_temp = pd.read_csv(file)
            semua_df.append(df_temp)
        except Exception as e:
            st.warning(f"File {file} gagal dibaca: {e}")
    
    df_main = pd.concat(semua_df, ignore_index=True)
    df_main["periode"] = pd.to_datetime(df_main["periode"], dayfirst=False, format="mixed")
    df_main["tahun"] = df_main["tahun"].astype(int)
    df_main["bulan"] = df_main["bulan"].astype(int)
    df_main = df_main.drop_duplicates(subset=["kecamatan", "periode"])
    df_main = df_main.sort_values("periode").reset_index(drop=True)
    return df_main

# Selalu load ulang dari file jika belum ada simulasi aktif
if "data_ditambah" not in st.session_state:
    st.session_state["data_ditambah"] = False

if not st.session_state["data_ditambah"]:
    df = load_semua_data()
    st.session_state["df_main"] = df
else:
    df = st.session_state["df_main"].copy()


# ===============================
# SIDEBAR FILTER
# ===============================
st.sidebar.markdown(
    """
    <div style="padding: 4px 0 16px;">
        <div style="font-size: 1rem; font-weight: 700; color: #1A1D2E;">Filter Data</div>
        <div style="font-size: 0.78rem; color: #9CA3AF; margin-top: 2px;">Sesuaikan tampilan grafik</div>
    </div>
    """,
    unsafe_allow_html=True,
)

kecamatan_list = sorted(df["kecamatan"].unique())
selected_kecamatan = st.sidebar.selectbox("Pilih Kecamatan", kecamatan_list)

min_year = df["tahun"].min()
max_year = df["tahun"].max()
selected_years = st.sidebar.slider(
    "Pilih Rentang Tahun", min_year, max_year, (min_year, max_year)
)

selected_months = st.sidebar.multiselect(
    "Pilih Bulan",
    options=list(range(1, 13)),
    default=list(range(1, 13)),
    format_func=lambda x: [
        "Jan","Feb","Mar","Apr","Mei","Jun",
        "Jul","Agu","Sep","Okt","Nov","Des"
    ][x - 1],
)

df_filtered = df[
    (df["kecamatan"] == selected_kecamatan)
    & (df["tahun"].between(selected_years[0], selected_years[1]))
    & (df["bulan"].isin(selected_months))
]

# Ringkasan sidebar
total_kasus = int(df_filtered["jumlah_kasus"].sum())
rata_kasus = round(df_filtered["jumlah_kasus"].mean(), 1)
st.sidebar.divider()
st.sidebar.markdown(
    f"""
    <div style="background:linear-gradient(135deg,#EEF0FE,#EDE9FD);border-radius:12px;padding:12px 14px;border:1px solid #C7CCF8;">
        <div style="font-size:0.75rem;font-weight:700;color:#5B6EF5;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;">Ringkasan Filter</div>
        <div style="font-size:0.85rem;color:#374151;margin-bottom:4px;">📍 {selected_kecamatan}</div>
        <div style="font-size:0.85rem;color:#374151;margin-bottom:4px;">📅 {selected_years[0]} – {selected_years[1]}</div>
        <div style="font-size:1.1rem;font-weight:800;color:#1A1D2E;margin-top:8px;">{total_kasus:,} kasus</div>
        <div style="font-size:0.75rem;color:#6B7280;">total · rata-rata {rata_kasus}/bulan</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ===============================
# SECTION 1 — TIME SERIES
# ===============================
st.markdown(
    """
    <div class="section-header">
        <div class="dot"></div>
        <span style="font-size:1rem;font-weight:700;color:#1A1D2E;">Grafik Time Series Pergerakan Kasus DBD</span>
    </div>
    """,
    unsafe_allow_html=True,
)

fig_ts = px.line(
    df_filtered,
    x="periode",
    y="jumlah_kasus",
    title=f"Tren DBD — {selected_kecamatan} ({selected_years[0]}–{selected_years[1]})",
    color_discrete_sequence=["#5B6EF5"],
)
fig_ts.update_traces(line=dict(width=2.5))
fig_ts.update_layout(
    margin=dict(l=20, r=20, t=44, b=20),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", size=12),
    title_font=dict(size=14, color="#1A1D2E"),
    xaxis=dict(gridcolor="#F0F2FA", title="Periode"),
    yaxis=dict(gridcolor="#F0F2FA", title="Jumlah Kasus"),
)
st.plotly_chart(fig_ts, use_container_width=True)

st.divider()


# ===============================
# SECTION 2 — BULANAN & MUSIMAN
# ===============================
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown(
        """
        <div class="section-header">
            <div class="dot" style="background:linear-gradient(135deg,#7C3AED,#EC4899);"></div>
            <span style="font-size:1rem;font-weight:700;color:#1A1D2E;">Pola Musiman (Rata-rata per Bulan)</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    nama_bulan = ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"]
    monthly_avg = df_filtered.groupby("bulan")["jumlah_kasus"].mean().reset_index()
    monthly_avg["nama_bulan"] = monthly_avg["bulan"].apply(lambda x: nama_bulan[x - 1])

    fig_month = px.bar(
        monthly_avg,
        x="nama_bulan",
        y="jumlah_kasus",
        color="jumlah_kasus",
        color_continuous_scale=["#C7CCF8", "#5B6EF5", "#7C3AED"],
        labels={"nama_bulan": "Bulan", "jumlah_kasus": "Rata-rata Kasus"},
    )
    fig_month.update_layout(
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=16, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", size=11),
        xaxis=dict(gridcolor="#F0F2FA"),
        yaxis=dict(gridcolor="#F0F2FA"),
    )
    st.plotly_chart(fig_month, use_container_width=True)

with col2:
    st.markdown(
        """
        <div class="section-header">
            <div class="dot" style="background:linear-gradient(135deg,#F59E0B,#EF4444);"></div>
            <span style="font-size:1rem;font-weight:700;color:#1A1D2E;">Rata-rata Berdasarkan Musim</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Detail Klasifikasi Musim"):
        st.markdown(
            """
            Pengelompokan musim mengacu pada pola iklim DKI Jakarta berdasarkan data BMKG:

            * 🌧️ **Musim Hujan:** Desember, Januari, Februari
            * 🌤️ **Pancaroba I (Peralihan Hujan ke Kemarau):**  Maret, April, Mei
            * ☀️ **Musim Kemarau:** Juni, Juli, Agustus
            * 🌥️ **Pancaroba II (Peralihan Kemarau ke Hujan):** September, Oktober, November

            <div style="font-size:0.82em;color:#9CA3AF;margin-top:8px;">
                Sumber: Badan Meteorologi, Klimatologi, dan Geofisika (BMKG)
            </div>
            """,
            unsafe_allow_html=True,
        )

    season_avg = df_filtered.groupby("musim")["jumlah_kasus"].mean().reset_index()

    fig_season = px.bar(
        season_avg,
        x="musim",
        y="jumlah_kasus",
        color="musim",
        color_discrete_map={
            "Musim Hujan":  "#3B82F6",
            "Pancaroba I":  "#8B5CF6",
            "Musim Kemarau": "#F59E0B",
            "Pancaroba II": "#10B981",
        },
        labels={"musim": "Musim", "jumlah_kasus": "Rata-rata Kasus"},
    )
    fig_season.update_layout(
        showlegend=False,
        margin=dict(l=10, r=10, t=16, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", size=11),
        xaxis=dict(gridcolor="#F0F2FA"),
        yaxis=dict(gridcolor="#F0F2FA"),
    )
    st.plotly_chart(fig_season, use_container_width=True)


# ===============================
# FOOTER
# ===============================
show_footer()