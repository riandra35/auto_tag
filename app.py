import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ExifTags, ImageOps
from datetime import datetime
import io

def ambil_waktu_exif(img):
    try:
        exif = img.getexif()
        if exif:
            for tag_id, value in exif.items():
                tag = ExifTags.TAGS.get(tag_id, tag_id)
                if tag == 'DateTime' or tag == 'DateTimeOriginal':
                    # Mengubah format YYYY:MM:DD HH:MM:SS menjadi Aug 31, 2026 7:36:16 AM
                    dt = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                    return dt.strftime("%b %d, %Y %I:%M:%S %p")
    except Exception:
        pass
    # Jika tidak ada metadata, gunakan waktu saat ini
    return datetime.now().strftime("%b %d, %Y %I:%M:%S %p")

def beri_watermark(img, teks_waktu, teks_lokasi):
    # Mengembalikan orientasi foto ke posisi aslinya
    img = ImageOps.exif_transpose(img)
    
    draw = ImageDraw.Draw(img)
    
    # Memuat font. Letakkan file arial.ttf di folder yang sama agar font mirip dengan gambar.
    try:
        font = ImageFont.truetype("arial.ttf", int(img.height / 35))
    except IOError:
        font = ImageFont.load_default()
        
    # Menggabungkan waktu dan lokasi dengan baris baru
    teks_lengkap = f"{teks_waktu}\n{teks_lokasi}"
    
    # Menghitung ukuran area teks dengan rata kiri
    bbox = draw.textbbox((0, 0), teks_lengkap, font=font, align="left")
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Menentukan posisi teks (Kiri Bawah)
    margin_x = int(img.width * 0.03)
    margin_y = int(img.height * 0.03)
    
    x = margin_x  # Posisi kiri
    y = img.height - margin_y - text_height  # Posisi bawah
    
    # Menggambar teks dengan garis tepi hitam (stroke) dan isi putih
    draw.multiline_text(
        (x, y), 
        teks_lengkap, 
        font=font, 
        fill="white", 
        align="left", 
        stroke_width=2,     # Ketebalan outline hitam
        stroke_fill="black" # Warna outline
    )
    
    return img

# ================= TAMPILAN ANTARMUKA STREAMLIT ================= #

st.set_page_config(page_title="Auto Tag Foto", layout="centered")
st.title("📸 Aplikasi Auto Tag Foto")
st.write("Unggah foto lapangan, masukkan detail lokasi, lalu unduh hasilnya (tanpa disimpan di server).")

uploaded_file = st.file_uploader("1. Pilih Foto", type=["jpg", "jpeg", "png"])

# Menggunakan text_area agar pengguna bisa menempelkan teks multi-baris
detail_lokasi = st.text_area(
    "2. Detail Lokasi (Copy-Paste dari Google Maps/Titik Koordinat)", 
    placeholder="0.92584614S 100.36096574E\nNo. 1 Jalan Khatib Sulaiman\nFlamboyan Baru\nKecamatan Padang Barat\nKota Padang\nSumatera Barat",
    height=150
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    # Mengekstrak dan memformat waktu dari metadata foto
    waktu_foto = ambil_waktu_exif(image)
    
    # Membiarkan pengguna mengedit waktu jika diperlukan
    waktu_input = st.text_input("Konfirmasi Waktu (Bisa diedit)", value=waktu_foto)
    
    if st.button("Proses Foto", type="primary"):
        with st.spinner("Memproses foto..."):
            # Proses watermark
            img_hasil = beri_watermark(image.copy(), waktu_input, detail_lokasi)
            
            st.success("✅ Foto berhasil diproses!")
            st.image(img_hasil, caption="Pratinjau Hasil Foto", use_container_width=True)
            
            # Konversi gambar ke format yang bisa diunduh
            buf = io.BytesIO()
            img_hasil.save(buf, format="JPEG", quality=95)
            byte_im = buf.getvalue()
            
            st.download_button(
                label="📥 Unduh Foto",
                data=byte_im,
                file_name=f"tagged_{uploaded_file.name}",
                mime="image/jpeg"
            )
