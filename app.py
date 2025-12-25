import streamlit as st
from groq import Groq
import json
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Museum Batik Indonesia",
    page_icon="jg",
    layout="wide"
)

# --- API KEY (Langsung di dalam kode) ---
GROQ_API_KEY = "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"

# --- CUSTOM CSS (TEMA BATIK KLASIK / SOGAN) ---
st.markdown("""
    <style>
    /* 1. Latar Belakang (Krem Kain Mori) */
    .stApp {
        background-color: #fdfcf0;
        color: #3e2723;
    }

    /* 2. Sidebar (Cokelat Tua Batik) */
    [data-testid="stSidebar"] {
        background-color: #4e342e;
        color: white;
    }
    [data-testid="stSidebar"] * {
        color: #ffecb3 !important; /* Teks Emas */
    }

    /* 3. Judul */
    h1 {
        color: #3e2723;
        font-family: 'Georgia', serif;
        text-align: center;
        border-bottom: 2px solid #8d6e63;
        padding-bottom: 10px;
    }

    /* 4. Chat Bubbles */
    /* User (Cokelat Muda) */
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: #d7ccc8; 
        color: #3e2723;
        border-radius: 15px;
    }
    
    /* Asisten (Putih Gading) */
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background-color: #fff8e1;
        border: 1px solid #d7ccc8;
        border-radius: 15px;
    }

    /* 5. Menghilangkan Glitch Icon jika ada */
    .material-icons {
        display: none;
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

# --- SIDEBAR ---
with st.sidebar:
    st.title("🏛️ Museum Batik")
    st.markdown("---")
    
    if museum_data:
        st.write(f"📍 **Lokasi:**\n{museum_data['informasi_umum']['lokasi']['alamat']}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.expander("🎫 Daftar Harga Tiket", expanded=True):
            st.write(f"Dewasa: Rp{museum_data['harga_tiket']['dewasa']:,}")
            st.write(f"Pelajar: Rp{museum_data['harga_tiket']['pelajar_mahasiswa']:,}")
            st.write(f"Asing: Rp{museum_data['harga_tiket']['wisatawan_mancanegara']:,}")
            
    st.markdown("---")
    st.caption("Asisten Virtual Resmi")

# --- MAIN CONTENT ---
st.title("Asisten Museum Batik Indonesia")
st.markdown("<p style='text-align: center;'><em>Melestarikan Warisan Budaya Nusantara</em></p>", unsafe_allow_html=True)

if not museum_data:
    st.error("⚠️ File 'dataset_museum_batik.json' belum diunggah.")
    st.stop()

# --- CHAT LOGIC ---
client = Groq(api_key=GROQ_API_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Sugeng Rawuh. Saya siap membantu Anda dengan informasi seputar Museum Batik."}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Tanyakan sesuatu..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prompt System
    system_prompt = f"""
    Anda adalah asisten Museum Batik Indonesia.
    Jawablah pertanyaan pengunjung berdasarkan data ini: {json.dumps(museum_data)}
    Gunakan bahasa Indonesia yang sopan dan ramah.
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
        st.error(f"Terjadi kesalahan: {e}")
