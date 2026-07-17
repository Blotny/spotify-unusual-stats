import streamlit as st
from etl.pipeline import pipeline


st.set_page_config(
    page_title="Unusual Spotify Stats",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Unusual Spotify Stats")
st.markdown(
    "Discover what Spotify Wrapped doesn't show you — upload your data export and explore.")

st.divider()

if "upload_id" not in st.session_state:
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

            # po załadowaniu danych
            st.rerun()

        else:
            st.write("Already loaded a file")
    # jesli dane nie zaladowane
    else:
        st.page_link("pages/0_import_guide.py",
                     label="Don't have your data yet? Check the **Import Guide**")

# jesli dane juz załadowane
else:
    st.success(f"Data loaded: **{st.session_state['uploaded_filename']}**")

    col1, col2, col3 = st.columns([3, 1, 3])
    with col2:
        if st.button("Upload different file"):
            del st.session_state["upload_id"]
            del st.session_state["uploaded_filename"]
            st.rerun()


st.divider()

st.subheader("What you can explore")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Most Skipped")
    st.markdown("""
    Find out which tracks and artists you skip the most. 
    Maybe it will help you with blocking some content.
    """)
    st.page_link("pages/1_most_skipped.py", label="Go to Most Skipped →")
    st.image("assets/skip_page.png")
    
with col2:
    st.markdown("### Country Map")
    st.markdown("""
    See which countries your listening came from. 
    Click a country to explore your top artists and songs from that location.
    """)
    st.page_link("pages/2_country_map.py", label="Go to Country Map →")
    st.image("assets/country_map_page.png")
    
with col3:
    st.markdown("### Early Wrapped")
    st.markdown("""
    See your Spotify Wrapped before it's released — or revisit 
    any previous year with full data including December.
    """)
    st.page_link("pages/3_early_wrapped.py", label="Go to Early Wrapped →")
    st.image("assets/wrapped_page.png")
    