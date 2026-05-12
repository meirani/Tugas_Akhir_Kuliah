import streamlit as st
import pandas as pd
import glob
from components import show_footer, local_css

# ===============================
# CONFIG & CSS
# ===============================
st.set_page_config(page_title="Tambah Data - DBD", layout="wide", page_icon="➕")
local_css("style.css")

# ===============================
# HELPER: load semua CSV di folder data/
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
    df = pd.concat(semua_df, ignore_index=True)
    df["periode"] = pd.to_datetime(df["periode"])
    df["tahun"] = df["tahun"].astype(int)
    df["bulan"] = df["bulan"].astype(int)
    df = df.drop_duplicates(subset=["kecamatan", "periode"])
    df = df.sort_values("periode").reset_index(drop=True)
    return df

# ===============================
# INISIALISASI SESSION STATE
# ===============================
if "df_main" not in st.session_state:
    st.session_state["df_main"] = load_semua_data()

if "data_ditambah" not in st.session_state:
    st.session_state["data_ditambah"] = False

# ===============================
# HEADER
# ===============================
st.markdown(
    """
    <div class="hero-container" style="padding-bottom: 0;">
        <div class="hero-badge">Simulasi Data</div>
        <span class="title-highlight" style="font-size: 2.4rem;">Form Tambah Data</span>
        <span class="title-secondary">Upload data baru untuk simulasi analisis dan prediksi kasus DBD</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ===============================
# INFO STATUS DATA
# ===============================
df_current = st.session_state["df_main"]
min_periode = df_current["periode"].min().strftime("%B %Y")
max_periode = df_current["periode"].max().strftime("%B %Y")
total_rows = len(df_current)

if st.session_state["data_ditambah"]:
    st.success(
        f"Data simulasi aktif: **{total_rows:,} baris** | "
        f"Periode: **{min_periode} – {max_periode}**. "
    )
else:
    st.info(
        f"Data default: **{total_rows:,} baris** | "
        f"Periode: **{min_periode} – {max_periode}**"
    )

st.divider()

# ===============================
# PANDUAN FORMAT
# ===============================
st.subheader("Panduan Format CSV")
st.markdown(
    "File CSV yang diupload harus memiliki kolom berikut **persis sama** dengan dataset asli:"
)

st.code(
    "kecamatan,periode,jumlah_kasus,tahun,bulan,nama_bulan,musim",
    language="text"
)

st.markdown("**Contoh isi data:**")
contoh_data = pd.DataFrame({
    "kecamatan": ["Cakung", "Koja", "Penjaringan"],
    "periode": ["2026-01-01", "2026-01-01", "2026-01-01"],
    "jumlah_kasus": [65, 43, 38],
    "tahun": [2026, 2026, 2026],
    "bulan": [1, 1, 1],
    "nama_bulan": ["January", "January", "January"],
    "musim": ["Musim Hujan", "Musim Hujan", "Musim Hujan"],
})
st.dataframe(contoh_data, hide_index=True, use_container_width=True)

with st.expander("Referensi klasifikasi musim"):
    st.markdown("""
    | Periode Bulan | Klasifikasi Musim |
    |---|---|
    | Desember, Januari, Februari | Musim Hujan |
    | Maret, April, Mei | Pancaroba I |
    | Juni, Juli, Agustus | Musim Kemarau |
    | September, Oktober, November | Pancaroba II |
    """)

st.divider()

# ===============================
# UPLOAD FILE
# ===============================
st.subheader("📂 Upload Data Baru")

uploaded_file = st.file_uploader(
    "Pilih file CSV data DBD baru",
    type=["csv"],
    help="File harus mengikuti format kolom yang sudah ditentukan di atas.",
)

if uploaded_file is not None:
    try:
        df_new = pd.read_csv(uploaded_file)

        # Validasi kolom
        kolom_wajib = ["kecamatan", "periode", "jumlah_kasus", "tahun", "bulan", "nama_bulan", "musim"]
        kolom_hilang = [k for k in kolom_wajib if k not in df_new.columns]

        if kolom_hilang:
            st.error(f"Kolom berikut tidak ditemukan di file: **{', '.join(kolom_hilang)}**. Periksa kembali format CSV kamu.")
        else:
            df_new["periode"] = pd.to_datetime(df_new["periode"])
            df_new["tahun"] = df_new["tahun"].astype(int)
            df_new["bulan"] = df_new["bulan"].astype(int)
            df_new["jumlah_kasus"] = df_new["jumlah_kasus"].astype(int)

            # Preview
            st.markdown("**Preview data yang akan ditambahkan:**")
            st.dataframe(df_new, hide_index=True, use_container_width=True)

            periode_baru = df_new["periode"].dt.strftime("%B %Y").unique().tolist()
            kecamatan_baru = df_new["kecamatan"].nunique()
            jumlah_kecamatan_default = st.session_state["df_main"]["kecamatan"].nunique()

            st.markdown(
                f"Data mencakup **{kecamatan_baru} kecamatan** "
                f"pada periode: **{', '.join(periode_baru)}**"
            )

            # Warning jika kecamatan tidak lengkap
            if kecamatan_baru < jumlah_kecamatan_default:
                st.warning(
                    f"⚠️ Data hanya mencakup **{kecamatan_baru} dari {jumlah_kecamatan_default} kecamatan**. "
                    f"Data yang tidak lengkap dapat mempengaruhi akurasi hasil prediksi."
                )

            st.divider()

            col_btn1, col_btn2 = st.columns([1, 1], gap="large")

            with col_btn1:
                if st.button("Tambahkan ke Simulasi", type="primary", use_container_width=True):
                    # Load ulang semua file di folder data/ sebagai base
                    df_default = load_semua_data()

                    df_combined = pd.concat([df_default, df_new], ignore_index=True)
                    df_combined = df_combined.drop_duplicates(subset=["kecamatan", "periode"])
                    df_combined = df_combined.sort_values("periode").reset_index(drop=True)

                    st.session_state["df_main"] = df_combined
                    st.session_state["data_ditambah"] = True
                    st.rerun()

            with col_btn2:
                if st.session_state["data_ditambah"]:
                    if st.button("🔄 Reset ke Data Default", use_container_width=True):
                        st.session_state["df_main"] = load_semua_data()
                        st.session_state["data_ditambah"] = False
                        st.rerun()

    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca file: {e}")

else:
    if st.session_state["data_ditambah"]:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Reset ke Data Default", type="secondary"):
            st.session_state["df_main"] = load_semua_data()
            st.session_state["data_ditambah"] = False
            st.rerun()

# ===============================
# FOOTER
# ===============================
show_footer()