import streamlit as st
from etl.pipeline import pipeline


st.set_page_config(layout="wide")

st.title("Unusual Spotify Stats")

uploaded_file = st.file_uploader("Load ZIP file from Spotify", type="zip")

if uploaded_file is not None:

    # sprawdzenie czy w sesji jest już plik
    already_processed = st.session_state.get(
        "uploaded_filename") == uploaded_file.name

    if not already_processed:
        with st.spinner("Loading..."):
            upload_id = pipeline(uploaded_file)

        # dodanie do sesji upload_id i filename
        st.session_state["upload_id"] = upload_id
        st.session_state["uploaded_filename"] = uploaded_file.name

        st.success("Data loaded!")

    else:
        st.write("Already loaded a file")


st.header("Import guide")

st.subheader("1. Request your data")
st.markdown("1. Open Privacy page on the Spotify website")
st.markdown('2. Find "Download your data" section')
st.markdown('3. Select only the box with "Extended streaming history"')
# zdjecie
st.markdown('4. Press "Request data" button')

st.subheader("2. Confirm your request")
st.markdown('Confirm your request via email')

st.subheader("3. Wait until Spotify sends you data")
st.markdown('Wait for the second email with the download link (usually a few days, officially up to 30)')

st.subheader("4. Download the files")
st.markdown('You will get an email with a link to download a .zip file')

st.subheader("4. Import your files")
st.markdown('Import your .zip file here:')