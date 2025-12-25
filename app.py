import streamlit as st
from groq import Groq
import json
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Museum Batik: Nuansa Alam",
    page_icon="🌿",
    layout="wide"
)

# --- API KEY (Hardcoded sesuai request) ---
GROQ_API_KEY = "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"

# --- CUSTOM CSS (TEMA COKLAT & HIJAU) ---
st.markdown("""
    <style>
    /* 1. Latar Belakang Utama (Krem Kehijauan lembut) */
    .stApp {
        background-color: #f1f8e9; 
        color: #3e2723; /* Teks Cokelat Tua */
    }

    /* 2. Sidebar (Hijau Tua Alami) */
    [data-testid="stSidebar"] {
        background-color: #33691e; /* Hijau Daun Tua */
        color: white;
    }
    
    /* Teks di Sidebar (Putih Gading) */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] span, [data-testid="stSidebar"] p {
        color: #f1f8e9 !important;
        font-family: 'Segoe UI', sans-serif;
    }

    /* 3. Judul Utama (Cokelat Kayu) */
    h1 {
        color: #4e342e;
        font-family: 'Georgia', serif;
        text-align: center;
        border-bottom: 3px solid #558b2f; /* Garis Bawah Hijau */
        padding-bottom: 15px;
    }
    
    /* Subjudul */
    h3 {
        color: #558b2f; /* Hijau Cerah */
    }

    /* 4. Chat Bubbles (Balon Percakapan) */
    
    /* User (Hijau Muda Segar) */
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: #dcedc8;
        border: 1px solid #aed581;
        border-radius: 20px 20px 0px 20px;
    }
    
    /* Assistant (Cokelat Muda Hangat) */
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background-color: #efebe9;
        border: 1px solid #d7ccc8;
        border-radius: 20px 20px 20px 0px;
    }

    /* 5. Tombol Input & Send */
    .stButton>button {
        background-color: #4e342e; /* Tombol Cokelat */
        color: white;
        border-radius: 8px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #6d4c41; /* Cokelat lebih terang saat hover */
    }
    
    /* 6. Info Box/Expander */
    .streamlit-expanderHeader {
        background-color: #c5e1a5; /* Hijau Pastel */
        color: #33691e;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOAD DATASET ---
@st.cache_data
def load_data():
    if os.path.exists('dataset_museum_batik.json'):
        with open('dataset_museum_batik.json', 'r') as f:
            return json.load(f)
    return None

museum_data = load_data()

# --- SIDEBAR (INFO MUSEUM) ---
with st.sidebar:
    st.title("🌿 Museum Info")
    st.markdown("---")
    
    if museum_data:
        st.subheader("📍 Lokasi")
        st.caption(museum_data['informasi_umum']['lokasi']['alamat'])
        
        st.markdown("---")
        
        with st.expander("🎫 Tiket Masuk", expanded=True):
            st.markdown(f"**Dewasa:** \nRp{museum_data['harga_tiket']['dewasa']:,}")
            st.markdown(f"**Pelajar:** \nRp{museum_data['harga_tiket']['pelajar_mahasiswa']:,}")
            st.markdown(f"**Asing:** \nRp{museum_data['harga_tiket']['wisatawan_mancanegara']:,}")
        
        st.markdown("---")
        st.info("💡 **Tips:** Tanyakan tentang 'Motif Semen' atau 'Batik Pesisir'.")

# --- MAIN PAGE ---
st.title("Asisten Batik Nusantara")
st.markdown("<div style='text-align: center;'><em>Menjelajahi Keindahan Warisan Budaya dengan Nuansa Alam</em></div>", unsafe_allow_html=True)
st.divider()

if not museum_data:
    st.error("⚠️ Data museum tidak ditemukan. Mohon cek file JSON di GitHub.")
    st.stop()

# --- LOGIKA CHATBOT ---
client = Groq(api_key=GROQ_API_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Halo! Saya siap menemani Anda menjelajahi dunia Batik. Ada yang ingin ditanyakan?"}
    ]

# Render Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input User
if prompt := st.chat_input("Tulis pertanyaan Anda di sini..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prompt System
    system_prompt = f"""
    Anda adalah pemandu museum yang ramah dan mencintai budaya.
    Jawablah pertanyaan berdasarkan data berikut: {json.dumps(museum_data)}
    Gunakan bahasa yang santai namun sopan.
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
        )
        response_text = completion.choices[0].message.content
        with st.chat_message("assistant"):
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
    except Exception as e:
        st.error(f"Koneksi terputus: {e}")
