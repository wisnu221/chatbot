import streamlit as st
from groq import Groq
import json
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Virtual Assistant Museum Batik", 
    page_icon="🎨", 
    layout="wide"
)

# --- KEAMANAN API KEY ---
# Di Streamlit Cloud, masukkan API Key di 'Advanced Settings' -> 'Secrets'
# Jangan lupa ganti 'GROQ_API_KEY' sesuai nama di Secrets Anda
if "GROQ_API_KEY" in st.secrets:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
else:
    # Fallback jika dijalankan lokal tanpa Secrets
    GROQ_API_KEY = "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"

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main { background-color: #fcf8f2; }
    .stChatMessage { border-radius: 15px; }
    .stTitle { color: #5d4037; font-family: 'Georgia', serif; }
    </style>
    """, unsafe_allow_html=True)

# --- LOAD DATASET ---
@st.cache_data # Menggunakan cache agar aplikasi lebih cepat saat diakses banyak orang
def load_data():
    if os.path.exists('dataset_museum_batik.json'):
        with open('dataset_museum_batik.json', 'r') as f:
            return json.load(f)
    return None

museum_data = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.title("🏛️ Info Museum")
    if museum_data:
        st.info(f"📍 **Lokasi:**\n{museum_data['informasi_umum']['lokasi']['alamat']}")
        
        with st.expander("🎫 Harga Tiket"):
            st.write(f"Dewasa: Rp{museum_data['harga_tiket']['dewasa']:,}")
            st.write(f"Mancanegara: Rp{museum_data['harga_tiket']['wisatawan_mancanegara']:,}")
    st.divider()
    st.caption("Dikelola oleh Museum Batik Indonesia")

# --- LOGIKA CHAT ---
st.title("Asisten Virtual Museum Batik")
client = Groq(api_key=GROQ_API_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Halo! Ada yang bisa saya bantu terkait Museum Batik?"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Tanyakan tentang batik..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    system_prompt = f"Anda asisten museum. Jawab berdasarkan data: {json.dumps(museum_data)}"
    
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
        st.error(f"Error: {e}")
