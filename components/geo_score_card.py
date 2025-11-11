"""Reusable GEO score card component."""

import streamlit as st


def render_score_card(score: float, label: str = "GEO Score"):
    """
    Render a color-coded GEO score card.
    
    Args:
        score: GEO score (0-100)
        label: Label for the score metric
    """
    # Determine color based on score
    if score < 40:
        color = "#d62728"  # Red
        status = "Poor"
    elif score < 70:
        color = "#ff7f0e"  # Yellow/Orange
        status = "Fair"
    else:
        color = "#2ca02c"  # Green
        status = "Good"
    
    # Display metric with custom styling
    st.markdown(
        f"""
        <div style="background-color: {color}20; padding: 1.5rem; border-radius: 0.5rem; border-left: 4px solid {color};">
            <h2 style="margin: 0; color: {color}; font-size: 3rem;">{score:.1f}</h2>
            <p style="margin: 0.5rem 0 0 0; color: #666; font-size: 1rem;">{label} - {status}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

