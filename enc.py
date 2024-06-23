import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import base64
from io import BytesIO

# Fungsi untuk mengenkripsi PDF
def encrypt_pdf(cover_file, message_bytes, password, imbed=4):
    cover_reader = PdfReader(cover_file)
    message_bits = "".join(format(byte, "08b") for byte in message_bytes)

    writer = PdfWriter()
    for page_num, page in enumerate(cover_reader.pages):
        content_bytes = page.get_contents().get_data()
        
        # Sisipkan pesan ke dalam byte konten
        stego_content = bytearray()
        message_index = 0
        for byte in content_bytes:
            if message_index < len(message_bits):
                # Sisipkan bit pesan ke bit terendah
                stego_byte = (byte & ~((1 << imbed) - 1)) | int(message_bits[message_index:message_index + imbed], 2)
                message_index += imbed
            else:
                stego_byte = byte
            stego_content.append(stego_byte)

        # Ganti konten halaman dengan konten yang sudah disisipi pesan
        page._set_contents(stego_content)
        writer.add_page(page)

    # Enkripsi PDF
    writer.encrypt(password)

    return writer.get_object()

# Fungsi untuk mendownload PDF
def get_pdf_download_link(pdf_object, filename, text):
    buffered = BytesIO()
    buffered.write(pdf_object)
    pdf_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:application/pdf;base64,{pdf_str}" download="{filename}">{text}</a>'
    return href

# Antarmuka Streamlit
st.title("Enkripsi PDF Steganografi")

cover_file = st.file_uploader("Unggah PDF Cover", type=["pdf"])
message_file = st.file_uploader("Unggah Pesan (File apa saja)", type=["pdf", "png", "jpg", "txt", "docx", "zip", "mp3"])
password = st.text_input("Masukkan kata sandi enkripsi:", type="password")

if cover_file and message_file and password:
    message_bytes = message_file.read()
    pdf_object = encrypt_pdf(cover_file, message_bytes, password)
    st.markdown(get_pdf_download_link(pdf_object, "stego.pdf", "Unduh PDF Stego"), unsafe_allow_html=True)
