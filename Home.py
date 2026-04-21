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
        <span class="title-highlight">Analisis Tren dan Prediksi<br>Kasus Demam Berdarah Dengue</span>
        <span class="title-secondary">di DKI Jakarta Menggunakan Model Time Series ARIMA<br>Periode 2010 - 2025</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.image("assets/virusdengue.png", use_container_width=True)

with st.container():
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
        Demam berdarah dengue (DBD) adalah penyakit yang ditularkan oleh gigitan nyamuk bernama *Aedes aegypti*. 
        Penyakit ini masih menjadi salah satu isu kesehatan masyarakat di Indonesia, 
        dan tingkat penyebarannya di Indonesia termasuk yang tertinggi di antara negara-negara Asia Tenggara.

        DKI Jakarta merupakan salah satu wilayah dengan kasus DBD yang cukup tinggi di Indonesia. Faktor seperti kepadatan penduduk, lingkungan, dan perubahan musim sangat mempengaruhi 
        peningkatan kasus setiap tahunnya.
        """
        )

    with col2:
        st.image(
            "assets/nyamuk.jpg",
            caption="Nyamuk Aedes aegypti",
            use_container_width=True,
        )


# ===============================
# TUJUAN PENELITIAN
# ===============================
st.write("---")
with st.container():
    st.subheader("Tujuan Penelitian")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(
            """
        <div class="box-blue">
            • Menganalisis tren kasus DBD di DKI Jakarta (2010–2025)<br>
            • Membangun model prediksi menggunakan metode Seasonal ARIMA
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col_b:
        st.markdown(
            """
        <div class="box-blue">
            • Memprediksi jumlah kasus DBD di DKI Jakarta tahun 2026<br>
            • Menentukan wilayah prioritas berdasarkan estimasi risiko
        </div>
        """,
            unsafe_allow_html=True,
        )


# ===============================
# METODOLOGI & FITUR
# ===============================
st.write("---")
m1, m2 = st.columns(2)

with m1:
    st.subheader("Metodologi")
    inner_col1, inner_col2 = st.columns(2)

    with inner_col1:
        st.markdown(
            """
        <div class="box-purple">
            <strong>Metode:</strong><br>
            • Time Series<br>
            • Seasonal ARIMA
        </div>
        """,
            unsafe_allow_html=True,
        )

    with inner_col2:
        st.markdown(
            """
        <div class="box-purple">
            <strong>Evaluasi:</strong><br>
            • MAE<br>
            • MAPE<br>
            • RMSE
        </div>
        """,
            unsafe_allow_html=True,
        )

with m2:
    st.subheader("Fitur Aplikasi")
    st.markdown(
        """
    | Fitur | Deskripsi |
    | :--- | :--- |
    | **Analisis Tren** | Pola kasus & musim |
    | **Prediksi** | Forecast tahun 2026 |
    | **Evaluasi** | Performa model |
    | **Early Warning** | Wilayah risiko tinggi |
    """
    )


# ===============================
# INSIGHT AWAL & PENUTUP
# ===============================
st.write("---")
c1, c2 = st.columns([1, 1])

with c1:
    st.subheader("Insight Awal")
    st.markdown(
        """
    <div class="box-outline">
        Kasus DBD di DKI Jakarta cenderung meningkat pada periode <strong>pancaroba I</strong>, 
        terutama pada bulan <strong>Maret hingga Mei</strong>, yang menunjukkan adanya pola musiman yang kuat.
    </div>
    """,
        unsafe_allow_html=True,
    )

with c2:
    st.subheader("Kesimpulan")
    st.markdown(
        """
    <div class="box-outline">
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
