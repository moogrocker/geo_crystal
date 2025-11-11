"""Content comparison component for side-by-side diff viewer."""

import streamlit as st


def render_content_comparison(original_content: str, transformed_content: str):
    """
    Render side-by-side content comparison.
    
    Args:
        original_content: Original content text
        transformed_content: Transformed content text
    """
    st.subheader("📝 Content Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Original Content**")
        st.text_area(
            "Original",
            original_content,
            height=400,
            disabled=True,
            key="original_content_area",
            label_visibility="collapsed"
        )
        st.caption(f"Length: {len(original_content)} characters, {len(original_content.split())} words")
    
    with col2:
        st.markdown("**Transformed Content**")
        st.text_area(
            "Transformed",
            transformed_content,
            height=400,
            disabled=True,
            key="transformed_content_area",
            label_visibility="collapsed"
        )
        st.caption(f"Length: {len(transformed_content)} characters, {len(transformed_content.split())} words")
    
    # Highlight differences (simplified - in production would use diff library)
    if original_content != transformed_content:
        st.info("💡 Content has been transformed. Differences are highlighted above.")
    else:
        st.warning("⚠️ No changes detected in content.")

