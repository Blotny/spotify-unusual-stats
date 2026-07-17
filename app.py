# test_nav.py
import streamlit as st

pg = st.navigation(
    [
        st.Page("main.py", title="Home"),
        st.Page("pages/1_most_skipped.py", title="Most Skipped"),
        st.Page("pages/2_country_map.py", title="Country Map"),
        st.Page("pages/3_early_wrapped.py", title="Early Wrapped"),
        st.Page("pages/0_import_guide.py", title="Import Guide"),
    ],
    position="top"
)
pg.run()