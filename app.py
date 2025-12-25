import streamlit as st
from groq import Groq
import json
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Asisten Museum Batik",
    page_icon="👑",
    layout="wide"
)

# --- API KEY (Hardcoded) ---
GROQ_API_KEY = "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"

# --- CUSTOM CSS (TEMA PREMIUM) ---
st.markdown("""
    <style>
    /* 1. Latar Belakang Utama (Ivory/Putih Gading) - Bersih & Terang */
    .stApp {
        background-color: #fbf7f5;
        color: #2b2b2b;
    }

    /* 2. Sidebar (Cokelat Tua Mewah) */
    [data-testid="stSidebar"] {
        background-color: #3e2723;
        border-right: 1px solid #d7ccc8;
    }
    
    /* Teks Sidebar */
    [data-testid="stSidebar"] * {
        color: #ffecb3 !important; /* Warna Emas Pucat */
    }
    [data-testid="stSidebar"] hr {
        border-color: #8d6e63;
    }

    /* 3. Judul Utama */
    h1 {
        font-family: 'Playfair Display', serif;
        color: #3e2723;
        text-align: center;
        font-weight: 700;
        margin-bottom: 30px;
    }
    h3 {
        font-family: 'Playfair Display', serif;
        color: #5d4037;
    }

    /* 4. Chat Bubbles (Perbaikan Kontras) */
    
    /* USER: Cokelat Elegan (Teks Putih) */
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: #5d4037;
        color: #ffffff;
        border-radius: 20px 20px 5px 20px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    /* Paksa teks user jadi putih */
    .stChatMessage[data-testid="stChatMessageUser"] p {
        color: #ffffff !important;
    }
    
    /* ASSISTANT: Putih Bersih (Teks Hitam) */
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background-color: #ffffff;
        border: 1px solid #d7ccc8;
        border-radius: 20px 20px 20px 5px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .stChatMessage[data-testid="stChatMessageAssistant"] p {
        color: #3e2723 !important;
    }

    /* 5. Input Field */
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 1px solid #8d6e63;
        padding: 10px 20px;
    }
    
    /* 6. Fix Glitch Icon Panah */
    .material-icons {
        display: none !important; /* Menyembunyikan teks icon yang bocor */
    }
    </style>
    
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

# --- LOAD DATASET ---
@st.cache_data
def load_data():
    if os.path.exists('dataset_museum_batik.json'):
        with open('dataset_museum_batik.json', 'r') as f:
            return json.load(f)
    return None

museum_data = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.title("🏛️ Info Museum")
    st.markdown("---")
    
    if museum_data:
        st.subheader("📍 Alamat")
        st.caption(museum_data['informasi_umum']['lokasi']['alamat'])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Expander tanpa glitch
        with st.expander("🎫 Harga Tiket", expanded=True):
            st.markdown(f"""
            - **Dewasa**: Rp{museum_data['harga_tiket']['dewasa']:,}
            - **Pelajar**: Rp{museum_data['
