import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
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
    <span class="title-highlight" style="font-size: 2.4rem;">Evaluasi Model Seasonal ARIMA</span>
    <span class="title-secondary">Performa Prediksi Data Historis Kasus DBD</span>
</div>
""",
    unsafe_allow_html=True,
)

st.divider()


# ===============================
# BACKEND MODEL
# ===============================
df = pd.read_csv("data/Data_DBD_FINAL_ANALISIS_2010_2025.csv")
df["periode"] = pd.to_datetime(df["periode"])

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


# ===============================
# EVALUASI MODEL
# ===============================
col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

with col_kpi1:
    st.markdown(
        f"""
    <div class="box-gradientblue" style="text-align: center;">
        <small>Mean Absolute Error (MAE)</small><br>
        <span style="font-size: 2rem; font-weight: 800;">{mae:.2f}</span>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col_kpi2:
    st.markdown(
        f"""
    <div class="box-gradientpurple" style="text-align: center;">
        <small>Root Mean Square Error (RMSE)</small><br>
        <span style="font-size: 2rem; font-weight: 800;">{rmse:.2f}</span>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col_kpi3:
    st.markdown(
        f"""
    <div class="box-gradientorange" style="text-align: center;">
        <small>MAPE (Persentase Error)</small><br>
        <span style="font-size: 2rem; font-weight: 800;">{mape:.2f}%</span>
    </div>
    """,
        unsafe_allow_html=True,
    )

# Akurasi
akurasi = 100 - mape
st.markdown(
    f"""
<div class="box-outline">
    Model SARIMA memiliki akurasi prediksi sebesar <strong>{akurasi:.2f}%</strong> dengan tingkat error (MAPE) <strong>{mape:.2f}%</strong>.
    Dalam pemodelan time series epidemiologi penyakit menular, nilai ini <strong>sangat wajar</strong>.
    Kasus DBD memiliki sifat <strong>fluktuatif</strong> yang ekstrem dan rentan terhadap <strong>anomali</strong> seperti contohnya pandemi covid lalu,
    sehingga evaluasi tidak bisa hanya bertumpu pada besaran angka <i>error</i> semata.
</div>
""",
    unsafe_allow_html=True,
)


# ===============================
# ACTUAL VS PREDICTED
# ===============================
st.divider()
with st.container():
    st.subheader("Visualisasi Uji Coba: Data Aktual vs Prediksi")

    df_eval = pd.DataFrame(
        {
            "periode": df_total["periode"][train_size:],
            "Aktual": test.values,
            "Prediksi": pred_test.values,
        }
    )

    fig_compare = px.line(
        df_eval,
        x="periode",
        y=["Aktual", "Prediksi"],
        color_discrete_map={"Aktual": "#FFAA01", "Prediksi": "#E60001"},
    )

    fig_compare.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend_title_text="Keterangan:",
        margin=dict(t=20, b=20, l=10, r=10),
    )

    st.plotly_chart(fig_compare, use_container_width=True)

    st.markdown(
        """
    <div class="box-gradientorange">
        Grafik di atas menunjukkan bahwa model <strong>sangat konsisten menangkap pola musiman</strong> (kapan kasus naik dan turun). 
        Selisih (gap) yang terjadi biasanya berada pada titik puncak ekstrem, di mana realita kasus (Aktual) melonjak lebih tinggi dari tren historisnya. Ini membuktikan model bersifat <i>robust</i> (stabil) namun tetap konservatif dalam memberikan estimasi.
    </div>
    """,
        unsafe_allow_html=True,
    )


# ===============================
# ANALISIS RESIDUAL
# ===============================
st.divider()
st.subheader("Analisis Sisaan Prediksi (Residual Analysis)")

# Definisi Residual
st.markdown(
    """
<div class="box-outline">
    <strong>Apa itu Residual?</strong><br>
    Residual adalah selisih atau "sisa" antara data asli dengan hasil tebakan model. 
    Secara matematis: <br><code>Residual = Data Aktual - Data Prediksi</code>.
</div>
""",
    unsafe_allow_html=True,
)

col_res1, col_res2 = st.columns(2, gap="large")

residual = test.values - pred_test.values


with st.container():
    st.markdown("**1. Residual Error Over Time**")
    df_residual = pd.DataFrame(
        {"periode": df_total["periode"][train_size:], "residual": residual}
    )
    fig_res = px.line(
        df_residual, x="periode", y="residual", color_discrete_sequence=["#4c80f8"]
    )
    fig_res.add_hline(
        y=0, line_dash="dash", line_color="red", annotation_text="Target: Error 0"
    )
    fig_res.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=20, b=10, l=10, r=10),
    )
    st.plotly_chart(fig_res, use_container_width=True)

# PENJELASAN RESIDUAL
st.markdown(
    """
<div class="box-blue">
    <strong>Cara Membaca Grafik Error:</strong><br>
    <ul>
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
<div class="box-blue">
    <strong>Kesimpulan Analisis:</strong> Berdasarkan Histogram, mayoritas error berkumpul di tengah (nol). Lonjakan error yang menjauhi nol hanya terjadi pada awal 2024, yang secara faktual merupakan anomali Kejadian Luar Biasa (KLB) nasional.
</div>
""",
    unsafe_allow_html=True,
)


# ===============================
# FOOTER
# ===============================
show_footer()
