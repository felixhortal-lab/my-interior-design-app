# ...existing code...
import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter
import io
import time

st.set_page_config(page_title="Rediseña tu Casa", layout="centered")

st.title("Rediseña tu casa con un solo click")
st.caption("Demo local — Streamlit")

# session state
if "src_bytes" not in st.session_state:
    st.session_state.src_bytes = None
if "generated_bytes" not in st.session_state:
    st.session_state.generated_bytes = None
if "last_style" not in st.session_state:
    st.session_state.last_style = None

uploaded = st.file_uploader("Sube la foto de la habitación", type=["jpg", "jpeg", "png"])
if uploaded:
    st.session_state.src_bytes = uploaded.read()

if st.session_state.src_bytes:
    src_img = Image.open(io.BytesIO(st.session_state.src_bytes)).convert("RGB")
    st.image(src_img, caption="Imagen subida", use_column_width=True)

style = st.selectbox("Selecciona un estilo", ["Modern", "Classic", "Nordic", "Japanese"])

def fake_generate(image: Image.Image, style_name: str) -> bytes:
    img = image.convert("RGBA").copy()
    overlays = {
        "Modern": (30, 144, 255, 40),
        "Classic": (160, 82, 45, 40),
        "Nordic": (240, 248, 255, 40),
        "Japanese": (255, 182, 193, 40),
    }
    overlay = Image.new("RGBA", img.size, overlays.get(style_name, (0, 0, 0, 0)))
    img = Image.alpha_composite(img, overlay)
    img = img.convert("RGB").filter(ImageFilter.SMOOTH_MORE)
    img = ImageEnhance.Contrast(img).enhance(1.05)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Generar diseño"):
        if not st.session_state.src_bytes:
            st.error("Sube una imagen antes de generar.")
        else:
            with st.spinner("Generando..."):
                time.sleep(0.5)
                img = Image.open(io.BytesIO(st.session_state.src_bytes)).convert("RGB")
                st.session_state.generated_bytes = fake_generate(img, style)
                st.session_state.last_style = style
            st.success("Generación completada")

with col2:
    if st.button("Reset"):
        st.session_state.src_bytes = None
        st.session_state.generated_bytes = None
        st.session_state.last_style = None
        st.experimental_rerun()

if st.session_state.generated_bytes:
    st.subheader(f"Resultado — estilo: {st.session_state.last_style}")
    gen_img = Image.open(io.BytesIO(st.session_state.generated_bytes))
    st.image(gen_img, use_column_width=True)
    st.download_button("Descargar imagen generada", data=st.session_state.generated_bytes, file_name="generated.jpg", mime="image/jpeg")
# ...existing code...