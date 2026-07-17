import streamlit as st

def require_data():
    if "upload_id" not in st.session_state:
        st.markdown(
            """
            <div style="text-align: center; padding: 60px 0;">
                <p style="font-size: 32px;">📂</p>
                <p style="font-size: 24px; font-weight: bold;">No data loaded</p>
                <p style="color: #888888;">Upload your Spotify export to see your stats.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            st.page_link("main.py", label="Go to Home →", use_container_width=True)
            st.page_link("pages/0_import_guide.py", label="Import Guide →", use_container_width=True)
        st.stop()