import streamlit as st
from groq import Groq
import json
import os

# --- KONFIGURASI API ---
# Memasukkan API Key secara langsung
GROQ_API_KEY = "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"

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Asisten Virtual Museum Batik", 
    page_icon="🎨", 
    layout="wide"
)

# --- LOAD DATASET ---
@st.cache_data
def load_data():
    if os.path.exists('dataset_museum_batik.json'):
        with open('dataset_museum_batik.json', 'r') as f:
            return json.load(f)
    return None

museum_data = load_data()

# --- TAMPILAN SIDEBAR ---
with st.sidebar:
    st.title("🏛️ Museum Batik Indonesia")
    if museum_data:
        st.info(f"📍 **Lokasi:**\n{museum_data['informasi_umum']['lokasi']['alamat']}")
        st.write(f"🎫 **Tiket Dewasa:** Rp{museum_data['harga_tiket']['dewasa']:,}")
    st.divider()
    st.caption("Aplikasi Chatbot Museum")

# --- LOGIKA CHATBOT ---
st.title("🎨 Asisten Virtual Museum Batik")

if not museum_data:
    st.error("File 'dataset_museum_batik.json' tidak ditemukan di repository GitHub!")
    st.stop()

# Inisialisasi Groq dengan API Key yang Anda berikan
client = Groq(api_key=GROQ_API_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Halo! Saya asisten resmi Museum Batik. Ada yang bisa saya bantu?"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Tanyakan sesuatu..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Menggunakan model terbaru untuk menghindari error 'decommissioned'
    system_prompt = f"Anda adalah asisten Museum Batik Indonesia. Jawab berdasarkan data ini: {json.dumps(museum_data)}"
    
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
        st.error(f"Terjadi kesalahan: {e}")
