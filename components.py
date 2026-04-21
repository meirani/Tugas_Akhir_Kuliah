import streamlit as st


def show_footer():
    """Fungsi untuk menampilkan footer seragam di semua halaman"""
    st.markdown(
        """
        <div class="footer">
            <hr>
            © 2026 | Skripsi Nabila Winanda Meirani - H1D022108 | Informatics Engineering
        </div>
        """,
        unsafe_allow_html=True,
    )


def local_css(file_name):
    """Fungsi untuk meload file CSS (biar sekalian DRY juga!)"""
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
