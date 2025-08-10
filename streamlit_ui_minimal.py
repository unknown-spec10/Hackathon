#!/usr/bin/env python3
"""
Minimal, sleek Streamlit UI for core functionality:
 - Auth (very lightweight)
 - Resume upload + AI / fallback analysis (using NLPInsightsAnalyzer)
 - Display of key metrics + recommendations (no heavy cards)
Design principles:
 - Flat layout, restrained color, native Streamlit components
 - Progressive disclosure via expanders & tabs
 - Avoid verbose marketing copy
"""
import os
import json
from datetime import datetime
import tempfile
import streamlit as st

# Optional dependencies are imported lazily only when needed

st.set_page_config(page_title="Talent Insights", page_icon="🧠", layout="wide")

# --- Helpers -----------------------------------------------------------------

def get_analyzer():
    from app.services.nlp_insights import NLPInsightsAnalyzer
    if 'analyzer' not in st.session_state:
        # Always use the synchronous fallback factory method
        try:
            st.session_state.analyzer = NLPInsightsAnalyzer.create_with_fallback()
        except Exception as e:
            st.error(f"Failed to create analyzer: {e}")
            return None
    return st.session_state.analyzer

# Simple in-memory user session (demo only)
if 'user' not in st.session_state:
    st.session_state.user = None

# --- Sidebar -----------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🧠 Talent Insights")
    st.caption("Minimal interface")

    if st.session_state.user:
        st.success(f"Logged in as {st.session_state.user}")
        if st.button("Logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.pop('latest_resume', None)
            st.rerun()
    else:
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="demo")
            submitted = st.form_submit_button("Start Session", use_container_width=True)
            if submitted:
                st.session_state.user = username or "demo"
                st.experimental_set_query_params(user=st.session_state.user)
                st.rerun()

    st.markdown("---")
    st.markdown("### Settings")
    ai_enabled = bool(os.getenv('GROQ_API_KEY'))
    st.checkbox("AI Mode (auto if key present)", value=ai_enabled, disabled=True, help="Set GROQ_API_KEY env var to enable")
    if st.button("Refresh Dynamic Keywords", use_container_width=True):
        try:
            analyzer = get_analyzer()
            if analyzer and hasattr(analyzer, 'refresh_dynamic_config'):
                analyzer.refresh_dynamic_config()
                st.toast("Dynamic config refreshed")
            else:
                st.toast("Refresh not available")
        except Exception as e:
            st.error(f"Refresh failed: {e}")

# --- Main Content ------------------------------------------------------------
st.title("Resume Insights & Recommendations")
st.caption("Upload a resume (JSON or simple text) to analyze skills & get career suggestions.")

if not st.session_state.user:
    st.info("Start a session from the sidebar to continue.")
    st.stop()

col_up, col_meta = st.columns([3,1])
with col_up:
    uploaded = st.file_uploader("Resume File", type=["txt", "json", "pdf"], help="PDF currently expects text-extractable content; JSON = structured resume.")
with col_meta:
    st.write("\n")
    analyze_btn = st.button("Analyze", type="primary", use_container_width=True, disabled=uploaded is None)

resume_payload = None
raw_text = ""

if uploaded is not None:
    suffix = uploaded.name.lower().split('.')[-1]
    content = uploaded.read()
    if suffix == 'json':
        try:
            resume_payload = json.loads(content.decode('utf-8'))
        except Exception as e:
            st.error(f"JSON parse error: {e}")
    elif suffix == 'txt':
        raw_text = content.decode('utf-8', errors='ignore')
        resume_payload = {
            'personal_info': {},
            'skills': [],
            'experience': [],
            'education': []
        }
    elif suffix == 'pdf':
        try:
            from app.services.pdf_processor import PDFProcessor  # fallback simple extractor if exists
            proc = PDFProcessor()
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            raw_text = proc.extract_text(tmp_path) or ''
            resume_payload = {'raw_text': raw_text}
        except Exception as e:
            st.warning(f"PDF extraction fallback: {e}")
            resume_payload = {'raw_text': ''}
    else:
        st.error("Unsupported file type")

