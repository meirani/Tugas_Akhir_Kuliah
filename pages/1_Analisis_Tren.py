import streamlit as st
import pandas as pd
import plotly.express as px
from components import show_footer, local_css

# ===============================
# CONFIG & CSS & HEADER
# ===============================
st.set_page_config(page_title="Analisis Tren DBD", layout="wide", page_icon="📊")

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

st.markdown(
    """
<div class="hero-container" style="padding-bottom: 0;">
    <span class="title-highlight" style="font-size: 2.4rem;">Analisis Tren Historis Kasus DBD</span>
    <span class="title-secondary">Kecamatan di DKI Jakarta (2010–2025)</span>
</div>
""",
    unsafe_allow_html=True,
)

st.divider()


# ===============================
# DATA
# ===============================
df = pd.read_csv("data/Data_DBD_FINAL_ANALISIS_2010_2025.csv")

df["periode"] = pd.to_datetime(df["periode"])
df["tahun"] = df["tahun"].astype(int)
df["bulan"] = df["bulan"].astype(int)


# ===============================
# SIDEBAR FILTER
# ===============================
st.sidebar.header("⚙️ Filter Data")

# Filter Kecamatan
kecamatan_list = sorted(df["kecamatan"].unique())
selected_kecamatan = st.sidebar.selectbox("Pilih Kecamatan", kecamatan_list)

# Filter Tahun
min_year = df["tahun"].min()
max_year = df["tahun"].max()
selected_years = st.sidebar.slider(
    "Pilih Rentang Tahun", min_year, max_year, (min_year, max_year)
)

# Filter Bulan
selected_months = st.sidebar.multiselect(
    "Pilih Bulan", options=list(range(1, 13)), default=list(range(1, 13))
)

# filtering data
df_filtered = df[
    (df["kecamatan"] == selected_kecamatan)
    & (df["tahun"].between(selected_years[0], selected_years[1]))
    & (df["bulan"].isin(selected_months))
]


# ===============================
# Tabel
# ===============================

# 1️⃣ Pergerakan Kasus
with st.container():
    st.subheader("Grafik Time Series Pergerakan Kasus")

    fig_ts = px.line(
        df_filtered,
        x="periode",
        y="jumlah_kasus",
        title=f"Tren DBD - {selected_kecamatan}",
        color_discrete_sequence=["#E60001"],
    )
    fig_ts.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(fig_ts, use_container_width=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    # 2️⃣ Per Bulan
    with st.container():
        st.subheader("Pola Musiman (Bulanan)")

        st.markdown('<div style="height: 52px;"></div>', unsafe_allow_html=True)

        monthly_avg = df_filtered.groupby("bulan")["jumlah_kasus"].mean().reset_index()

        fig_month = px.bar(
            monthly_avg,
            x="bulan",
            y="jumlah_kasus",
            color_discrete_sequence=["#5932bc"],
        )
        fig_month.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

        st.plotly_chart(fig_month, use_container_width=True)

with col2:
    # 3️⃣ Grafik Musim
    with st.container():
        st.subheader("Rata-rata Berdasarkan Musim")

        with st.expander("Detail Klasifikasi Musim"):
            st.markdown(
                """
            Pengelompokan musim mengacu pada pola iklim umum wilayah DKI Jakarta berdasarkan data historis klimatologi:
            
            * 🌧️ **Musim Hujan:** Desember, Januari, Februari
            * 🌤️ **Pancaroba I (Peralihan Hujan ke Kemarau):** Maret, April, Mei
            * ☀️ **Musim Kemarau:** Juni, Juli, Agustus
            * 🌥️ **Pancaroba II (Peralihan Kemarau ke Hujan):** September, Oktober, November
            
            <div style="font-size: 0.85em; color: #5E6E7E; margin-top: 10px;">
                <i>Source: Badan Meteorologi, Klimatologi, dan Geofisika (BMKG)</i>
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
                "Musim Hujan": "#FFAA01",  
                "Pancaroba I": "#4c80f8",  
                "Musim Kemarau": "#F03B01",  
                "Pancaroba II": "#6c3ce5",  
            },
        )
        fig_season.update_layout(
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

        st.plotly_chart(fig_season, use_container_width=True)


# ===============================
# FOOTER
# ===============================
show_footer()
