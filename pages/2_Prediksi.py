import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_absolute_error, mean_squared_error
from components import show_footer, local_css

# ===============================
# CSS dan Judul
# ===============================
st.set_page_config(page_title="Prediksi DBD", layout="wide", page_icon="📈")

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

st.markdown(
    """
<div class="hero-container" style="padding-bottom: 0;">
    <span class="title-highlight" style="font-size: 2.4rem;">Prediksi Kasus DBD 2026</span>
</div>
""",
    unsafe_allow_html=True,
)

st.divider()


# ===============================
# BACKEND MODEL
# ===============================

# LOAD DATA
df = pd.read_csv("data/Data_DBD_FINAL_ANALISIS_2010_2025.csv")
df["periode"] = pd.to_datetime(df["periode"])

# AGREGASI TOTAL DKI
df_total = df.groupby("periode")["jumlah_kasus"].sum().reset_index()
df_total = df_total.sort_values("periode")

# ADF TEST
adf_result = adfuller(df_total["jumlah_kasus"])

# SPLIT TRAIN TEST
train_size = int(len(df_total) * 0.8)
train = df_total["jumlah_kasus"][:train_size]
test = df_total["jumlah_kasus"][train_size:]

# MODEL SARIMA
model = SARIMAX(
    train,
    order=(2, 1, 2),
    seasonal_order=(2, 1, 1, 12),
    enforce_stationarity=False,
    enforce_invertibility=False,
)

results = model.fit(disp=False)

# PREDIKSI TEST
pred_test = results.predict(start=len(train), end=len(train) + len(test) - 1)

mae = mean_absolute_error(test, pred_test)
rmse = np.sqrt(mean_squared_error(test, pred_test))

# FORECAST 12 BULAN KE DEPAN
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


# ===============================
# GRAFIK PREDIKSI
# ===============================
fig_forecast = px.line(
    df_total,
    x="periode",
    y="jumlah_kasus",
    title="Prediksi Kasus DBD 2026",
    color_discrete_sequence=["#6c3ce5"],  
)

fig_forecast.add_scatter(
    x=df_forecast["periode"],
    y=df_forecast["prediksi_kasus"],
    mode="lines",
    name="Prediksi 2026",
    line=dict(
        color="#c8b8ef", width=3
    ),  
)

fig_forecast.add_scatter(
    x=df_forecast["periode"],
    y=df_forecast["upper_ci"],
    mode="lines",
    name="Upper CI",
    line=dict(dash="dash", color="#FF2701"),  
)

fig_forecast.add_scatter(
    x=df_forecast["periode"],
    y=df_forecast["lower_ci"],
    mode="lines",
    name="Lower CI",
    line=dict(dash="dash", color="#FFAA01"), 
)

st.plotly_chart(fig_forecast, use_container_width=True)

# PENJELASAN GRAFIK
peak_row = df_forecast.loc[df_forecast["prediksi_kasus"].idxmax()]
peak_month = peak_row["periode"].strftime("%B %Y")
peak_value = round(peak_row["prediksi_kasus"])

st.markdown(
    f"""
<div class="box-gradientpurple">
    Berdasarkan pemodelan <i>Seasonal ARIMA</i>, puncak kasus DBD di tahun 2026 diprediksi jatuh pada <strong>{peak_month}</strong> dengan estimasi <strong>{peak_value} kasus</strong>. Algoritma SARIMA berhasil menangkap pola siklus tahunan ini karena mayoritas lonjakan historis memang secara konsisten terjadi pada periode Pancaroba I (peralihan musim hujan ke kemarau).<br><br>
    Garis putus-putus pada grafik mewakili <strong>Rentang Kepercayaan (Confidence Interval / CI) 95%</strong>:
    <ul>
        <li><strong>Upper CI:</strong> Skenario terburuk (batas atas) jika terjadi anomali cuaca yang memperparah penyebaran.</li>
        <li><strong>Lower CI:</strong> Skenario terbaik (batas bawah). Pada perhitungan matematis, batas ini bisa bernilai negatif, namun dalam konteks epidemologi (jumlah orang sakit), nilai negatif tidaklah mungkin, sehingga kita batasi secara absolut di angka 0.</li>
    </ul>
</div>
""",
    unsafe_allow_html=True,
)


# ===============================
# TABEL & GRAFIK TOP 10
# ===============================
st.divider()
st.subheader("Estimasi Wilayah Prioritas DBD Tahun 2026")

# Perhitungan Estimasi
total_2026 = df_forecast["prediksi_kasus"].sum()
df_kecamatan = df.groupby("kecamatan")["jumlah_kasus"].sum().reset_index()
total_historis = df_kecamatan["jumlah_kasus"].sum()
df_kecamatan["proporsi"] = df_kecamatan["jumlah_kasus"] / total_historis
df_kecamatan["estimasi_2026"] = df_kecamatan["proporsi"] * total_2026

