!pip install -q streamlit groq pyngrok

from pyngrok import ngrok
NGROK_AUTH_TOKEN = "37IBwFJFFCDX0jcYa7YZhLe9jQy_4P3KPbdPnJvNw8xa8efFf" 
ngrok.set_auth_token(NGROK_AUTH_TOKEN)

%%writefile app.py
import streamlit as st
from groq import Groq
import json
import os

# --- KONFIGURASI API (Hardcoded agar orang luar langsung pakai) ---
GROQ_API_KEY = "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" # <--- GANTI INI

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Virtual Assistant Museum Batik", 
    page_icon="🎨", 
    layout="wide"
)

# --- CUSTOM CSS (Mempercantik Tampilan) ---
st.markdown("""
    <style>
    .main { background-color: #fcf8f2; }
    .stChatMessage { border-radius: 15px; border: 1px solid #e0d5c1; }
    .stTitle { color: #5d4037; font-family: 'Georgia', serif; font-weight: bold; }
    .sidebar .sidebar-content { background-image: linear-gradient(#5d4037, #8d6e63); color: white; }
    div.stButton > button:first-child { background-color: #8d6e63; color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOAD DATASET ---
def load_data():
    if os.path.exists('dataset_museum_batik.json'):
        with open('dataset_museum_batik.json', 'r') as f:
            return json.load(f)
    return None

museum_data = load_data()

# --- SIDEBAR (Informasi Cepat) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3256/3256150.png", width=100)
    st.title("🏛️ Info Museum")
    if museum_data:
        st.info(f"📍 **Lokasi:**\n{museum_data['informasi_umum']['lokasi']['alamat']}")
        
        with st.expander("🎫 Harga Tiket"):
            st.write(f"Dewasa: Rp{museum_data['harga_tiket']['dewasa']:,}")
            st.write(f"Pelajar: Rp{museum_data['harga_tiket']['pelajar_mahasiswa']:,}")
            st.write(f"Mancanegara: Rp{museum_data['harga_tiket']['wisatawan_mancanegara']:,}")
            st.caption(f"Gratis: {museum_data['harga_tiket']['gratis']}")
        
        with st.expander("⏰ Jam Buka"):
            st.write(f"Biasa: {museum_data['jam_operasional']['hari_biasa']}")
            st.write(f"Weekend: {museum_data['jam_operasional']['akhir_pekan']}")
    
    st.divider()
    st.caption("Powered by Groq AI - Llama 3.3")

# --- HEADER UTAMA ---
col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/1048/1048953.png", width=120)
with col2:
    st.title("Asisten Virtual Museum Batik")
    st.markdown("*Pelestarian, Edukasi, dan Dokumentasi Batik Nusantara*")

st.divider()

# --- LOGIKA CHATBOT ---
client = Groq(api_key=GROQ_API_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Halo! Saya asisten virtual Museum Batik. Ada yang bisa saya bantu terkait koleksi, harga tiket, atau teknik membatik?"}
    ]

# Tampilkan chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input Chat
if prompt := st.chat_input("Tanyakan sesuatu..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Persiapan Context
    system_prompt = f"""
    Anda adalah asisten Museum Batik Indonesia yang ramah.
    Gunakan data resmi ini untuk menjawab: {json.dumps(museum_data)}
    Gunakan bahasa Indonesia yang sopan. Jika bertanya harga, sebutkan angka dengan format Rupiah.
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
        st.error(f"Gagal memproses pesan: {e}")
