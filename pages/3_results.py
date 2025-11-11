"""Results page for GEO Autopilot MVP."""

import json
from datetime import datetime

import pandas as pd
import streamlit as st

from streamlit_helpers import load_audit_history


def render():
    """Render the results page."""
    st.title("📈 Audit History & Results")
    st.markdown("View your audit history and track improvements over time.")
    
    # Load audit history
    audits = load_audit_history()
    
    if not audits:
        st.info("📭 No audit history found. Run some audits to see results here!")
        return
    
    # Summary statistics
    st.subheader("📊 Summary Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_audits = len(audits)
    avg_score = sum(audit["geo_score"]["total_score"] for audit in audits) / total_audits if audits else 0
    latest_score = audits[0]["geo_score"]["total_score"] if audits else 0
    
    with col1:
        st.metric("Total Audits", total_audits)
    
    with col2:
        st.metric("Average Score", f"{avg_score:.1f}")
    
    with col3:
        st.metric("Latest Score", f"{latest_score:.1f}")
    
    with col4:
        unique_urls = len(set(audit["url"] for audit in audits))
        st.metric("Unique URLs", unique_urls)
    
    # Audit history table
    st.markdown("---")
    st.subheader("📋 Audit History")
    
    # Prepare data for table
    table_data = []
    for audit in audits:
        score = audit["geo_score"]["total_score"]
        audit_date = audit.get("audit_date", "")
        
        # Try to parse date
        try:
            if isinstance(audit_date, str):
                date_obj = datetime.fromisoformat(audit_date.replace("Z", "+00:00"))
                formatted_date = date_obj.strftime("%Y-%m-%d %H:%M")
            else:
                formatted_date = str(audit_date)
        except Exception:
            formatted_date = str(audit_date)
        
        table_data.append({
            "URL": audit["url"],
            "Date": formatted_date,
            "Score": f"{score:.1f}",
            "Score (Raw)": score  # For sorting
        })
    
    df = pd.DataFrame(table_data)
    
    # Display table with clickable rows
    selected_index = st.selectbox(
        "Select an audit to view details",
        range(len(df)),
        format_func=lambda x: f"{df.iloc[x]['URL']} - {df.iloc[x]['Date']} (Score: {df.iloc[x]['Score']})"
    )
    
    # Display selected audit details
    if selected_index is not None:
        selected_audit = audits[selected_index]
        display_audit_details(selected_audit)
    
    # Export functionality
    st.markdown("---")
    st.subheader("📥 Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Export as JSON
        json_data = json.dumps(audits, indent=2, default=str)
        st.download_button(
            label="📥 Export All as JSON",
            data=json_data,
            file_name=f"geo_audits_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # Export as CSV
        csv_data = df.drop(columns=["Score (Raw)"]).to_csv(index=False)
        st.download_button(
            label="📥 Export Table as CSV",
            data=csv_data,
            file_name=f"geo_audits_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )


def display_audit_details(audit: dict):
    """Display detailed information about a specific audit."""
    st.markdown("---")
    st.subheader("🔍 Audit Details")
    
    # Basic info
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**URL:**")
        st.write(audit["url"])
        
        st.write("**Audit Date:**")
        audit_date = audit.get("audit_date", "")
        try:
            if isinstance(audit_date, str):
                date_obj = datetime.fromisoformat(audit_date.replace("Z", "+00:00"))
                st.write(date_obj.strftime("%Y-%m-%d %H:%M:%S"))
            else:
                st.write(str(audit_date))
        except Exception:
            st.write(str(audit_date))
    
    with col2:
        score = audit["geo_score"]["total_score"]
        st.metric("GEO Score", f"{score:.1f}")
        
        breakdown = audit["geo_score"]["breakdown"]
        st.write("**Score Breakdown:**")
        for category, score_value in breakdown.items():
            display_name = category.replace("_", " ").title()
            st.write(f"- {display_name}: {score_value:.1f}")
    
    # Recommendations
    recommendations = audit.get("recommendations", [])
    if recommendations:
        st.write("**Recommendations:**")
        for i, rec in enumerate(recommendations, 1):
            st.write(f"{i}. {rec}")
    
    # Full JSON view
    with st.expander("📄 View Full JSON"):
        st.json(audit)

