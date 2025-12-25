import streamlit as st
from groq import Groq
import json
import os

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Asisten Museum Batik",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. API KEY ---
GROQ_API_KEY = "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"

# --- 3. CUSTOM CSS (TEMA PREMIUM BATIK) ---
st.markdown("""
    <style>
    /* Import Font Google: Playfair Display untuk kesan Elegan */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Lato:wght@400;700&display=swap');

    /* Latar Belakang Utama (Krem Kertas) */
    .stApp {
        background-color: #fdfbf7;
        color: #4a4a4a;
        font-family: 'Lato', sans-serif;
    }

    /* Sidebar (Cokelat Tua Mewah) */
    [data-testid="stSidebar"] {
        background-color: #3e2723;
        border-right: 2px solid #8d6e63;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #ffecb3 !important; /* Emas */
        font-family: 'Playfair Display', serif;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] li, [data-testid="stSidebar"] div {
        color: #d7ccc8; /* Abu-cokelat muda */
    }

    /* Judul Utama */
    h1 {
        font-family: 'Playfair Display', serif;
        color: #3e2723;
        font-size: 3rem;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    /* Sub-judul */
    .subtitle {
        text-align: center;
        color: #8d6e63;
        font-style: italic;
        margin-bottom: 2rem;
    }

    /* Chat Bubbles */
    /* User: Cokelat Muda */
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: #efebe9;
        border-left: 5px solid #5d4037;
        border-radius: 10px;
    }
    /* Assistant: Putih Bersih */
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    /* Tombol Saran (Quick Reply) */
    .stButton > button {
        background-color: #ffffff;
        color: #5d4037;
        border: 1px solid #5d4037;
        border-radius: 20px;
        padding: 5px 15px;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #5d4037;
        color: #ffffff;
        border-color: #5d4037;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. FUNGSI LOAD DATA ---
@st.cache_data
def load_data():
    file_path = 'dataset_museum_batik.json'
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error JSON: {e}")
            return None
    return None

museum_data = load_data()

# --- 5. SIDEBAR YANG LEBIH INFORMATIF ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Wayang_Gunungan.svg/1200px-Wayang_Gunungan.svg.png", width=100) # Ikon Gunungan
    st.title("Info Praktis")
    
    if museum_data:
        identitas = museum_data.get('informasi_umum', {}).get('identitas', {})
        jam = museum_data.get('jam_operasional', {})
        tiket = museum_data.get('harga_tiket', {})

        st.markdown("---")
        
        # Status Buka/Tutup (Simulasi sederhana)
        st.success("🟢 Museum Buka Hari Ini")
        
        with st.expander("📍 Lokasi & Kontak", expanded=False):
            st.write(f"**Alamat:** {identitas.get('lokasi', {}).get('alamat')}")
            st.write(f"**Telp:** {identitas.get('kontak', {}).get('telepon')}")

        with st.expander("🎫 Tiket Masuk", expanded=True):
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Dewasa", f"Rp{tiket.get('dewasa', 0)//1000}rb")
            with col_b:
                st.metric("Pelajar", f"Rp{tiket.get('pelajar_mahasiswa', 0)//1000}rb")
            st.caption("*Harga dalam ribuan Rupiah")

        st.info("💡 **Tips:** Coba tanyakan tentang 'Rute 30 menit' jika Anda terburu-buru.")
    
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: #a1887f;'>© Museum Batik AI</div>", unsafe_allow_html=True)

# --- 6. HEADER HALAMAN UTAMA ---
col_head1, col_head2 = st.columns([1, 6])
with col_head1:
    st.write("") # Spacer
with col_head2:
    st.markdown("<h1>Asisten Museum Batik</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Melestarikan Warisan Budaya Nusantara Melalui Teknologi</p>", unsafe_allow_html=True)

if not museum_data:
    st.error("⚠️ Data museum tidak ditemukan. Pastikan file JSON sudah diunggah.")
    st.stop()

# --- 7. LOGIKA CHATBOT & SESSION STATE ---
client = Groq(api_key=GROQ_API_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Fitur Quick Reply (Muncul jika chat masih kosong)
if len(st.session_state.messages) == 0:
    st.markdown("### 👋 Bingung mau tanya apa? Coba ini:")
    col1, col2, col3 = st.columns(3)
    
    # Tombol Saran
    if col1.button("🎫 Harga Tiket?"):
        st.session_state.messages.append({"role": "user", "content": "Berapa harga tiket masuk?"})
    if col2.button("🌸 Filosofi Mega Mendung?"):
        st.session_state.messages.append({"role": "user", "content": "Apa makna motif Mega Mendung?"})
    if col3.button("⏱️ Rute Cepat 30 Menit"):
        st.session_state.messages.append({"role": "user", "content": "Berikan rekomendasi rute kunjungan 30 menit."})

# Render Riwayat Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 8. PROSES INPUT & JAWABAN ---
if prompt := st.chat_input("Tanyakan sesuatu tentang koleksi atau layanan museum..."):
    # Tampilkan pesan user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Persiapan Prompt System
    data_str = json.dumps(museum_data, ensure_ascii=False)
    
    system_prompt = f"""
    Anda adalah Kurator Digital Museum Batik Indonesia yang cerdas dan berbudaya.
    Tugas: Menjawab pertanyaan pengunjung berdasarkan data JSON ini: {data_str}

    Aturan Menjawab:
    1. Jika ditanya **Rute**, ambil dari 'rute_kunjungan'.
    2. Jika ditanya **Motif**, jelaskan filosofi dan asalnya dari 'koleksi_motif'.
    3. Jika ditanya **Fasilitas**, sebutkan dari list 'fasilitas'.
    4. Gunakan bahasa Indonesia yang sopan, mengalir, dan sedikit formal (seperti pemandu museum).
    5. Formatlah harga dengan "Rp" (contoh: Rp10.000).
    """
    
    # Generate Jawaban
    try:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *st.session_state.messages[-5:] # Context window
                ],
                temperature=0.5,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
