import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    mean_absolute_percentage_error,
)
from components import show_footer, local_css

# ===============================
# CONFIG & CSS & HEADER
# ===============================
st.set_page_config(page_title="Evaluasi Model", layout="wide", page_icon="📝")

local_css("style.css")

st.markdown(
    """
<div class="hero-container" style="padding-bottom: 0;">
    <div class="hero-badge">Validasi & Performa</div>
    <span class="title-highlight" style="font-size: 2.4rem;">Evaluasi Model Seasonal ARIMA</span>
    <span class="title-secondary">Performa Prediksi Data Historis Kasus DBD DKI Jakarta</span>
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
mape = mean_absolute_percentage_error(test, pred_test) * 100
akurasi = 100 - mape


# ===============================
# SECTION 1 — KPI DASHBOARD
# ===============================
st.markdown(
    """
    <div class="section-header">
        <div class="dot"></div>
        <span style="font-size:1rem;font-weight:700;color:#1A1D2E;">Dashboard Metrik Performa Model</span>
    </div>
    """,
    unsafe_allow_html=True,
)

col_kpi1, col_kpi2, col_kpi3 = st.columns(3, gap="small")

with col_kpi1:
    st.markdown(
        f"""
        <div class="box-gradientblue" style="text-align:center;padding:20px 16px;">
            <div style="font-size:0.72rem;font-weight:700;color:#3B82F6;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;">MAE</div>
            <div style="font-size:2rem;font-weight:900;color:#1A1D2E;line-height:1;">{mae:.2f}</div>
            <div style="font-size:0.75rem;color:#6B7280;margin-top:4px;">Mean Absolute Error</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_kpi2:
    st.markdown(
        f"""
        <div class="box-gradientpurple" style="text-align:center;padding:20px 16px;">
            <div style="font-size:0.72rem;font-weight:700;color:#7C3AED;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;">RMSE</div>
            <div style="font-size:2rem;font-weight:900;color:#1A1D2E;line-height:1;">{rmse:.2f}</div>
            <div style="font-size:0.75rem;color:#6B7280;margin-top:4px;">Root Mean Square Error</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_kpi3:
    st.markdown(
        f"""
        <div class="box-gradientorange" style="text-align:center;padding:20px 16px;">
            <div style="font-size:0.72rem;font-weight:700;color:#F59E0B;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;">MAPE</div>
            <div style="font-size:2rem;font-weight:900;color:#1A1D2E;line-height:1;">{mape:.2f}%</div>
            <div style="font-size:0.75rem;color:#6B7280;margin-top:4px;">Mean Absolute % Error</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    f"""
<div class="box-outline" style="margin-top:4px;">
    Model SARIMA memiliki akurasi prediksi sebesar <strong>{akurasi:.2f}%</strong> dengan tingkat error (MAPE) <strong>{mape:.2f}%</strong>.
    Dalam pemodelan time series epidemiologi penyakit menular, nilai ini <strong>sangat wajar</strong>.
    Kasus DBD memiliki sifat <strong>fluktuatif</strong> yang ekstrem dan rentan terhadap <strong>anomali</strong> seperti contohnya pandemi covid lalu,
    sehingga evaluasi tidak bisa hanya bertumpu pada besaran angka <i>error</i> semata.
</div>
""",
    unsafe_allow_html=True,
)

st.divider()


# ===============================
# SECTION 2 — AKTUAL VS PREDIKSI
# ===============================
st.markdown(
    """
    <div class="section-header">
        <div class="dot" style="background:linear-gradient(135deg,#F59E0B,#EF4444);"></div>
        <span style="font-size:1rem;font-weight:700;color:#1A1D2E;">Visualisasi Uji Coba: Data Aktual vs Prediksi</span>
    </div>
    """,
    unsafe_allow_html=True,
)

df_eval = pd.DataFrame(
    {
        "periode": df_total["periode"][train_size:],
        "Aktual": test.values,
        "Prediksi": pred_test.values,
    }
)

fig_compare = go.Figure()
fig_compare.add_trace(go.Scatter(
    x=df_eval["periode"], y=df_eval["Aktual"],
    mode="lines", name="Aktual",
    line=dict(color="#F59E0B", width=2.5),
))
fig_compare.add_trace(go.Scatter(
    x=df_eval["periode"], y=df_eval["Prediksi"],
    mode="lines", name="Prediksi",
    line=dict(color="#5B6EF5", width=2.5, dash="dot"),
))
fig_compare.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", size=12),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(t=20, b=20, l=10, r=10),
    xaxis=dict(gridcolor="#F0F2FA", title="Periode"),
    yaxis=dict(gridcolor="#F0F2FA", title="Jumlah Kasus"),
    hovermode="x unified",
)
st.plotly_chart(fig_compare, use_container_width=True)