if analyze_btn and resume_payload is not None:
    analyzer = get_analyzer()
    if not analyzer:
        st.error("Failed to initialize analyzer. Please check the configuration.")
        st.stop()
        
    with st.spinner("Analyzing resume ..."):
        try:
            insights = analyzer.analyze_resume_sync(resume_payload)
            st.session_state.latest_resume = {
                'insights': insights,
                'ts': datetime.utcnow().isoformat(),
                'name': uploaded.name,
            }
        except Exception as e:
            st.error(f"Analysis failed: {e}")

latest = st.session_state.get('latest_resume')
if latest:
    insights = latest['insights']
    st.subheader("Summary")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        overall_score = insights.overall_score if hasattr(insights, 'overall_score') else insights.get('overall_score', 0)
        st.metric("Overall Score", f"{overall_score*100:.0f}%")
    with m2:
        skill_analysis = insights.skill_analysis if hasattr(insights, 'skill_analysis') else insights.get('skill_analysis', {})
        st.metric("Skills", f"{skill_analysis.get('total_skills', 0)}")
    with m3:
        emerging_skills = skill_analysis.get('emerging_skills', [])
        st.metric("Emerging", f"{len(emerging_skills)}")
    with m4:
        experience_insights = insights.experience_insights if hasattr(insights, 'experience_insights') else insights.get('experience_insights', {})
        st.metric("Leadership", experience_insights.get('leadership_indicators', 0))

    tabs = st.tabs(["Skills", "Experience", "Education", "Personality", "Recommendations", "Raw"])

    # Skills
    with tabs[0]:
        sa = insights.skill_analysis
        st.markdown("**Core Competencies**")
        cc = sa.get('core_competencies', [])
        if cc:
            st.write(', '.join(cc))
        st.markdown("**Emerging Skills**")
        es = sa.get('emerging_skills', [])
        if es:
            st.write(', '.join(es[:25]))
        with st.expander("All Skill Categories"):
            for cat, vals in sa.get('skill_categories', {}).items():
                if vals:
                    st.write(f"{cat}: {len(vals)}")
        with st.expander("Full Skill Analysis JSON"):
            st.json(sa)

    # Experience
    with tabs[1]:
        ex = insights.experience_insights
        grid = {
            'Positions': ex.get('total_positions'),
            'Avg Tenure (mo)': ex.get('avg_tenure_months'),
            'Leadership Indicators': ex.get('leadership_indicators'),
            'Quality Score %': int((ex.get('experience_quality_score') or 0)*100)
        }
        st.json(grid)
        if ex.get('timeline'):
            st.markdown("**Timeline**")
            st.json(ex['timeline'][:5])

    # Education
    with tabs[2]:
        ed = insights.education_insights
        st.json(ed)

    # Personality
    with tabs[3]:
        pers = insights.personality_traits
        st.json(pers)

    # Recommendations
    with tabs[4]:
        recs = insights.career_recommendations
        if recs:
            for i, r in enumerate(recs, 1):
                st.write(f"{i}. {r}")
        else:
            st.info("No recommendations generated.")
        with st.expander("Strengths & Improvements"):
            st.write("**Strengths**")
            for s in insights.strengths:
                st.write(f"- {s}")
            st.write("**Areas for Improvement**")
            for a in insights.areas_for_improvement:
                st.write(f"- {a}")

    # Raw
    with tabs[5]:
        try:
            st.json(insights.model_dump())
        except Exception:
            # If not a pydantic model, fallback to __dict__
            st.json(getattr(insights, '__dict__', {}))
else:
    st.info("Upload and analyze a resume to see insights.")

st.markdown("---")
st.caption("Prototype UI • No persistence • Set GROQ_API_KEY for AI mode")
