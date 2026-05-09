import streamlit as st
from components import show_footer, local_css

# ===============================
# CONFIG & CUSTOM CSS
# ===============================
st.set_page_config(page_title="Home - Prediksi DBD", layout="wide", page_icon="🦟")

local_css("style.css")


# ===============================
# HERO SECTION
# ===============================
st.markdown(
    """
    <div class="hero-container">
        <span class="title-highlight">Analisis Tren &amp; Prediksi<br>Kasus Demam Berdarah Dengue</span>
        <span class="title-secondary">di DKI Jakarta Menggunakan Model Time Series ARIMA  Periode 2010–2025</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.image("assets/virusdengue.png", use_container_width=True)

st.markdown(
    """
    <div class="box-gradientpurple">
        Sebuah aplikasi untuk <strong>Analisis</strong> tren historis dan <strong>Prediksi</strong> jumlah kasus 
        <strong>Demam Berdarah Dengue (DBD)</strong> di DKI Jakarta. Tersedia juga insight mengenai wilayah prioritas untuk membantu 
        upaya pencegahan penyakit.
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("---")


# ===============================
# TENTANG DBD
# ===============================
with st.container():
    st.subheader("Apa itu Demam Berdarah Dengue (DBD)?")
    col1, col2 = st.columns([2, 1], gap="large")

    with col1:
        st.markdown(
            """
            Demam berdarah dengue (DBD) adalah penyakit yang ditularkan melalui gigitan nyamuk 
            *Aedes aegypti*. Penyakit ini masih menjadi salah satu isu kesehatan masyarakat utama 
            di Indonesia, dengan tingkat penyebaran yang termasuk tertinggi di Asia Tenggara.

            **DKI Jakarta** merupakan salah satu wilayah dengan kasus DBD yang signifikan. 
            Faktor kepadatan penduduk, kondisi lingkungan, dan perubahan musim menjadi 
            pemicu utama peningkatan kasus setiap tahunnya.
            """
        )

    with col2:
        st.image(
            "assets/nyamuk.jpg",
            caption="Nyamuk Aedes Aegypti",
            use_container_width=True,
        )


# ===============================
# TUJUAN PENELITIAN
# ===============================
st.write("---")
with st.container():
    st.subheader("Tujuan Penelitian")

    col_a, col_b = st.columns(2, gap="medium")
    with col_a:
        st.markdown(
            """
            <div class="box-gradientblue">
                Menganalisis tren dan pola kasus DBD di DKI Jakarta periode 2010–2025.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="box-gradientblue">
                Membangun model prediksi menggunakan metode 
                Seasonal ARIMA (SARIMA) berbasis data time series.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_b:
        st.markdown(
            """
            <div class="box-gradientpurple">
                Memprediksi jumlah kasus DBD di DKI Jakarta untuk tahun 2026.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="box-gradientpurple">
                Menentukan wilayah prioritas berdasarkan estimasi risiko: 
                <span style="color:#F43F5E;font-weight:700;">Tinggi</span>, 
                <span style="color:#F59E0B;font-weight:700;">Sedang</span>, dan 
                <span style="color:#22C55E;font-weight:700;">Rendah</span>.
            </div>
            """,
            unsafe_allow_html=True,
        )


# ===============================
# METODOLOGI & FITUR
# ===============================
st.write("---")
m1, m2 = st.columns(2, gap="large")

with m1:
    st.subheader("Metodologi")

    inner_col1, inner_col2 = st.columns(2, gap="small")
    with inner_col1:
        st.markdown(
            """
            <div class="box-purple">
                <strong>Metode</strong><br><br>
                • Time Series Analysis<br>
                • Seasonal ARIMA (SARIMA)
            </div>
            """,
            unsafe_allow_html=True,
        )

    with inner_col2:
        st.markdown(
            """
            <div class="box-blue">
                <strong>Evaluasi Model</strong><br><br>
                • <strong>MAE</strong> (Mean Absolute Error)<br>
                • <strong>MAPE</strong> (Mean Absolute %)<br>
                • <strong>RMSE</strong> (Root Mean Square)
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="box-amber">
            <strong>Periode Data:</strong> Januari 2010 – Desember 2025<br>
            <strong>Cakupan:</strong> 44 kecamatan di setiap kota administrasi DKI Jakarta
        </div>
        """,
        unsafe_allow_html=True,
    )

with m2:
    st.subheader("Fitur Aplikasi")
    st.markdown(
        """
        <div class="box-outline">
            <strong>Analisis Tren</strong><br>
            Eksplorasi pola kasus DBD tahun ke tahun, per kecamatan, per bulan, dan per musim.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="box-outline">
            <strong>Prediksi 2026</strong><br>
            Visualisasi forecast kasus DBD tahun 2026 beserta pemetaan tingkat risiko 
            per kecamatan.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="box-outline">
            <strong>Evaluasi Model</strong><br>
            Performa model SARIMA lengkap dengan metrik MAE, MAPE, RMSE, 
            dan visualisasi distribusi error.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ===============================
# INSIGHT AWAL & PENUTUP
# ===============================
st.write("---")
st.subheader("Insight Awal & Kesimpulan")

c1, c2 = st.columns(2, gap="medium")

with c1:
    st.markdown(
        """
        <div class="risk-high">
            KKasus DBD di DKI Jakarta cenderung meningkat pada periode <strong>pancaroba I</strong>, 
            terutama pada bulan <strong>Maret hingga Mei</strong>, yang menunjukkan adanya pola musiman yang kuat.
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        """
        <div class="risk-low">
            Aplikasi ini diharapkan dapat membantu dalam memahami pola penyebaran DBD serta 
            memberikan informasi berguna bagi pengambilan keputusan di DKI Jakarta.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ===============================
# FOOTER
# ===============================
show_footer()