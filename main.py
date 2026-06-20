import streamlit as st
from etl.pipeline import pipeline


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
        st.write("Waiting for a file...")
