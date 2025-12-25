import streamlit as st
from groq import Groq
import json
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Asisten Museum Batik",
    page_icon="🏛️",
    layout="wide"
)

# --- API KEY ---
# Key dimasukkan langsung agar chatbot otomatis berjalan
GROQ_API_KEY = "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"

# --- FUNGSI LOAD DATA ---
@st.cache_data
def load_data():
    file_path = 'dataset_museum_batik.json'
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return None

museum_data = load_data()

# --- SIDEBAR (INFORMASI) ---
with st.sidebar:
    st.header("🏛️ Info Museum")
    
    if museum_data:
        st.subheader("📍 Lokasi")
        st.write(museum_data['informasi_umum']['lokasi']['alamat'])
        
        st.divider()
        
        st.subheader("🎫 Harga Tiket")
        st.write(f"**Dewasa:** Rp{museum_data['harga_tiket']['dewasa']:,}")
        st.write(f"**Pelajar:** Rp{museum_data['harga_tiket']['pelajar_mahasiswa']:,}")
        st.write(f"**Mancanegara:** Rp{museum_data['harga_tiket']['wisatawan_mancanegara']:,}")
    else:
        st.warning("Data museum tidak ditemukan.")

    st.divider()
    st.caption("Asisten Virtual Museum Batik Indonesia")

# --- HALAMAN UTAMA ---
st.title("Asisten Virtual Museum Batik")
st.write("Selamat datang! Silakan tanyakan informasi seputar koleksi batik, harga tiket, atau jadwal workshop.")

# Cek Data
if not museum_data:
    st.error("⚠️ File 'dataset_museum_batik.json' belum diunggah ke GitHub.")
    st.stop()

# Inisialisasi Client Groq
client = Groq(api_key=GROQ_API_KEY)

# --- LOGIKA CHATBOT ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Halo! Ada yang bisa saya bantu terkait Museum Batik hari ini?"}
    ]

# Menampilkan Riwayat Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input Chat User
if prompt := st.chat_input("Ketik pertanyaan Anda di sini..."):
    # Simpan & Tampilkan Pesan User
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Context untuk AI
    system_prompt = f"""
    Anda adalah asisten AI untuk Museum Batik Indonesia.
    Tugas Anda adalah menjawab pertanyaan pengunjung dengan ramah dan akurat.
    
    Gunakan data berikut sebagai referensi utama:
    {json.dumps(museum_data)}
    
    Jika pertanyaan di luar konteks museum atau batik, jawablah dengan sopan bahwa Anda hanya melayani informasi seputar museum.
    """
    
    try:
        # Request ke Groq (Llama 3)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        response_text = completion.choices[0].message.content
        
        # Simpan & Tampilkan Respon AI
        with st.chat_message("assistant"):
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            
    except Exception as e:
        st.error(f"Terjadi kesalahan koneksi: {e}")