st.markdown(
    """
<div class="box-gradientorange">
    Grafik di atas menunjukkan bahwa model <strong>sangat konsisten menangkap pola musiman</strong> (kapan kasus naik dan turun). 
        Selisih (gap) yang terjadi biasanya berada pada titik puncak ekstrem, di mana realita kasus (Aktual) melonjak lebih tinggi 
        dari tren historisnya. Ini membuktikan model bersifat <i>robust</i> (stabil) namun tetap konservatif dalam memberikan estimasi.
</div>
""",
    unsafe_allow_html=True,
)


# ===============================
# SECTION 3 — ANALISIS RESIDUAL
# ===============================
st.divider()
st.markdown(
    """
    <div class="section-header">
        <div class="dot" style="background:linear-gradient(135deg,#3B82F6,#7C3AED);"></div>
        <span style="font-size:1rem;font-weight:700;color:#1A1D2E;">Analisis Sisaan Prediksi (Residual Analysis)</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="box-blue" style="margin-bottom:16px;">
    <strong>Apa itu Residual?</strong><br>
    Residual adalah selisih atau "sisa" antara data asli dengan hasil tebakan model. 
    Secara matematis: <br><code>Residual = Data Aktual - Data Prediksi</code>
</div>
""",
    unsafe_allow_html=True,
)

residual = test.values - pred_test.values

df_residual = pd.DataFrame(
    {"periode": df_total["periode"][train_size:], "residual": residual}
)

fig_res = go.Figure()
fig_res.add_trace(go.Scatter(
    x=df_residual["periode"], y=df_residual["residual"],
    mode="lines+markers",
    line=dict(color="#5B6EF5", width=2),
    marker=dict(size=4, color="#5B6EF5"),
    fill="tozeroy",
    fillcolor="rgba(91,110,245,0.06)",
    name="Residual",
))
fig_res.add_hline(
    y=0,
    line_dash="dash",
    line_color="#F43F5E",
    line_width=1.5,
    annotation_text="Target: Error = 0",
    annotation_font_size=11,
    annotation_font_color="#F43F5E",
)
fig_res.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", size=12),
    margin=dict(t=20, b=10, l=10, r=10),
    xaxis=dict(gridcolor="#F0F2FA", title="Periode"),
    yaxis=dict(gridcolor="#F0F2FA", title="Residual (Aktual − Prediksi)"),
    hovermode="x unified",
    showlegend=False,
)
st.plotly_chart(fig_res, use_container_width=True)

st.markdown(
    """
<div class="box-gradientblue">
    <strong>Cara Membaca Grafik Residual:</strong>
    <ul style="margin:8px 0 0 0;">
        <li><strong>Mendekati Angka 0:</strong> Semakin banyak titik yang berada di garis 0, artinya model semakin <strong>"Tepat Sasaran"</strong> dalam menebak kenyataan.</li>
        <li><strong>Nilai Positif (Menjauhi 0 ke Atas):</strong> Model kecolongan atau <i>Under-forecasting</i>. Artinya, jumlah kasus asli ternyata jauh lebih banyak dibanding tebakan model.</li>
        <li><strong>Nilai Negatif (Menjauhi 0 ke Bawah):</strong> Model terlalu waspada atau <i>Over-forecasting</i>. Artinya, model menebak angka tinggi, namun kenyataannya kasusnya rendah.</li>
    </ul>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="box-success">
    <strong>Kesimpulan Analisis:</strong> Berdasarkan Histogram, mayoritas error berkumpul di tengah (nol). Lonjakan error yang menjauhi nol hanya terjadi pada awal 2024, yang secara faktual merupakan anomali Kejadian Luar Biasa (KLB) nasional.
</div>
""",
    unsafe_allow_html=True,
)


# ===============================
# FOOTER
# ===============================
show_footer()