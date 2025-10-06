import streamlit as st
import tempfile
from PIL import Image
import io
import time

st.title("Redesign your house with one click")

# Upload photo
uploaded_file = st.file_uploader("Upload your room photo", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # show preview
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded room", use_column_width=True)
    st.write(f"Filename: {uploaded_file.name}")

# Style selection
style = st.selectbox("Choose style", ["Modern", "Classic", "Nordic", "Japanese"])

# Ensure session state keys
if "generated" not in st.session_state:
    st.session_state.generated = None
if "last_upload" not in st.session_state:
    st.session_state.last_upload = None

# Redesign form (single submit)
with st.form(key="redesign_form"):
    st.write("Press to generate a redesigned concept for the selected style.")
    generate = st.form_submit_button("Redesign Room")
    if generate:
        if not uploaded_file:
            st.error("Please upload a room photo first.")
        else:
            st.session_state.last_upload = uploaded_file.name
            with st.spinner("Generating redesigned concept..."):
                # Placeholder for actual generation logic
                time.sleep(1)  # simulate work
                st.session_state.generated = f"Generated design (style={style}) for {uploaded_file.name}"

# Show generated result (placeholder text or image)
if st.session_state.generated:
    st.success("Design ready")
    st.write(st.session_state.generated)
    # If you later produce an image, use st.image(...) here

# Feedback form (separate submit)
with st.form(key="feedback_form"):
    feedback = st.text_input("Give feedback to change (e.g., add plants)")
    update = st.form_submit_button("Update Design")
    if update:
        if not st.session_state.generated:
            st.error("Generate a design first before updating.")
        else:
            with st.spinner("Applying update..."):
                # Placeholder: apply feedback to existing design
                time.sleep(0.5)
                st.session_state.generated = f"{st.session_state.generated} — Updated: {feedback or 'no feedback provided'}"
                st.success("Update applied")
