"""Audit page for GEO Autopilot MVP."""

import json
from datetime import datetime

import plotly.express as px
import streamlit as st

from streamlit_helpers import load_audit_history, run_geo_audit, save_audit_result
from components.geo_score_card import render_score_card
from components.recommendations_list import render_recommendations


def render():
    """Render the audit page."""
    st.title("🔍 GEO Audit")
    st.markdown("Analyze any URL to get a comprehensive GEO score and recommendations.")
    
    # Initialize session state
    if "audit_results" not in st.session_state:
        st.session_state.audit_results = None
    if "audit_error" not in st.session_state:
        st.session_state.audit_error = None
    
    # URL input section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        url = st.text_input(
            "Enter URL to audit",
            placeholder="https://example.com/article",
            help="Enter the full URL of the page you want to audit"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📋 Sample URL", use_container_width=True):
            st.session_state.sample_url = "https://example.com/article"
            st.rerun()
    
    # Use sample URL if set
    if "sample_url" in st.session_state:
        url = st.session_state.sample_url
        del st.session_state.sample_url
    
    # Run audit button
    if st.button("🚀 Run GEO Audit", type="primary", use_container_width=True):
        if not url:
            st.error("Please enter a URL")
        else:
            with st.spinner("Analyzing content... This may take a few moments."):
                try:
                    audit_result = run_geo_audit(url)
                    st.session_state.audit_results = audit_result
                    st.session_state.audit_error = None
                    
                    # Save audit result
                    save_audit_result(audit_result)
                    st.success("Audit completed successfully!")
                except Exception as e:
                    st.session_state.audit_error = str(e)
                    st.session_state.audit_results = None
                    st.error(f"Error running audit: {str(e)}")
    
    # Display results
    if st.session_state.audit_results:
        results = st.session_state.audit_results
        display_audit_results(results)
    
    if st.session_state.audit_error:
        st.error(f"❌ {st.session_state.audit_error}")


def display_audit_results(results: dict):
    """Display audit results in a formatted way."""
    st.markdown("---")
    
    # Overall GEO Score
    total_score = results["geo_score"]["total_score"]
    render_score_card(total_score)
    
    # Score breakdown chart
    st.subheader("📊 Score Breakdown")
    breakdown = results["geo_score"]["breakdown"]
    
    # Create bar chart
    categories = list(breakdown.keys())
    scores = [breakdown[cat] for cat in categories]
    
    # Format category names for display
    display_categories = [cat.replace("_", " ").title() for cat in categories]
    
    fig = px.bar(
        x=display_categories,
        y=scores,
        labels={"x": "Category", "y": "Score"},
        color=scores,
        color_continuous_scale=["#d62728", "#ff7f0e", "#2ca02c"],
        range_color=[0, 100]
    )
    fig.update_layout(
        showlegend=False,
        height=400,
        yaxis_title="Score",
        xaxis_title=""
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed findings
    st.subheader("🔍 Detailed Findings")
    
    with st.expander("📝 Content Analysis", expanded=False):
        content_analysis = results.get("content_analysis", {})
        
        # First paragraph analysis
        if "first_paragraph_analysis" in content_analysis:
            fp_analysis = content_analysis["first_paragraph_analysis"]
            st.write("**First Paragraph Analysis:**")
            st.write(f"- Word count: {fp_analysis.get('word_count', 'N/A')}")
            st.write(f"- Meets optimal length (40-60 words): {fp_analysis.get('meets_length', False)}")
            st.write(f"- Score: {fp_analysis.get('score', 0):.1f}/100")
            if fp_analysis.get("first_paragraph"):
                st.text_area("First paragraph:", fp_analysis["first_paragraph"], height=100, disabled=True)
        
        # Statistics analysis
        if "statistics_analysis" in content_analysis:
            stats_analysis = content_analysis["statistics_analysis"]
            st.write("**Statistics Analysis:**")
            st.write(f"- Statistics found: {stats_analysis.get('statistics_count', 0)}")
            st.write(f"- Score: {stats_analysis.get('score', 0):.1f}/100")
        
        # Citations analysis
        if "citations_analysis" in content_analysis:
            citations_analysis = content_analysis["citations_analysis"]
            st.write("**Citations Analysis:**")
            st.write(f"- External links found: {citations_analysis.get('external_links_count', 0)}")
            st.write(f"- Score: {citations_analysis.get('score', 0):.1f}/100")
        
        # Expert quotes analysis
        if "expert_quotes_analysis" in content_analysis:
            quotes_analysis = content_analysis["expert_quotes_analysis"]
            st.write("**Expert Quotes Analysis:**")
            st.write(f"- Quotes found: {quotes_analysis.get('quotes_count', 0)}")
            st.write(f"- Score: {quotes_analysis.get('score', 0):.1f}/100")
        
        # Readability analysis
        if "readability_analysis" in content_analysis:
            readability_analysis = content_analysis["readability_analysis"]
            st.write("**Readability Analysis:**")
            st.write(f"- Flesch Reading Ease: {readability_analysis.get('flesch_reading_ease', 'N/A')}")
            st.write(f"- Score: {readability_analysis.get('score', 0):.1f}/100")
    
    with st.expander("⚙️ Technical Analysis", expanded=False):
        technical_analysis = results.get("technical_analysis", {})
        
        # Headings analysis
        if "headings_analysis" in technical_analysis:
            headings_analysis = technical_analysis["headings_analysis"]
            st.write("**Headings Structure:**")
            st.write(f"- H1 tags: {headings_analysis.get('h1_count', 0)}")
            st.write(f"- Total headings: {headings_analysis.get('total_headings', 0)}")
            st.write(f"- Structure score: {headings_analysis.get('structure_score', 0):.1f}/100")
        
        # Schema analysis
        if "schema_analysis" in technical_analysis:
            schema_analysis = technical_analysis["schema_analysis"]
            st.write("**Schema Markup:**")
            st.write(f"- Has schema: {schema_analysis.get('has_schema', False)}")
            st.write(f"- Schema types found: {', '.join(schema_analysis.get('schema_types', []))}")
            st.write(f"- Valid GEO types: {', '.join(schema_analysis.get('valid_types', []))}")
    
    # Recommendations
    st.subheader("💡 Recommendations")
    recommendations = results.get("recommendations", [])
    render_recommendations(recommendations)
    
    # Download buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        # JSON download
        json_str = json.dumps(results, indent=2, default=str)
        st.download_button(
            label="📥 Download JSON Report",
            data=json_str,
            file_name=f"geo_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # PDF download (placeholder - would need reportlab or similar)
        st.info("📄 PDF export coming soon")

