import streamlit as st
from groq import Groq
import json
import os

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Asisten Museum Batik",
    page_icon="🏺", # Ikon Guci/Artefak Museum
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. API KEY ---
GROQ_API_KEY = "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"

# --- 3. CUSTOM CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Lato:wght@400;700&display=swap');

    .stApp { background-color: #fdfbf7; color: #4a4a4a; font-family: 'Lato', sans-serif; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #3e2723; border-right: 2px solid #8d6e63; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 { color: #ffecb3 !important; font-family: 'Playfair Display', serif; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] div { color: #d7ccc8; }

    /* Judul */
    h1 { font-family: 'Playfair Display', serif; color: #3e2723; text-align: center; }
    .subtitle { text-align: center; color: #8d6e63; font-style: italic; margin-bottom: 2rem; }

    /* Chat Bubbles */
    .stChatMessage[data-testid="stChatMessageUser"] { background-color: #efebe9; border-left: 5px solid #5d4037; }
    .stChatMessage[data-testid="stChatMessageAssistant"] { background-color: #ffffff; border: 1px solid #e0e0e0; }
    
    /* Tombol */
    .stButton > button { border-radius: 20px; border: 1px solid #5d4037; color: #5d4037; background: white; }
    .stButton > button:hover { background: #5d4037; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- 4. LOAD DATA ---
@st.cache_data
def load_data():
    file_path = 'dataset_museum_batik.json'
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

museum_data = load_data()

# --- 5. SIDEBAR (DENGAN IKON BARU) ---
with st.sidebar:
    # IKON 1: Gunungan Wayang (Simbol Budaya Jawa/Batik)
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Wayang_Gunungan.svg/1200px-Wayang_Gunungan.svg.png", width=120)
    
    st.title("Info Museum")
    
    if museum_data:
        info = museum_data.get('informasi_umum', {}).get('identitas', {})
        tiket = museum_data.get('harga_tiket', {})

        st.markdown("---")
        with st.expander("📍 Lokasi", expanded=True):
            st.write(info.get('lokasi', {}).get('alamat', '-'))

        with st.expander("🎫 Tiket Masuk", expanded=True):
            st.write(f"**Dewasa:** Rp{tiket.get('dewasa', 0):,}")
            st.write(f"**Asing:** Rp{tiket.get('wisatawan_mancanegara', 0):,}")

    st.markdown("---")
    st.caption("© Museum Batik AI")

# --- 6. HEADER ---
st.markdown("<h1>Asisten Museum Batik</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Eksplorasi Kekayaan Warisan Nusantara</p>", unsafe_allow_html=True)

if not museum_data:
    st.error("⚠️ Data JSON tidak ditemukan.")
    st.stop()

# --- 7. CHAT LOGIC ---
client = Groq(api_key=GROQ_API_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Quick Reply Icons
if len(st.session_state.messages) == 0:
    col1, col2, col3 = st.columns(3)
    if col1.button("🎫 Cek Tiket"):
        st.session_state.messages.append({"role": "user", "content": "Berapa harga tiket?"})
    if col2.button("☁️ Motif Mega Mendung"): # Ikon Awan untuk Mega Mendung
        st.session_state.messages.append({"role": "user", "content": "Jelaskan filosofi batik Mega Mendung."})
    if col3.button("⚡ Rute Kilat"): # Ikon Petir untuk Cepat
        st.session_state.messages.append({"role": "user", "content": "Rekomendasi rute kunjungan singkat."})

# Render Chat (DENGAN AVATAR BARU)
for message in st.session_state.messages:
    # IKON 2: Avatar Chat
    if message["role"] == "user":
        # Ikon User (Orang biasa)
        avatar_icon = "🧑‍🎨" 
    else:
        # Ikon Bot (Menggunakan URL gambar Wayang/Blangkon style jika ada, atau emoji Pria Bersorban)
        # Kita pakai URL gambar Wayang icon agar unik
        avatar_icon = "https://cdn-icons-png.flaticon.com/512/3663/3663363.png" 
        
    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])

# --- 8. INPUT ---
if prompt := st.chat_input("Tanyakan tentang batik..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍🎨"):
        st.markdown(prompt)

    data_str = json.dumps(museum_data, ensure_ascii=False)
    system_prompt = f"Anda adalah Pemandu Museum Batik. Jawab berdasarkan: {data_str}. Gunakan bahasa sopan."
    
    try:
        with st.chat_message("assistant", avatar="https://cdn-icons-png.flaticon.com/512/3663/3663363.png"):
            message_placeholder = st.empty()
            full_response = ""
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_prompt}, *st.session_state.messages[-5:]],
                temperature=0.5, stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
    except Exception as e:
        st.error(f"Error: {e}")
