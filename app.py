import streamlit as st
from groq import Groq
import json
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Museum Batik Indonesia",
    page_icon="🎨",
    layout="wide"
)

# --- API KEY ---
# (Menggunakan key yang Anda berikan sebelumnya agar langsung jalan)
GROQ_API_KEY = "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"

# --- CUSTOM CSS (TEMA BATIK) ---
st.markdown("""
    <style>
    /* 1. Latar Belakang Utama (Warna Krem Kain Mori) */
    .stApp {
        background-color: #fdfcf0;
        color: #3e2723;
    }

    /* 2. Sidebar (Warna Cokelat Tua Batik Sogan) */
    [data-testid="stSidebar"] {
        background-color: #4e342e;
        border-right: 5px solid #d7ccc8;
    }
    
    /* Teks di Sidebar */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] span, [data-testid="stSidebar"] p {
        color: #ffecb3 !important; /* Warna Emas */
        font-family: 'Georgia', serif;
    }

    /* 3. Judul Utama */
    h1 {
        color: #3e2723;
        font-family: 'Playfair Display', serif;
        text-align: center;
        border-bottom: 2px solid #8d6e63;
        padding-bottom: 10px;
    }

    /* 4. Chat Bubbles */
    /* Pesan User (Warna Cokelat Muda) */
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: #d7ccc8;
        border-radius: 15px;
        border: 1px solid #a1887f;
    }
    
    /* Pesan Asisten (Warna Emas Pucat) */
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background-color: #fff8e1;
        border-radius: 15px;
        border: 1px solid #ffecb3;
    }

    /* 5. Tombol */
    .stButton>button {
        background-color: #5d4037;
        color: white;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    if os.path.exists('dataset_museum_batik.json'):
        with open('dataset_museum_batik.json', 'r') as f:
            return json.load(f)
    return None

museum_data = load_data()

# --- SIDEBAR CONTENT ---
with st.sidebar:
    # Menambahkan Gambar Batik (URL Publik)
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Batik_Parang_Klitik.jpg/220px-Batik_Parang_Klitik.jpg", use_container_width=True)
    
    st.title("🏛️ Info Praktis")
    
    if museum_data:
        st.markdown("---")
        st.subheader("📍 Lokasi")
        st.write(museum_data['informasi_umum']['lokasi']['alamat'])
        
        st.markdown("---")
        with st.expander("🎫 Harga Tiket", expanded=True):
            st.write(f"**Dewasa:** Rp{museum_data['harga_tiket']['dewasa']:,}")
            st.write(f"**Mancanegara:** Rp{museum_data['harga_tiket']['wisatawan_mancanegara']:,}")
            st.write(f"**Anak-anak:** Rp{museum_data['harga_tiket']['anak_anak']:,}")
        
        st.markdown("---")
        st.caption("© Museum Batik Indonesia AI")

# --- MAIN CONTENT ---
st.title("🌸 Asisten Virtual Museum Batik")
st.markdown("<p style='text-align: center; color: #5d4037;'><em>Bertanya seputar koleksi, filosofi motif, dan layanan museum.</em></p>", unsafe_allow_html=True)

if not museum_data:
    st.error("⚠️ File 'dataset_museum_batik.json' belum diunggah ke GitHub!")
    st.stop()

# Inisialisasi Groq
client = Groq(api_key=GROQ_API_KEY)

# Session State Chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Sugeng Rawuh! 🙏 Saya asisten Museum Batik. Ada yang ingin Anda tanyakan tentang motif Batik atau jadwal workshop?"}
    ]

# Tampilkan Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input Chat
if prompt := st.chat_input("Contoh: Apa makna motif Parang?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # System Prompt
    system_prompt = f"""
    Kamu adalah pemandu wisata digital Museum Batik Indonesia yang sopan dan berwawasan luas.
    Gunakan data berikut untuk menjawab: {json.dumps(museum_data)}
    
    Gaya Bicara:
    - Gunakan bahasa Indonesia yang baik, sedikit formal namun ramah.
    - Jika relevan, gunakan sapaan sopan.
    - Jelaskan filosofi batik dengan mendalam jika ditanya.
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
        st.error(f"Terjadi kesalahan koneksi: {e}")
