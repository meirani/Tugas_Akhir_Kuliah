import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_absolute_error, mean_squared_error
from components import show_footer, local_css

# ===============================
# CONFIG & CSS & HEADER
# ===============================
st.set_page_config(page_title="Prediksi DBD", layout="wide", page_icon="📈")

local_css("style.css")

st.markdown(
    """
<div class="hero-container" style="padding-bottom: 0;">
    <div class="hero-badge">Forecast 2026</div>
    <span class="title-highlight" style="font-size: 2.4rem;">Prediksi Kasus DBD 2026</span>
    <span class="title-secondary">Menggunakan Model Seasonal ARIMA (SARIMA)</span>
</div>
""",
    unsafe_allow_html=True,
)

st.divider()


import glob

# ===============================
# BACKEND MODEL
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

df_total = df.groupby("periode")["jumlah_kasus"].sum().reset_index()
df_total = df_total.sort_values("periode")

adf_result = adfuller(df_total["jumlah_kasus"])

train_size = int(len(df_total) * 0.8)
train = df_total["jumlah_kasus"][:train_size]
test = df_total["jumlah_kasus"][train_size:]

model = SARIMAX(
    train,
    order=(2, 1, 2),
    seasonal_order=(2, 1, 1, 12),
    enforce_stationarity=False,
    enforce_invertibility=False,
)
results = model.fit(disp=False)

pred_test = results.predict(start=len(train), end=len(train) + len(test) - 1)

mae = mean_absolute_error(test, pred_test)
rmse = np.sqrt(mean_squared_error(test, pred_test))

forecast_result = results.get_forecast(steps=12)
forecast = forecast_result.predicted_mean
conf_int = forecast_result.conf_int()

future_dates = pd.date_range(
    start=df_total["periode"].max() + pd.DateOffset(months=1), periods=12, freq="MS"
)

df_forecast = pd.DataFrame(
    {
        "periode": future_dates,
        "prediksi_kasus": forecast.values,
        "lower_ci": conf_int.iloc[:, 0].clip(lower=0).values,
        "upper_ci": conf_int.iloc[:, 1].values,
    }
)

peak_row = df_forecast.loc[df_forecast["prediksi_kasus"].idxmax()]
peak_month = peak_row["periode"].strftime("%B %Y")
peak_value = round(peak_row["prediksi_kasus"])
total_forecast_2026 = int(df_forecast["prediksi_kasus"].sum())


