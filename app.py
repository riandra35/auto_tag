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
                    dt = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                    return dt.strftime("%b %d, %Y %I:%M:%S %p")
    except Exception:
        pass
    return datetime.now().strftime("%b %d, %Y %I:%M:%S %p")

def dapatkan_font(ukuran_ideal):
    # Daftar font alternatif untuk Windows, Mac, dan Linux/Streamlit Cloud
    daftar_font = [
        "arial.ttf", 
        "DejaVuSans.ttf", 
        "LiberationSans-Regular.ttf", 
        "FreeSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "C:\\Windows\\Fonts\\arial.ttf"
    ]
    
    for nama_font in daftar_font:
        try:
            return ImageFont.truetype(nama_font, ukuran_ideal)
        except IOError:
            continue
            
    # Jika semua gagal, akan pakai default (kemungkinan kecil di Linux/Windows standar)
    return ImageFont.load_default()

def beri_watermark(img, teks_waktu, teks_lokasi):
    img = ImageOps.exif_transpose(img)
    draw = ImageDraw.Draw(img)
    
    # Memperbesar rasio font agar lebih proporsional (dibagi 25 bukan 35)
    ukuran_font_ideal = max(int(img.height / 25), 16) 
    font = dapatkan_font(ukuran_font_ideal)
        
    teks_lengkap = f"{teks_waktu}\n{teks_lokasi}"
    
    bbox = draw.textbbox((0, 0), teks_lengkap, font=font, align="left")
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    margin_x = int(img.width * 0.03)
    margin_y = int(img.height * 0.03)
    
    x = margin_x
    y = img.height - margin_y - text_height
    
    draw.multiline_text(
        (x, y), 
        teks_lengkap, 
        font=font, 
        fill="white", 
        align="left", 
        stroke_width=2,
        stroke_fill="black"
    )
    
    return img

# ================= TAMPILAN ANTARMUKA STREAMLIT ================= #

st.set_page_config(page_title="Auto Tag Foto", layout="centered")
st.title("📸 Aplikasi Auto Tag Foto")
st.write("Unggah foto lapangan, masukkan detail lokasi, lalu unduh hasilnya (tanpa disimpan di server).")

uploaded_file = st.file_uploader("1. Pilih Foto", type=["jpg", "jpeg", "png"])

detail_lokasi = st.text_area(
    "2. Detail Lokasi (Copy-Paste dari Google Maps/Titik Koordinat)", 
    placeholder="0.92584614S 100.36096574E\nNo. 1 Jalan Khatib Sulaiman\nFlamboyan Baru\nKecamatan Padang Barat\nKota Padang\nSumatera Barat",
    height=150
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    waktu_foto = ambil_waktu_exif(image)
    waktu_input = st.text_input("Konfirmasi Waktu (Bisa diedit)", value=waktu_foto)
    
    if st.button("Proses Foto", type="primary"):
        with st.spinner("Memproses foto..."):
            img_hasil = beri_watermark(image.copy(), waktu_input, detail_lokasi)
            
            st.success("✅ Foto berhasil diproses!")
            st.image(img_hasil, caption="Pratinjau Hasil Foto", use_container_width=True)
            
            buf = io.BytesIO()
            img_hasil.save(buf, format="JPEG", quality=95)
            byte_im = buf.getvalue()
            
            st.download_button(
                label="📥 Unduh Foto",
                data=byte_im,
                file_name=f"tagged_{uploaded_file.name}",
                mime="image/jpeg"
            )
