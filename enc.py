import streamlit as st
from PIL import Image, ImageEnhance
import numpy as np
import base64
from io import BytesIO
from pdf2image import convert_from_path
import tempfile
import os

# Helper functions for downloading, resizing, and PDF handling (unchanged)
# ... (your existing get_image_download_link, resize_image, handlePdf functions)

def encryptPage():
    st.title("Image Steganography")

    # Cover Image Upload
    st.subheader("Upload Cover Image (PNG, JPG, BMP)")
    cover_file = st.file_uploader("", type=["png", "jpg", "bmp"], key="cover")

    if cover_file:
        try:
            cover = Image.open(cover_file).convert('RGB')

            # Message File Upload
            st.subheader("Upload Message File (PNG, JPG, BMP, PDF)")
            message_file = st.file_uploader("", type=["png", "jpg", "bmp", "pdf"], key="message")

            if message_file:
                try:
                    # Handle different file types with clearer logic
                    if message_file.type == "application/pdf":
                        message = handlePdf(message_file).convert('RGB')
                    else:
                        message = Image.open(message_file).convert('RGB')

                    # Resize to ensure consistent dimensions (with error handling)
                    try:
                        cover, message = resize_image(cover, message), resize_image(message, cover)
                    except Exception as e:
                        st.error(f"Error resizing images: {e}")
                        return  # Exit to avoid further errors

                    # Steganography process (with comments for clarity)
                    embed_bits = 4  # Number of bits to embed
                    message_shift = np.right_shift(np.array(message), 8 - embed_bits)
                    show_message = message_shift << (8 - embed_bits)

                    st.image(show_message, caption="Message with embedded bits")  # Show message for verification

                    cover_zeroed = np.array(cover) & ~(0b11111111 >> embed_bits)
                    stego = cover_zeroed | message_shift
                    stego = np.clip(stego, 0, 255)
                    st.image(stego, caption="Stego image")  # Display in RGB

                    # Download link (unchanged)
                    stego_img = Image.fromarray(stego.astype(np.uint8))
                    st.markdown(get_image_download_link(stego_img, "stego.png", "Download Stego Image"), unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Error processing message image: {e}")

        except Exception as e:
            st.error(f"Error processing cover image: {e}")

# Run the app
if __name__ == "__main__":
    encryptPage()
