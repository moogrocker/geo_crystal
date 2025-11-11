"""Main Streamlit app for GEO Autopilot MVP."""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="GEO Autopilot MVP",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("🚀 GEO Autopilot MVP")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["Audit", "Transform", "Results"],
    index=0,
    label_visibility="collapsed"
)

# Route to appropriate page
# Streamlit automatically loads pages from pages/ directory
# We'll use importlib to load the numbered page files
if page == "Audit":
    import importlib.util
    import os
    spec = importlib.util.spec_from_file_location("audit", os.path.join(os.path.dirname(__file__), "pages", "1_audit.py"))
    audit_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit_module)
    audit_module.render()
elif page == "Transform":
    import importlib.util
    import os
    spec = importlib.util.spec_from_file_location("transform", os.path.join(os.path.dirname(__file__), "pages", "2_transform.py"))
    transform_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(transform_module)
    transform_module.render()
elif page == "Results":
    import importlib.util
    import os
    spec = importlib.util.spec_from_file_location("results", os.path.join(os.path.dirname(__file__), "pages", "3_results.py"))
    results_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(results_module)
    results_module.render()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.8rem;'>
        GEO Autopilot MVP v0.1.0
    </div>
    """,
    unsafe_allow_html=True
)

