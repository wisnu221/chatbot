import streamlit as st
from groq import Groq
import json
import os

# --- KONFIGURASI HALAMAN STREAMLIT ---
st.set_page_config(
    page_title="Asisten Virtual Museum Batik",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- KONFIGURASI API ---
# GANTI DENGAN API KEY ANDA YANG SEBENARNYA DI SINI
GROQ_API_KEY = "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"

# --- FUNGSI LOAD DATASET ---
@st.cache_data(ttl=3600) # Cache data selama 1 jam agar performa lebih cepat
def load_museum_data():
    file_path = 'dataset_museum_batik.json'
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca file JSON: {e}")
        return None

# Memuat data
museum_data = load_museum_data()

# --- SIDEBAR: INFORMASI PENTING ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1909/1909704.png", width=100)
    st.title("🏛️ Info Museum")
    st.markdown("---")

    if museum_data and 'informasi_umum' in museum_data:
        info = museum_data['informasi_umum']
        
        # Lokasi
        st.subheader("📍 Lokasi")
        st.write(info['lokasi']['alamat'])
        st.caption(f"Koordinat: {info['lokasi']['koordinat']}")
        
        st.divider()
        
        # Jam Buka (Menggunakan Expander agar rapi)
        with st.expander("⏰ Jam Operasional"):
            st.write(f"**Hari Biasa:** {info['jam_operasional']['hari_biasa']}")
            st.write(f"**Akhir Pekan:** {info['jam_operasional']['akhir_pekan']}")
            st.write(f"**Tutup:** {info['jam_operasional']['hari_libur']}")

        # Harga Tiket (Menggunakan Expander)
        if 'harga_tiket' in museum_data:
            tiket = museum_data['harga_tiket']
            with st.expander("🎫 Harga Tiket Masuk"):
                st.write(f"**Dewasa:** Rp{tiket.get('dewasa', 0):,}")
                st.write(f"**Pelajar:** Rp{tiket.get('pelajar_mahasiswa', 0):,}")
                st.write(f"**Mancanegara:** Rp{tiket.get('wisatawan_mancanegara', 0):,}")
    else:
        st.warning("Data informasi umum tidak tersedia di sidebar.")
        
    st.markdown("---")
    st.caption("© 2024 Asisten Virtual Museum Batik Indonesia")

# --- HALAMAN UTAMA: INTERFACE CHAT ---
st.title("🎨 Asisten Virtual Museum Batik Indonesia")
st.markdown(
    """
    Selamat datang! Saya adalah asisten virtual yang siap membantu Anda. 
    Tanyakan apa saja tentang koleksi batik, filosofi motif, jadwal workshop, atau fasilitas museum.
    """
)
st.divider()

# Cek apakah data berhasil dimuat sebelum lanjut
if museum_data is None:
    st.error("⚠️ Kritis: File 'dataset_museum_batik.json' tidak ditemukan di direktori aplikasi.")
    st.info("Pastikan file JSON sudah diunggah ke folder yang sama dengan file app.py ini.")
    st.stop()

# Inisialisasi Klien Groq
try:
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    st.error(f"Gagal menginisialisasi Groq Client. Pastikan API Key benar. Error: {e}")
    st.stop()

# Inisialisasi Riwayat Chat di Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Halo! Ada yang bisa saya bantu terkait Museum Batik hari ini?"}
    ]

# Menampilkan Riwayat Chat yang Ada
for message in st.session_state.messages:
    # Menggunakan ikon berbeda untuk user dan asisten
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- LOGIKA INPUT PENGGUNA & RESPON AI ---
if prompt := st.chat_input("Ketik pertanyaan Anda di sini... (Contoh: Apa makna motif Parang?)"):
    # 1. Tampilkan dan simpan pesan pengguna
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # 2. Siapkan Context untuk AI (System Prompt)
    # Kita mengubah data JSON menjadi string agar bisa dibaca oleh model
    context_data = json.dumps(museum_data, ensure_ascii=False)
    
    system_prompt = f"""
    Peran: Anda adalah Asisten Virtual resmi dan berpengetahuan luas untuk Museum Batik Indonesia.
    Tugas: Jawablah pertanyaan pengguna berdasarkan HANYA pada data konteks yang diberikan di bawah ini.
    
    Pedoman:
    1. Gunakan Bahasa Indonesia yang sopan, ramah, dan edukatif.
    2. Jika informasi tersedia di data konteks, berikan jawaban yang detail dan akurat.
    3. Jika jawaban TIDAK tersedia di data konteks, katakan dengan jujur: "Maaf, saya tidak memiliki informasi tersebut dalam data museum kami saat ini." Jangan mengarang informasi.
    4. Jika ditanya soal harga, formatlah angka menjadi format Rupiah (contoh: Rp10.000).
    
    Data Konteks Museum (JSON):
    {context_data}
    """

    # 3. Generate Respon dari Groq AI
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Membuat stream response agar terlihat seperti sedang mengetik
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile", # Model yang stabil dan kapabel
                messages=[
                    {"role": "system", "content": system_prompt},
                    # Sertakan beberapa pesan terakhir untuk konteks percakapan (opsional)
                    *st.session_state.messages[-5:], 
                ],
                temperature=0.5, # Keseimbangan antara kreatif dan faktual
                max_tokens=1024,
                stream=True, # Mengaktifkan streaming
            )
            
            # Memproses stream
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            # Tampilkan respon final tanpa kursor
            message_placeholder.markdown(full_response)
            
            # 4. Simpan respon asisten ke riwayat
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            message_placeholder.error(f"Terjadi kesalahan koneksi ke layanan AI: {e}")
