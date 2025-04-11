import pandas as pd
import streamlit as st
from datetime import datetime


@st.cache_data(show_spinner="Veri yükleniyor...")
def load_data(uploaded_file):
    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
        df.columns = [str(col).strip() for col in df.columns]

        # Zorunlu sütun kontrolü
        mandatory_columns = ["Masraf Yeri Adı", "Kümüle Bütçe", "Kümüle Fiili"]
        missing_columns = [col for col in mandatory_columns if col not in df.columns]
        if missing_columns:
            st.error(
                f"Eksik sütunlar: {', '.join(missing_columns)}. Lütfen geçerli bir ZFMR0003 raporu yükleyin."
            )
            return None

        return df
    except Exception as e:
        st.error(f"Veri yükleme hatası: {str(e)}")
        # Hata detayını logla (opsiyonel)
        with open("error_log.txt", "a") as f:
            f.write(f"{datetime.now()}: {str(e)}\n")
        return None