# ===============================
# KPI RINGKASAN — SIDEBAR
# ===============================
st.sidebar.markdown(
    f"""
    <div style="padding: 4px 0 12px;">
        <div style="font-size:1rem;font-weight:700;color:#1A1D2E;">Ringkasan Prediksi</div>
    </div>

    <div style="background:linear-gradient(135deg,#F5F3FF,#EDE9FD);border-radius:12px;padding:14px 16px;border:1.5px solid #DDD6FE;margin-bottom:10px;">
        <div style="font-size:0.7rem;font-weight:700;color:#7C3AED;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">Total Prediksi 2026</div>
        <div style="font-size:1.7rem;font-weight:900;color:#1A1D2E;line-height:1;">{total_forecast_2026:,}</div>
        <div style="font-size:0.75rem;color:#6B7280;margin-top:3px;">kasus di DKI Jakarta</div>
    </div>

    <div style="background:linear-gradient(135deg,#FFF1F2,#FFE4E6);border-radius:12px;padding:14px 16px;border:1.5px solid #FECDD3;margin-bottom:10px;">
        <div style="font-size:0.7rem;font-weight:700;color:#F43F5E;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">Puncak Prediksi</div>
        <div style="font-size:1.1rem;font-weight:900;color:#1A1D2E;line-height:1.3;">{peak_month}</div>
        <div style="font-size:0.75rem;color:#6B7280;margin-top:3px;">{peak_value:,} kasus estimasi</div>
    </div>

    <div style="background:linear-gradient(135deg,#F0FDF4,#DCFCE7);border-radius:12px;padding:14px 16px;border:1.5px solid #BBF7D0;">
        <div style="font-size:0.7rem;font-weight:700;color:#22C55E;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">Metode</div>
        <div style="font-size:1.1rem;font-weight:900;color:#1A1D2E;line-height:1.3;">SARIMA</div>
        <div style="font-size:0.75rem;color:#6B7280;margin-top:3px;">Seasonal ARIMA (2,1,2)(2,1,1,12)</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ===============================
# SECTION 1 — GRAFIK PREDIKSI
# ===============================
st.markdown(
    """
    <div class="section-header">
        <div class="dot"></div>
        <span style="font-size:1rem;font-weight:700;color:#1A1D2E;">Grafik Prediksi Kasus DBD 2026</span>
    </div>
    """,
    unsafe_allow_html=True,
)

fig_forecast = go.Figure()

fig_forecast.add_trace(go.Scatter(
    x=df_total["periode"],
    y=df_total["jumlah_kasus"],
    mode="lines",
    name="Data Historis",
    line=dict(color="#5B6EF5", width=2),
))

fig_forecast.add_trace(go.Scatter(
    x=df_forecast["periode"],
    y=df_forecast["upper_ci"],
    mode="lines",
    name="Upper CI (95%)",
    line=dict(dash="dash", color="#F43F5E", width=1.5),
))

fig_forecast.add_trace(go.Scatter(
    x=df_forecast["periode"],
    y=df_forecast["lower_ci"],
    mode="lines",
    name="Lower CI (95%)",
    line=dict(dash="dash", color="#F59E0B", width=1.5),
    fill="tonexty",
    fillcolor="rgba(244,63,94,0.06)",
))

fig_forecast.add_trace(go.Scatter(
    x=df_forecast["periode"],
    y=df_forecast["prediksi_kasus"],
    mode="lines+markers",
    name="Prediksi 2026",
    line=dict(color="#EC4899", width=3),
    marker=dict(size=6, color="#EC4899"),
))

fig_forecast.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", size=12),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=20, r=20, t=44, b=20),
    xaxis=dict(gridcolor="#F0F2FA", title="Periode"),
    yaxis=dict(gridcolor="#F0F2FA", title="Jumlah Kasus"),
    hovermode="x unified",
)
st.plotly_chart(fig_forecast, use_container_width=True)

st.markdown(
    f"""
<div class="box-gradientpurple">
    Berdasarkan pemodelan <strong>Seasonal ARIMA</strong>, puncak kasus DBD tahun 2026 diprediksi jatuh pada 
    <strong>{peak_month}</strong> dengan estimasi <strong>{peak_value:,} kasus</strong>. Algoritma SARIMA berhasil menangkap pola siklus tahunan ini karena mayoritas lonjakan historis 
    memang secara konsisten terjadi pada periode Pancaroba I (peralihan musim hujan ke kemarau).<br><br>
    Garis putus-putus merepresentasikan <strong>Confidence Interval</strong>:
    <ul style="margin:8px 0 0 0;">
        <li><span style="color:#F43F5E;font-weight:600;">Upper CI</span> — Skenario terburuk (batas atas) jika terjadi anomali cuaca yang memperparah penyebaran.</li>
        <li><span style="color:#F59E0B;font-weight:600;">Lower CI</span> — Skenario terbaik (batas bawah). Pada perhitungan matematis, batas ini bisa bernilai negatif, namun dalam konteks epidemologi (jumlah orang sakit), nilai negatif tidaklah mungkin, sehingga kita batasi secara absolut di angka 0.</li>
    </ul>
</div>
""",
    unsafe_allow_html=True,
)


# ===============================
# SECTION 2 — TOP 10 KECAMATAN
# ===============================
st.divider()
st.markdown(
    """
    <div class="section-header">
        <div class="dot" style="background:linear-gradient(135deg,#F43F5E,#F59E0B);"></div>
        <span style="font-size:1rem;font-weight:700;color:#1A1D2E;">Estimasi Wilayah Prioritas DBD Tahun 2026</span>
    </div>
    """,
    unsafe_allow_html=True,
)

total_2026 = df_forecast["prediksi_kasus"].sum()
df_kecamatan = df.groupby("kecamatan")["jumlah_kasus"].sum().reset_index()
total_historis = df_kecamatan["jumlah_kasus"].sum()
df_kecamatan["proporsi"] = df_kecamatan["jumlah_kasus"] / total_historis
df_kecamatan["estimasi_2026"] = df_kecamatan["proporsi"] * total_2026

top_prioritas = df_kecamatan.sort_values("estimasi_2026", ascending=False).head(10)
df_table_kec = top_prioritas.copy()
df_table_kec["estimasi_2026"] = df_table_kec["estimasi_2026"].round(0)

col_tbl, col_chart = st.columns([1, 1.6], gap="small")

with col_tbl:
    st.markdown(
        """
        <div style="font-size:0.85rem;font-weight:700;color:#1A1D2E;margin-bottom:8px;">
            Top 10 Kecamatan Tertinggi
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.dataframe(
        df_table_kec[["kecamatan", "estimasi_2026"]].rename(
            columns={"kecamatan": "Kecamatan", "estimasi_2026": "Estimasi Kasus"}
        ),
        hide_index=True,
        use_container_width=True,
    )

with col_chart:
    fig_prioritas = px.bar(
        top_prioritas.sort_values("estimasi_2026"),
        x="estimasi_2026",
        y="kecamatan",
        orientation="h",
        color="estimasi_2026",
        color_continuous_scale=["#FEF3C7", "#F59E0B", "#EF4444", "#B91C1C"],
        labels={"estimasi_2026": "Estimasi Kasus", "kecamatan": ""},
        title="Grafik Proporsi Top 10 Kecamatan Prioritas",
    )
    fig_prioritas.update_layout(
        coloraxis_showscale=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", size=11),
        title_font=dict(size=13),
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(gridcolor="#F0F2FA"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig_prioritas, use_container_width=True)

top1 = df_table_kec.iloc[0]
st.markdown(
    f"""
<div class="box-gradientorange">
    Kecamatan <strong>{top1['kecamatan']}</strong> menduduki peringkat pertama dengan estimasi mencapai <strong>{int(top1['estimasi_2026'])} kasus</strong>. 
    Metode ini mendistribusikan total prediksi DKI Jakarta berdasarkan bobot proporsi historis (2010-2025) masing-masing wilayah. Kecamatan yang masuk ke dalam 
    Top 10 ini adalah wilayah yang secara historis terbukti memiliki kerentanan tinggi, yang umumnya berkorelasi dengan tingginya kepadatan penduduk dan karakteristik sanitasi lingkungan setempat.
</div>
""",
    unsafe_allow_html=True,
)


# ===============================
# SECTION 3 — KATEGORI RISIKO
# ===============================
st.divider()
st.markdown(
    """
    <div class="section-header">
        <div class="dot" style="background:linear-gradient(135deg,#FF8F8F,#A40000);"></div>
        <span style="font-size:1rem;font-weight:700;color:#1A1D2E;">Kategori Risiko DBD 2026 per Kecamatan</span>
    </div>
    """,
    unsafe_allow_html=True,
)

df_risiko = df_kecamatan.copy()
mean_val = df_kecamatan["estimasi_2026"].mean()
std_val = df_kecamatan["estimasi_2026"].std()

def kategori_risiko(x):
    if x >= mean_val + std_val:
        return "Tinggi 🔴"
    elif x >= mean_val:
        return "Sedang 🟡"
    else:
        return "Rendah 🟢"

df_risiko["kategori"] = df_risiko["estimasi_2026"].apply(kategori_risiko)
df_risiko["estimasi_2026"] = df_risiko["estimasi_2026"].round(0)

jumlah_tinggi = (df_risiko["kategori"] == "Tinggi 🔴").sum()
jumlah_sedang = (df_risiko["kategori"] == "Sedang 🟡").sum()
jumlah_rendah = (df_risiko["kategori"] == "Rendah 🟢").sum()

# Ringkasan risiko
r1, r2, r3 = st.columns(3, gap="medium")
with r1:
    st.markdown(
        f"""
        <div class="risk-high" style="text-align:center;border-radius:12px;">
            <div style="font-size:1.8rem;font-weight:900;">{jumlah_tinggi}</div>
            <div style="font-size:0.8rem;font-weight:700;">Kecamatan Risiko Tinggi</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with r2:
    st.markdown(
        f"""
        <div class="risk-medium" style="text-align:center;border-radius:12px;">
            <div style="font-size:1.8rem;font-weight:900;">{jumlah_sedang}</div>
            <div style="font-size:0.8rem;font-weight:700;">Kecamatan Risiko Sedang</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with r3:
    st.markdown(
        f"""
        <div class="risk-low" style="text-align:center;border-radius:12px;">
            <div style="font-size:1.8rem;font-weight:900;">{jumlah_rendah}</div>
            <div style="font-size:0.8rem;font-weight:700;">Kecamatan Risiko Rendah</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

options_risiko = ["Tinggi 🔴", "Sedang 🟡", "Rendah 🟢"]
selected_risiko = st.multiselect(
    "Filter Kategori Risiko",
    options=options_risiko,
    default=options_risiko,
)

df_risiko_filtered = df_risiko[df_risiko["kategori"].isin(selected_risiko)]

col_risk_tbl, col_risk_chart = st.columns([1, 1.6], gap="small")

with col_risk_tbl:
    st.dataframe(
        df_risiko_filtered.sort_values("estimasi_2026", ascending=False)[
            ["kecamatan", "estimasi_2026", "kategori"]
        ].rename(columns={
            "kecamatan": "Kecamatan",
            "estimasi_2026": "Estimasi Kasus",
            "kategori": "Kategori Risiko",
        }),
        hide_index=True,
        use_container_width=True,
    )

with col_risk_chart:
    color_map = {
        "Tinggi 🔴": "#F43F5E",
        "Sedang 🟡": "#F59E0B",
        "Rendah 🟢": "#22C55E",
    }
    df_risiko_sorted = df_risiko_filtered.sort_values("estimasi_2026", ascending=True)

    fig_heatmap = px.bar(
        df_risiko_sorted,
        x="estimasi_2026",
        y="kecamatan",
        color="kategori",
        orientation="h",
        color_discrete_map=color_map,
        labels={"estimasi_2026": "Estimasi Kasus", "kecamatan": "", "kategori": "Risiko"},
        title="Distribusi Risiko DBD per Kecamatan 2026",
    )
    fig_heatmap.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", size=10),
        title_font=dict(size=13),
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(title="Kategori", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(gridcolor="#F0F2FA"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

st.markdown(
    f"""
<div class="box-outline">
    <strong>Early Warning System</strong><br><br>
    Berdasarkan pengelompokan tingkat risiko menggunakan nilai rata-rata (mean) dan standar deviasi dari hasil prediksi kasus, terdapat <strong>{jumlah_tinggi} kecamatan</strong> yang berstatus Risiko Tinggi 🔴. 
    Melalui filter ini, Pengguna atau pembuat keputusan (Dinas Kesehatan) dapat langsung menyoroti wilayah yang paling rawan. Dengan begitu, tindakan pencegahan seperti fogging dan Pemberantasan Sarang Nyamuk (PSN) 
    bisa langsung difokuskan pada zona merah, sebelum kasus DBD terlanjur meledak.
</div>
""",
    unsafe_allow_html=True,
)


# ===============================
# FOOTER
# ===============================
show_footer()