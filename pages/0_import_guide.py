import streamlit as st

st.set_page_config(
    page_title="Import guide",
    page_icon="🎵",
    layout="wide",
)

st.title("How to import your Spotify data")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("1. Request your data")
    st.markdown("""
    1. Go to [Spotify Privacy Settings](https://www.spotify.com/account/privacy/)
    2. Scroll down to **"Download your data"** section
    3. Check **only** "Extended streaming history" — skip "Account data" and "Technical log information"
    4. Click **"Request data"**
    """)

with col2:
    st.image("assets/data_checkboxes.png")

st.divider()

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("2. Confirm your request")
    st.markdown("Spotify will send you an email — click the confirmation link inside. Without this step, your request won't start.")

with col2:
    st.image("assets/data_request.png")

st.divider()

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("3. Wait for your data")
    st.markdown("You'll receive a second email with a download link. Usually arrives within **1–5 days**, officially up to 30.")

with col2:
    st.image("assets/data_email.jpg")

st.divider()

st.subheader("4. Upload here")
st.page_link("main.py", label="← Go back to main page to upload your file")