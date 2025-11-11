"""Transform page for GEO Autopilot MVP."""

import streamlit as st

from streamlit_helpers import load_audit_history, run_geo_audit, transform_content
from components.content_comparison import render_content_comparison
from components.geo_score_card import render_score_card


def render():
    """Render the transform page."""
    st.title("✨ Content Transformation")
    st.markdown("Transform your content to improve GEO scores with AI-powered optimizations.")
    
    # Initialize session state
    if "transformation_results" not in st.session_state:
        st.session_state.transformation_results = None
    if "selected_audit" not in st.session_state:
        st.session_state.selected_audit = None
    
    # URL input or select from previous audits
    col1, col2 = st.columns([2, 1])
    
    with col1:
        url_input = st.text_input(
            "Enter URL or select from previous audits",
            placeholder="https://example.com/article",
            help="Enter a URL or select from your audit history"
        )
    
    with col2:
        # Load audit history
        audit_history = load_audit_history()
        if audit_history:
            audit_options = {f"{audit['url']} ({audit.get('audit_date', 'Unknown')})": audit for audit in audit_history[:10]}
            selected_audit_key = st.selectbox(
                "Or select from history",
                ["None"] + list(audit_options.keys()),
                help="Select a previously audited URL"
            )
            
            if selected_audit_key != "None":
                st.session_state.selected_audit = audit_options[selected_audit_key]
                url_input = audit_options[selected_audit_key]["url"]
        else:
            st.info("No audit history available")
    
    # Load content button
    if st.button("📥 Load Content", type="primary", use_container_width=True):
        if not url_input:
            st.error("Please enter a URL or select from audit history")
        else:
            with st.spinner("Loading and analyzing content..."):
                try:
                    audit_result = run_geo_audit(url_input)
                    st.session_state.selected_audit = audit_result
                    st.success("Content loaded successfully!")
                except Exception as e:
                    st.error(f"Error loading content: {str(e)}")
    
    # Display current content and score if available
    if st.session_state.selected_audit:
        audit = st.session_state.selected_audit
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Current Content")
            current_score = audit["geo_score"]["total_score"]
            render_score_card(current_score)
        
        with col2:
            st.subheader("Content Preview")
            text_content = audit.get("parsed_data", {}).get("text_content", "")
            word_count = len(text_content.split())
            st.metric("Word Count", word_count)
            st.text_area(
                "Content preview (first 500 chars)",
                text_content[:500] + "..." if len(text_content) > 500 else text_content,
                height=150,
                disabled=True
            )
        
        # Transformation options
        st.markdown("---")
        st.subheader("🛠️ Transformation Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            add_statistics = st.checkbox(
                "➕ Add Statistics",
                help="Add relevant statistics and data points to improve fact density"
            )
            add_citations = st.checkbox(
                "🔗 Add Citations",
                help="Add external links and citations to authoritative sources"
            )
            add_expert_quotes = st.checkbox(
                "💬 Add Expert Quotes",
                help="Add expert quotes and testimonials to enhance credibility"
            )
        
        with col2:
            optimize_structure = st.checkbox(
                "📐 Optimize Structure",
                help="Improve heading hierarchy and content structure"
            )
            generate_schema = st.checkbox(
                "🏷️ Generate Schema Markup",
                help="Generate structured data (JSON-LD) markup"
            )
        
        # Transform button
        if st.button("✨ Transform Content", type="primary", use_container_width=True):
            transformation_options = {
                "add_statistics": add_statistics,
                "add_citations": add_citations,
                "add_expert_quotes": add_expert_quotes,
                "optimize_structure": optimize_structure,
                "generate_schema": generate_schema
            }
            
            if not any(transformation_options.values()):
                st.warning("Please select at least one transformation option")
            else:
                with st.spinner("Transforming content... This may take a few moments."):
                    try:
                        parsed_data = audit.get("parsed_data", {})
                        transform_result = transform_content(parsed_data, transformation_options)
                        st.session_state.transformation_results = transform_result
                        st.success("Transformation completed!")
                    except Exception as e:
                        st.error(f"Error transforming content: {str(e)}")
        
        # Display transformation results
        if st.session_state.transformation_results:
            results = st.session_state.transformation_results
            display_transformation_results(results)
    else:
        st.info("👆 Enter a URL and click 'Load Content' to get started")


def display_transformation_results(results: dict):
    """Display transformation results."""
    st.markdown("---")
    st.subheader("📊 Transformation Results")
    
    # Score comparison
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Score Before",
            f"{results['original_score']:.1f}",
            delta=None
        )
    
    with col2:
        improvement = results.get("score_improvement", 0)
        st.metric(
            "Score After",
            f"{results['transformed_score']:.1f}",
            delta=f"{improvement:+.1f}" if improvement != 0 else None
        )
    
    with col3:
        improvement_pct = ((results['transformed_score'] - results['original_score']) / results['original_score'] * 100) if results['original_score'] > 0 else 0
        st.metric(
            "Improvement",
            f"{improvement_pct:.1f}%"
        )
    
    # Side-by-side content comparison
    st.markdown("---")
    render_content_comparison(
        results["original_content"],
        results["transformed_content"]
    )
    
    # Transformations applied
    st.markdown("---")
    st.subheader("✅ Transformations Applied")
    transformations = results.get("transformations_applied", [])
    if transformations:
        for i, transformation in enumerate(transformations, 1):
            st.write(f"{i}. {transformation}")
    else:
        st.info("No transformations were applied")
    
    # Apply changes button
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("📋 Copy Transformed Content", use_container_width=True):
            st.code(results["transformed_content"], language="text")
            st.success("Content copied to clipboard! (In production, this would copy to clipboard)")
    
    with col2:
        st.info("💡 In production, this would integrate with your CMS or provide direct download")

