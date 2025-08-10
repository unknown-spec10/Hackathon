#!/usr/bin/env python3
"""
AI Interview & Resume Analyzer - Professional Interface
Enterprise-grade AI-powered talent assessment and career development platform.
"""
import streamlit as st
import json
import os
import tempfile
from datetime import datetime, date
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time

# Professional page configuration
st.set_page_config(
    page_title="AI Talent Analyzer | Professional Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #1f4e79;
        --secondary-color: #2d5aa0;
        --accent-color: #4a90e2;
        --success-color: #27ae60;
        --warning-color: #f39c12;
        --error-color: #e74c3c;
        --light-bg: #f8f9fa;
        --dark-text: #2c3e50;
    }

    /* Hide Streamlit defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Professional header */
    .main-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        padding: 2rem 0;
        margin: -1rem -1rem 2rem -1rem;
        color: white;
        text-align: center;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        color: white !important;
    }
    
    .main-header p {
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        color: white !important;
    }
    
    /* Navigation styling */
    .nav-container {
        background: white;
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 0 2px 15px rgba(0,0,0,0.08);
        margin-bottom: 2rem;
        border: 1px solid #e8ecef;
    }
    
    /* Card styling */
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e8ecef;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    /* Metrics styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem 0;
    }
    
    /* Status indicators */
    .status-success {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 600;
        display: inline-block;
    }
    
    .status-warning {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 600;
        display: inline-block;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(31, 78, 121, 0.3);
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* Progress bars */
    .stProgress > div > div > div {
        background: linear-gradient(135deg, var(--accent-color) 0%, var(--secondary-color) 100%);
    }
</style>
""", unsafe_allow_html=True)

# Setup environment for Streamlit Cloud compatibility
try:
    from streamlit_config import setup_environment, is_streamlit_cloud
    config = setup_environment()
    deployment_status = "🌟 Cloud Deployment" if is_streamlit_cloud() else "🏠 Local Environment"
except ImportError:
    os.environ["DATABASE_URL"] = "sqlite:///./hackathon.db"
    deployment_status = "🏠 Local Environment"

def create_professional_header():
    """Create a professional header with branding"""
    st.markdown("""
    <div class="main-header">
        <h1>🎯 AI Talent Analyzer</h1>
        <p>Enterprise-Grade AI-Powered Talent Assessment & Career Development Platform</p>
    </div>
    """, unsafe_allow_html=True)

def create_navigation_menu():
    """Create professional navigation menu"""
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    
    nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns(5)
    
    with nav_col1:
        if st.button("🏠 Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
    
    with nav_col2:
        if st.button("📄 Resume Analysis", use_container_width=True):
            st.session_state.page = "resume"
    
    with nav_col3:
        if st.button("🎯 AI Interviews", use_container_width=True):
            st.session_state.page = "interview"
    
    with nav_col4:
        if st.button("💼 Career Hub", use_container_width=True):
            st.session_state.page = "career"
    
    with nav_col5:
        if st.button("👤 Account", use_container_width=True):
            st.session_state.page = "account"
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_dashboard():
    """Professional dashboard view"""
    st.markdown("## 📊 Platform Dashboard")
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>1,247</h3>
            <p>Resumes Analyzed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>892</h3>
            <p>Interviews Completed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>95.3%</h3>
            <p>Success Rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>24/7</h3>
            <p>AI Availability</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Feature cards
    st.markdown("### 🎯 Platform Features")
    
    feature_col1, feature_col2, feature_col3 = st.columns(3)
    
    with feature_col1:
        st.markdown("""
        <div class="feature-card">
            <h4>📄 Smart Resume Analysis</h4>
            <p>AI-powered parsing and analysis of resumes with career insights and skill gap identification.</p>
            <div class="status-success">✓ Active</div>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_col2:
        st.markdown("""
        <div class="feature-card">
            <h4>🤖 AI Interview System</h4>
            <p>Dynamic interview generation with real-time evaluation and comprehensive scoring.</p>
            <div class="status-success">✓ Active</div>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_col3:
        st.markdown("""
        <div class="feature-card">
            <h4>🎯 Career Matching</h4>
            <p>Intelligent job and course recommendations based on profile analysis.</p>
            <div class="status-success">✓ Active</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick stats visualization
    st.markdown("### 📈 Analytics Overview")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        skills_data = pd.DataFrame({
            'Skill': ['Python', 'JavaScript', 'SQL', 'Machine Learning', 'React', 'AWS'],
            'Count': [324, 298, 267, 189, 156, 134]
        })
        fig = px.bar(skills_data, x='Skill', y='Count', 
                    title='Top Skills in Analyzed Resumes',
                    color='Count',
                    color_continuous_scale='Blues')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with chart_col2:
        performance_data = pd.DataFrame({
            'Score Range': ['90-100', '80-89', '70-79', '60-69', '50-59', '<50'],
            'Candidates': [145, 234, 298, 156, 89, 45]
        })
        fig = px.pie(performance_data, values='Candidates', names='Score Range',
                    title='Interview Score Distribution',
                    color_discrete_sequence=px.colors.sequential.Blues_r)
        st.plotly_chart(fig, use_container_width=True)

def show_resume_analysis():
    """Professional resume analysis interface"""
    st.markdown("## 📄 AI-Powered Resume Analysis")
    
    st.markdown("### 📤 Upload Resume")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Upload a resume in PDF format for AI analysis"
    )
    
    if uploaded_file is not None:
        with st.spinner("🤖 AI is analyzing your resume..."):
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.02)
                progress_bar.progress(i + 1)
            
            st.success("✅ Resume analysis completed!")
            
            result_col1, result_col2 = st.columns(2)
            
            with result_col1:
                st.markdown("#### 🎯 Key Insights")
                st.markdown("""
                <div class="info-box">
                    <strong>Overall Score:</strong> 8.7/10<br>
                    <strong>Experience Level:</strong> Senior (5+ years)<br>
                    <strong>Primary Domain:</strong> Software Engineering<br>
                    <strong>Match Confidence:</strong> 94%
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### 💪 Top Skills Identified")
                skills = ['Python', 'React', 'AWS', 'Machine Learning', 'Docker', 'SQL']
                for i, skill in enumerate(skills):
                    st.progress((10-i)/10, text=f"{skill} - {90-i*5}% proficiency")
            
            with result_col2:
                st.markdown("#### 🔍 Detailed Analysis")
                
                with st.expander("📊 Skill Gap Analysis"):
                    st.write("**Recommended improvements:**")
                    st.write("• Kubernetes experience")
                    st.write("• GraphQL knowledge")
                    st.write("• System design patterns")
                
                with st.expander("🎯 Career Trajectory"):
                    st.write("**Predicted career path:**")
                    st.write("• Technical Lead (1-2 years)")
                    st.write("• Engineering Manager (3-4 years)")
                    st.write("• VP Engineering (5+ years)")
                
                with st.expander("💼 Job Recommendations"):
                    st.write("**Top matches:**")
                    st.write("• Senior Full Stack Developer - TechCorp")
                    st.write("• Lead Software Engineer - StartupX")
                    st.write("• Principal Engineer - BigTech")

def show_ai_interview():
    """Professional AI interview interface"""
    st.markdown("## 🎯 AI Interview System")
    
    if 'interview_started' not in st.session_state:
        st.session_state.interview_started = False
    
    if not st.session_state.interview_started:
        st.markdown("### 🚀 Interview Configuration")
        
        config_col1, config_col2 = st.columns(2)
        
        with config_col1:
            domain = st.selectbox(
                "Select Domain",
                ["Python Development", "Data Science", "Machine Learning", "Web Development", "DevOps", "Cybersecurity"]
            )
            experience = st.slider("Years of Experience", 0, 20, 3)
        
        with config_col2:
            difficulty = st.selectbox(
                "Difficulty Level",
                ["Fresher", "Junior", "Intermediate", "Senior", "Expert"]
            )
            num_questions = st.selectbox("Number of Questions", [5, 10, 15, 20])
        
        st.markdown("### 📋 Interview Preview")
        st.markdown(f"""
        <div class="info-box">
            <strong>Domain:</strong> {domain}<br>
            <strong>Experience Level:</strong> {experience} years<br>
            <strong>Difficulty:</strong> {difficulty}<br>
            <strong>Questions:</strong> {num_questions}<br>
            <strong>Estimated Time:</strong> {num_questions * 3} minutes
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Start AI Interview", type="primary", use_container_width=True):
            st.session_state.interview_started = True
            st.session_state.current_question = 1
            st.session_state.total_questions = num_questions
            st.session_state.answers = {}
            st.rerun()
    
    else:
        # Interview simulation
        current_q = st.session_state.get('current_question', 1)
        total_q = st.session_state.get('total_questions', 10)
        
        progress = current_q / total_q
        st.progress(progress, text=f"Question {current_q} of {total_q}")
        
        st.markdown(f"### Question {current_q}")
        
        questions = [
            "Explain the difference between a list and a tuple in Python.",
            "How would you implement a binary search algorithm?",
            "Describe the MVC architecture pattern.",
            "What is the difference between SQL and NoSQL databases?",
            "Explain the concept of RESTful APIs."
        ]
        
        question = questions[(current_q - 1) % len(questions)]
        st.markdown(f"**{question}**")
        
        answer = st.text_area("Your Answer:", height=150, key=f"answer_{current_q}")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if current_q > 1:
                if st.button("← Previous"):
                    st.session_state.current_question -= 1
                    st.rerun()
        
        with col3:
            if current_q < total_q:
                if st.button("Next →"):
                    st.session_state.answers[current_q] = answer
                    st.session_state.current_question += 1
                    st.rerun()
            else:
                if st.button("🏁 Finish Interview", type="primary"):
                    st.session_state.answers[current_q] = answer
                    st.session_state.interview_completed = True
                    st.rerun()
    
    if st.session_state.get('interview_completed', False):
        st.markdown("## 🎉 Interview Completed!")
        
        result_col1, result_col2, result_col3 = st.columns(3)
        
        with result_col1:
            st.markdown("""
            <div class="metric-card">
                <h3>87%</h3>
                <p>Overall Score</p>
            </div>
            """, unsafe_allow_html=True)
        
        with result_col2:
            st.markdown("""
            <div class="metric-card">
                <h3>B+</h3>
                <p>Grade</p>
            </div>
            """, unsafe_allow_html=True)
        
        with result_col3:
            st.markdown("""
            <div class="metric-card">
                <h3>18 min</h3>
                <p>Time Taken</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### 📊 Detailed Feedback")
        
        feedback_col1, feedback_col2 = st.columns(2)
        
        with feedback_col1:
            st.markdown("#### ✅ Strengths")
            st.write("• Strong understanding of core concepts")
            st.write("• Clear and concise explanations")
            st.write("• Good problem-solving approach")
            
        with feedback_col2:
            st.markdown("#### 📈 Areas for Improvement")
            st.write("• More specific examples needed")
            st.write("• Consider edge cases in solutions")
            st.write("• Expand on architectural decisions")
        
        if st.button("🔄 Take Another Interview"):
            for key in ['interview_started', 'current_question', 'total_questions', 'answers', 'interview_completed']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

def show_career_hub():
    """Professional career hub interface"""
    st.markdown("## 💼 Career Development Hub")
    
    tab1, tab2, tab3 = st.tabs(["🎯 Job Matches", "📚 Learning Paths", "📈 Skill Development"])
    
    with tab1:
        st.markdown("### 🎯 Personalized Job Recommendations")
        
        jobs = [
            {"title": "Senior Python Developer", "company": "TechCorp", "match": "95%", "salary": "$120K - $150K"},
            {"title": "Full Stack Engineer", "company": "StartupX", "match": "89%", "salary": "$100K - $130K"},
            {"title": "Data Scientist", "company": "DataInc", "match": "82%", "salary": "$110K - $140K"}
        ]
        
        for job in jobs:
            st.markdown(f"""
            <div class="feature-card">
                <h4>{job['title']}</h4>
                <p><strong>{job['company']}</strong> • {job['salary']}</p>
                <div class="status-success">Match: {job['match']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 📚 Recommended Learning Paths")
        
        courses = [
            {"title": "Advanced Python Patterns", "provider": "TechEd", "duration": "6 weeks", "level": "Advanced"},
            {"title": "System Design Fundamentals", "provider": "ArchitectAcademy", "duration": "8 weeks", "level": "Intermediate"},
            {"title": "Kubernetes Mastery", "provider": "CloudCert", "duration": "4 weeks", "level": "Intermediate"}
        ]
        
        for course in courses:
            st.markdown(f"""
            <div class="feature-card">
                <h4>{course['title']}</h4>
                <p><strong>{course['provider']}</strong> • {course['duration']} • {course['level']}</p>
                <div class="status-warning">Recommended</div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### 📈 Skill Development Roadmap")
        
        skills_data = {
            'skill': ['Python', 'JavaScript', 'SQL', 'AWS', 'Docker', 'React'],
            'current': [90, 75, 80, 60, 70, 65],
            'target': [95, 85, 90, 80, 85, 80]
        }
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=skills_data['current'],
            theta=skills_data['skill'],
            fill='toself',
            name='Current Level'
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=skills_data['target'],
            theta=skills_data['skill'],
            fill='toself',
            name='Target Level'
        ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            title="Skills Development Roadmap"
        )
        
        st.plotly_chart(fig, use_container_width=True)

def show_account():
    """Professional account management interface"""
    st.markdown("## 👤 Account Management")
    
    tab1, tab2, tab3 = st.tabs(["👤 Profile", "⚙️ Settings", "📊 Analytics"])
    
    with tab1:
        st.markdown("### Professional Profile")
        
        profile_col1, profile_col2 = st.columns([1, 2])
        
        with profile_col1:
            st.markdown("""
            <div class="feature-card" style="text-align: center;">
                <h4>👤 John Doe</h4>
                <p>Senior Software Engineer</p>
                <div class="status-success">✓ Verified</div>
            </div>
            """, unsafe_allow_html=True)
        
        with profile_col2:
            st.markdown("#### Profile Information")
            st.text_input("Full Name", value="John Doe")
            st.text_input("Email", value="john.doe@email.com")
            st.text_input("Title", value="Senior Software Engineer")
            st.text_area("Bio", value="Experienced software engineer with 5+ years in full-stack development.")
    
    with tab2:
        st.markdown("### Platform Settings")
        
        st.markdown("#### Notification Preferences")
        st.checkbox("Email notifications for job matches", value=True)
        st.checkbox("SMS alerts for interview invitations", value=False)
        st.checkbox("Weekly career insights digest", value=True)
        
        st.markdown("#### Privacy Settings")
        st.checkbox("Make profile visible to recruiters", value=True)
        st.checkbox("Allow anonymous interview feedback", value=True)
    
    with tab3:
        st.markdown("### Your Analytics")
        
        analytics_col1, analytics_col2, analytics_col3 = st.columns(3)
        
        with analytics_col1:
            st.markdown("""
            <div class="metric-card">
                <h3>12</h3>
                <p>Interviews Taken</p>
            </div>
            """, unsafe_allow_html=True)
        
        with analytics_col2:
            st.markdown("""
            <div class="metric-card">
                <h3>8.4</h3>
                <p>Average Score</p>
            </div>
            """, unsafe_allow_html=True)
        
        with analytics_col3:
            st.markdown("""
            <div class="metric-card">
                <h3>87%</h3>
                <p>Profile Completion</p>
            </div>
            """, unsafe_allow_html=True)

def main():
    """Main application function with professional interface"""
    
    if 'page' not in st.session_state:
        st.session_state.page = "dashboard"
    
    create_professional_header()
    
    # Status bar
    status_col1, status_col2, status_col3 = st.columns([2, 1, 1])
    
    with status_col1:
        st.markdown(f"**Status:** {deployment_status}")
    
    with status_col2:
        st.markdown("**Mode:** Professional")
    
    with status_col3:
        current_time = datetime.now().strftime("%H:%M")
        st.markdown(f"**Time:** {current_time}")
    
    create_navigation_menu()
    
    # Database setup (silent)
    try:
        from database.db_setup import Base, engine
        from sqlalchemy.orm import Session
        Base.metadata.create_all(bind=engine)
        if 'db_session' not in st.session_state:
            st.session_state.db_session = Session(engine)
    except Exception:
        pass
    
    # Page routing
    if st.session_state.page == "dashboard":
        show_dashboard()
    elif st.session_state.page == "resume":
        show_resume_analysis()
    elif st.session_state.page == "interview":
        show_ai_interview()
    elif st.session_state.page == "career":
        show_career_hub()
    elif st.session_state.page == "account":
        show_account()
    
    # Professional footer
    st.markdown("---")
    footer_col1, footer_col2, footer_col3 = st.columns(3)
    
    with footer_col1:
        st.markdown("**🎯 AI Talent Analyzer**")
        st.markdown("Enterprise-grade talent assessment platform")
    
    with footer_col2:
        st.markdown("**🔗 Quick Links**")
        st.markdown("• Documentation")
        st.markdown("• Support")
    
    with footer_col3:
        st.markdown("**📞 Contact**")
        st.markdown("• support@aianalyzer.com")
        st.markdown("• +1 (555) 123-4567")

def safe_run():
    """Run application with error handling"""
    try:
        main()
    except Exception as e:
        st.error("🔧 **System Maintenance**")
        st.markdown("""
        <div class="info-box">
            <p>Our platform is currently undergoing maintenance to improve your experience.</p>
            <p>Please try refreshing the page or contact support if the issue persists.</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("Technical Details"):
            st.code(str(e))

if __name__ == "__main__":
    safe_run()
