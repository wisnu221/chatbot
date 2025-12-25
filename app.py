import streamlit as st
from groq import Groq
import json
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Asisten Museum Batik",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- API KEY (Ganti jika perlu) ---
GROQ_API_KEY = "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"

# --- FUNGSI LOAD DATA ---
@st.cache_data
def load_data():
    file_path = 'dataset_museum_batik.json'
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error membaca file JSON: {e}")
            return None
    return None

museum_data = load_data()

# --- SIDEBAR: INFORMASI UTAMA (Disesuaikan dengan Dataset Baru) ---
with st.sidebar:
    # Menggunakan Logo Default atau Gambar Batik
    st.image("https://cdn-icons-png.flaticon.com/512/1909/1909704.png", width=80)
    
    if museum_data:
        # Mengambil data dari struktur JSON baru yang bersarang
        info_identitas = museum_data.get('informasi_umum', {}).get('identitas', {})
        lokasi = info_identitas.get('lokasi', {})
        jam = museum_data.get('jam_operasional', {})
        tiket = museum_data.get('harga_tiket', {})
        
        # Judul Nama Museum
        nama_museum = info_identitas.get('nama', "Museum Batik")
        st.header(nama_museum)
        st.caption(f"Est. {info_identitas.get('tahun_pendirian', '-')}")
        
        st.divider()

        # 1. Lokasi
        st.subheader("📍 Lokasi")
        alamat_lengkap = f"{lokasi.get('alamat')}, {lokasi.get('kota')}"
        st.write(alamat_lengkap)
        
        # 2. Jam Buka
        with st.expander("⏰ Jam Operasional"):
            st.write(f"**Senin-Jumat:** {jam.get('hari_biasa', '-')}")
            st.write(f"**Akhir Pekan:** {jam.get('akhir_pekan', '-')}")
            st.caption(jam.get('hari_libur', ''))

        # 3. Tiket
        with st.expander("🎫 Harga Tiket"):
            if 'dewasa' in tiket:
                st.write(f"**Dewasa:** Rp{tiket['dewasa']:,}")
            if 'pelajar_mahasiswa' in tiket:
                st.write(f"**Pelajar:** Rp{tiket['pelajar_mahasiswa']:,}")
            if 'wisatawan_mancanegara' in tiket:
                st.write(f"**Asing:** Rp{tiket['wisatawan_mancanegara']:,}")
            st.caption(f"Info: {tiket.get('kebijakan_refund', '-')}")
            
        # 4. Kontak Media Sosial
        st.divider()
        sosmed = info_identitas.get('media_sosial', {})
        st.markdown(f"[Instagram]({sosmed.get('instagram', '#')}) | [Website]({info_identitas.get('kontak', {}).get('website', '#')})")

    else:
        st.warning("⚠️ Data JSON belum dimuat dengan benar.")
        st.stop()

# --- HALAMAN UTAMA ---
st.title("🎨 Asisten Virtual Museum Batik")
st.markdown(
    """
    <style>
    .stChatMessage {border-radius: 10px;}
    </style>
    Selamat datang! Tanyakan tentang **koleksi motif**, **sejarah**, **rute kunjungan**, atau **jadwal workshop**.
    """, 
    unsafe_allow_html=True
)
st.divider()

# Inisialisasi Klien Groq
try:
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    st.error(f"Error API Key: {e}")
    st.stop()

# Inisialisasi Riwayat Chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Halo! Saya siap memandu Anda. Apakah Anda ingin rekomendasi rute kunjungan atau info tentang motif batik tertentu?"}
    ]

# Tampilkan Riwayat
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- LOGIKA CHAT ---
if prompt := st.chat_input("Contoh: Buatkan rute kunjungan 1 jam..."):
    # Simpan & Tampilkan Input User
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Context Data (Konversi JSON ke String)
    data_str = json.dumps(museum_data, ensure_ascii=False)

    # System Prompt yang dioptimalkan untuk struktur baru
    system_prompt = f"""
    Anda adalah Pemandu Cerdas Museum Batik Indonesia.
    Gunakan data JSON berikut untuk menjawab pertanyaan pengunjung:
    {data_str}

    PANDUAN MENJAWAB:
    1. **Identitas & Lokasi**: Ambil dari bagian 'informasi_umum' -> 'identitas'.
    2. **Tiket & Jam**: Ambil dari 'harga_tiket' dan 'jam_operasional'.
    3. **Koleksi & Motif**: Jika ditanya motif (misal: Parang, Mega Mendung), cari detailnya di array 'koleksi_motif'. Jelaskan filosofi dan asalnya.
    4. **Rute Kunjungan**: Jika pengunjung bingung mau lihat apa, tawarkan opsi dari bagian 'rute_kunjungan' (misal: Rute Kilat 30 Menit atau Rute Edukasi).
    5. **Teknik**: Jelaskan detail dari bagian 'teknik_pembuatan'.
    
    Gaya bahasa: Ramah, edukatif, dan membantu. Gunakan format Rupiah (Rp) untuk harga.
    Jika data tidak ada di JSON, katakan "Maaf informasi tersebut belum tersedia di database museum kami."
    """
    
    # Generate Jawaban
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *st.session_state.messages[-5:] # Membawa konteks 5 chat terakhir
                ],
                temperature=0.5,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Terjadi kesalahan koneksi: {e}")
