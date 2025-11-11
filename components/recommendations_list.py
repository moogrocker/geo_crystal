"""Recommendations list component."""

import streamlit as st


def render_recommendations(recommendations: list):
    """
    Render a formatted list of recommendations.
    
    Args:
        recommendations: List of recommendation strings
    """
    if not recommendations:
        st.info("✨ Great! No recommendations at this time. Your content is well optimized!")
        return
    
    # Prioritize recommendations (in production, would use scoring)
    prioritized = prioritize_recommendations(recommendations)
    
    st.markdown("### High Priority")
    for i, rec in enumerate(prioritized.get("high", []), 1):
        st.markdown(f"🔴 **{i}. {rec}**")
    
    if prioritized.get("medium"):
        st.markdown("### Medium Priority")
        for i, rec in enumerate(prioritized.get("medium", []), 1):
            st.markdown(f"🟡 **{i}. {rec}**")
    
    if prioritized.get("low"):
        st.markdown("### Low Priority")
        for i, rec in enumerate(prioritized.get("low", []), 1):
            st.markdown(f"🟢 **{i}. {rec}**")


def prioritize_recommendations(recommendations: list) -> dict:
    """
    Prioritize recommendations based on keywords.
    
    Args:
        recommendations: List of recommendation strings
        
    Returns:
        Dictionary with 'high', 'medium', 'low' priority lists
    """
    high_priority_keywords = ["answer", "first paragraph", "structure", "schema"]
    medium_priority_keywords = ["citations", "statistics", "fact density"]
    
    prioritized = {
        "high": [],
        "medium": [],
        "low": []
    }
    
    for rec in recommendations:
        rec_lower = rec.lower()
        if any(keyword in rec_lower for keyword in high_priority_keywords):
            prioritized["high"].append(rec)
        elif any(keyword in rec_lower for keyword in medium_priority_keywords):
            prioritized["medium"].append(rec)
        else:
            prioritized["low"].append(rec)
    
    return prioritized