# Ambil Top 10
top_prioritas = df_kecamatan.sort_values("estimasi_2026", ascending=False).head(10)

# TABEL
df_table_kec = top_prioritas.copy()
df_table_kec["estimasi_2026"] = df_table_kec["estimasi_2026"].round(0)

st.markdown("**Tabel 10 Kecamatan dengan Estimasi Kasus Tertinggi**")
st.dataframe(
    df_table_kec[["kecamatan", "estimasi_2026"]],
    hide_index=True,
    use_container_width=True,
)

# BARCHART TOP 10
custom_color_scale = [
    "#FFAA01",  
    "#FA6F01",  
    "#FF5301",  
    "#F03B01",  
    "#EB1C01",  
    "#E60001",  
]

fig_prioritas = px.bar(
    top_prioritas,
    x="kecamatan",
    y="estimasi_2026",
    color="estimasi_2026",
    color_continuous_scale=custom_color_scale,
    title="Grafik Proporsi Top 10 Kecamatan Prioritas",
)

fig_prioritas.update_layout(coloraxis_showscale=False)
st.plotly_chart(fig_prioritas, use_container_width=True)

# PENJELASAN TOP 10
top1 = df_table_kec.iloc[0]
st.markdown(
    f"""
<div class="box-gradientorange">
    Kecamatan <strong>{top1['kecamatan']}</strong> menduduki peringkat pertama dengan estimasi mencapai <strong>{int(top1['estimasi_2026'])} kasus</strong>. 
    Metode ini mendistribusikan total prediksi DKI Jakarta berdasarkan bobot proporsi historis (2010-2025) masing-masing wilayah. Kecamatan yang masuk ke dalam Top 10 ini adalah wilayah yang secara historis terbukti memiliki kerentanan tinggi, yang umumnya berkorelasi dengan tingginya kepadatan penduduk dan karakteristik sanitasi lingkungan setempat.
</div>
""",
    unsafe_allow_html=True,
)


# ===============================
# KATEGORI RISIKO & FILTERING
# ===============================
st.divider()
st.subheader("Kategori Risiko DBD 2026 per Kecamatan")

df_risiko = df_kecamatan.copy()

# KATEGORI BERDASARKAN PERSENTIL
mean = df_kecamatan["estimasi_2026"].mean()
std = df_kecamatan["estimasi_2026"].std()

def kategori_risiko(x):
    if x >= mean + std:
        return "Tinggi 🔴"
    elif x >= mean:
        return "Sedang 🟡"
    else:
        return "Rendah 🟢"

df_risiko["kategori"] = df_risiko["estimasi_2026"].apply(kategori_risiko)
df_risiko["estimasi_2026"] = df_risiko["estimasi_2026"].round(0)

# FITUR FILTERING
options_risiko = ["Tinggi 🔴", "Sedang 🟡", "Rendah 🟢"]
selected_risiko = st.multiselect(
    "⚙️ Filter", options=options_risiko, default=options_risiko
)

df_risiko_filtered = df_risiko[df_risiko["kategori"].isin(selected_risiko)]

# TABEL RISIKO
st.dataframe(
    df_risiko_filtered.sort_values("estimasi_2026", ascending=False)[
        ["kecamatan", "estimasi_2026", "kategori"]
    ],
    hide_index=True,
    use_container_width=True,
)

# HEATMAP
df_risiko_sorted = df_risiko_filtered.sort_values("estimasi_2026", ascending=True)

fig_heatmap = px.bar(
    df_risiko_sorted,
    x="estimasi_2026",
    y="kecamatan",
    color="estimasi_2026",
    orientation="h",
    title="Heatmap Risiko DBD per Kecamatan 2026 (Filtered)",
    color_continuous_scale="Reds",
)
st.plotly_chart(fig_heatmap, use_container_width=True)

# PENJELASAN RISIKO
jumlah_tinggi = (df_risiko["kategori"] == "Tinggi 🔴").sum()
st.markdown(
    f"""
<div class="box-outline">
    <strong>Early Warning System</strong><br><br>
    Berdasarkan pengelompokan tingkat risiko menggunakan nilai rata-rata (mean) dan standar deviasi dari hasil prediksi kasus, terdapat <strong>{jumlah_tinggi} kecamatan</strong> yang berstatus Risiko Tinggi 🔴. 
    Melalui filter ini, Pengguna atau pembuat keputusan (Dinas Kesehatan) dapat langsung menyoroti wilayah yang paling rawan. Dengan begitu, tindakan pencegahan seperti fogging dan Pemberantasan Sarang Nyamuk (PSN) bisa langsung difokuskan pada zona merah, sebelum kasus DBD terlanjur meledak.
</div>
""",
    unsafe_allow_html=True,
)


# ===============================
# FOOTER
# ===============================
show_footer()
