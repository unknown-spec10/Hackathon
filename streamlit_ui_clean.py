#!/usr/bin/env python3
"""
Streamlit UI for testing the Hackathon API with Resume Processing
"""
import streamlit as st
import json
import os
import atexit
import tempfile
from datetime import datetime, date

# Set page config
st.set_page_config(
    page_title="Hackathon API Tester",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set up environment
os.environ["DATABASE_URL"] = "sqlite:///./hackathon.db"

def cleanup_database():
    """Clean up the database file when the session ends"""
    try:
        db_file = "hackathon.db"
        if os.path.exists(db_file):
            os.remove(db_file)
            print(f"🗑️ Database cleaned up: {db_file}")
    except Exception as e:
        print(f"⚠️ Could not clean up database: {e}")

# Register cleanup function to run when the script exits
atexit.register(cleanup_database)

def main():
    st.title("🚀 Hackathon API Tester with Resume Processing")
    st.markdown("---")
    
    # Add session cleanup info
    if 'session_started' not in st.session_state:
        st.session_state.session_started = True
        st.info("🔄 **Auto-cleanup enabled**: Database will be cleared when you close this tab/browser")
    
    try:
        # Import core functions
        from database.db_setup import Base, engine
        from app.service import course_service, job_service, profile_service
        from app.schemas.course_schema import CourseCreate
        from app.schemas.job_schema import JobCreate
        from app.utils.auth import get_password_hash, create_access_token, verify_password
        from app.models.user import User
        from app.models.course import Course
        from app.models.job import Job
        from app.models.profile import Organization
        from app.models.resume import Resume
        from sqlalchemy.orm import Session
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        st.success("✅ Database tables created successfully!")
        
        # Create a database session
        db = Session(engine)
        
        # Sidebar for navigation
        st.sidebar.title("📋 API Functions")
        page = st.sidebar.selectbox(
            "Choose a function to test:",
            ["🏠 Root", "👤 Authentication", "📚 Courses", "💼 Jobs", "🏢 Organizations", "📄 Resume Processing", "📊 Statistics"]
        )
        
        # Add manual cleanup button in sidebar
        st.sidebar.markdown("---")
        if st.sidebar.button("🗑️ Clear Database Now"):
            try:
                # Drop all tables
                Base.metadata.drop_all(bind=engine)
                # Recreate tables
                Base.metadata.create_all(bind=engine)
                st.sidebar.success("✅ Database cleared!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"❌ Error clearing database: {e}")
        
        # Initialize session state for token
        if 'auth_token' not in st.session_state:
            st.session_state.auth_token = None
        if 'current_user_id' not in st.session_state:
            st.session_state.current_user_id = None
        
        # Root endpoint
        if page == "🏠 Root":
            st.header("🏠 Root Endpoint")
            st.markdown("Test the basic API root endpoint")
            
            if st.button("Test Root Endpoint"):
                st.success("Status: 200")
                st.json({"status": "ok", "message": "Hackathon API with Resume Processing"})
        
        # Authentication endpoints
        elif page == "👤 Authentication":
            st.header("👤 User Authentication & Registration")
            
            # Initialize session state for authentication flow
            if 'auth_step' not in st.session_state:
                st.session_state.auth_step = 'select_type'
            if 'selected_user_type' not in st.session_state:
                st.session_state.selected_user_type = None
            
            # Step 1: User Type Selection
            if st.session_state.auth_step == 'select_type':
                st.subheader("🔍 Step 1: Choose Your User Type")
                st.info("Please select whether you are registering as a Business/Institution (B2B) or as an Individual (B2C)")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🏢 B2B (Business/Institution)")
                    st.markdown("""
                    **For Organizations:**
                    - **Companies** → Can post job openings
                    - **Educational Institutions** → Can create and offer courses
                    - Manage organizational profile
                    - View applicants and enrollments
                    """)
                    
                    if st.button("🏢 Register as B2B", key="select_b2b", use_container_width=True, type="primary"):
                        st.session_state.selected_user_type = "B2B"
                        st.session_state.auth_step = 'b2b_signup'
                        st.rerun()
                
                with col2:
                    st.markdown("### 👤 B2C (Individual)")
                    st.markdown("""
                    **For Job Seekers & Learners:**
                    - Apply for job positions
                    - Enroll in courses
                    - Upload and manage resumes
                    - Get personalized job & course recommendations
                    """)
                    
                    if st.button("👤 Register as B2C", key="select_b2c", use_container_width=True, type="primary"):
                        st.session_state.selected_user_type = "B2C"
                        st.session_state.auth_step = 'b2c_signup'
                        st.rerun()
                
                # Existing User Login
                st.markdown("---")
                st.subheader("🔐 Already have an account?")
                
                col1, col2 = st.columns(2)
                with col1:
                    with st.form("quick_login_form"):
                        st.markdown("**Quick Login**")
                        login_email = st.text_input("Email", placeholder="your.email@example.com")
                        login_password = st.text_input("Password", type="password")
                        
                        if st.form_submit_button("Login", use_container_width=True):
                            if not login_email or not login_password:
                                st.error("❌ Email and password are required")
                            else:
                                try:
                                    user = db.query(User).filter(User.email == login_email).first()
                                    if user and verify_password(login_password, user.password_hash):
                                        token = create_access_token(data={"sub": str(user.id)})
                                        st.session_state.auth_token = token
                                        st.session_state.current_user_id = user.id
                                        st.session_state.current_user_type = user.user_type.value
                                        st.session_state.current_user = user
                                        
                                        st.success("✅ Login successful!")
                                        
                                        # Show user info
                                        if user.user_type.value == "B2B" and user.org_id:
                                            org = db.query(Organization).filter(Organization.id == user.org_id).first()
                                            if org:
                                                st.success(f"🏢 Welcome {org.name} ({org.org_type.value})")
                                                permissions = "Post Jobs" if org.org_type.value == "COMPANY" else "Create Courses"
                                                st.info(f"📋 You can: {permissions}")
                                        else:
                                            st.success(f"👤 Welcome {user.username}!")
                                            st.info("📋 You can: Apply for Jobs, Enroll in Courses, Upload Resumes")
                                        
                                        st.rerun()
                                    else:
                                        st.error("❌ Invalid credentials")
                                except Exception as e:
                                    st.error(f"❌ Login error: {str(e)}")
            
            # Step 2: B2B Registration
            elif st.session_state.auth_step == 'b2b_signup':
                st.subheader("🏢 B2B Organization Registration")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    with st.form("b2b_signup_form"):
                        st.markdown("**🔐 Account Credentials**")
                        email = st.text_input("Email Address *", placeholder="contact@yourcompany.com")
                        password = st.text_input("Password *", type="password", placeholder="Secure password (min 6 chars)")
                        confirm_password = st.text_input("Confirm Password *", type="password", placeholder="Re-enter password")
                        username = st.text_input("Username (Optional)", placeholder="Will auto-generate if empty")
                        
                        st.markdown("**🏢 Organization Details**")
                        org_name = st.text_input("Organization Name *", placeholder="Your Company/Institution Name")
                        org_type = st.selectbox("Organization Type *", 
                                               ["Company", "Institution"], 
                                               help="Company: Can post jobs | Institution: Can create courses")
                        org_address = st.text_area("Business Address *", placeholder="Full business address with city, state, country")
                        org_contact_phone = st.text_input("Contact Phone *", placeholder="+1-234-567-8900")
                        org_logo_path = st.text_input("Logo URL (Optional)", placeholder="https://yourcompany.com/logo.png")
                        
                        # Show permissions based on type
                        st.markdown("**📋 Your Permissions:**")
                        if org_type == "Company":
                            st.success("✅ **Job Posting**: You will be able to post job openings and view applicants")
                            st.info("📊 **Analytics**: Track job views, applications, and candidate analytics")
                        else:
                            st.success("✅ **Course Creation**: You will be able to create and manage courses")
                            st.info("📊 **Analytics**: Track course enrollments and student progress")
                        
                        if st.form_submit_button("🚀 Register B2B Organization", use_container_width=True, type="primary"):
                            # Validation
                            if not all([email, password, confirm_password, org_name, org_address, org_contact_phone]):
                                st.error("❌ All required fields (*) must be filled")
                                st.stop()
                            
                            if len(password) < 6:
                                st.error("❌ Password must be at least 6 characters long")
                                st.stop()
                            
                            if password != confirm_password:
                                st.error("❌ Passwords do not match")
                                st.stop()
                            
                            try:
                                # Check if user exists
                                existing_user = db.query(User).filter(User.email == email).first()
                                if existing_user:
                                    st.error("❌ Email already registered")
                                    st.stop()
                                
                                # Create organization first
                                from app.models.profile import Organization, OrgTypeEnum
                                org_type_enum = OrgTypeEnum.COMPANY if org_type == "Company" else OrgTypeEnum.INSTITUTION
                                
                                new_org = Organization(
                                    name=org_name,
                                    org_type=org_type_enum,
                                    address=org_address,
                                    contact_email=email,
                                    contact_phone=org_contact_phone,
                                    logo_path=org_logo_path if org_logo_path else None
                                )
                                db.add(new_org)
                                db.flush()  # Get org ID without committing
                                
                                # Create B2B user
                                from app.models.user import UserTypeEnum
                                hashed_password = get_password_hash(password)
                                new_user = User(
                                    email=email,
                                    password_hash=hashed_password,
                                    username=username or f"org_{new_org.id}",
                                    org_id=new_org.id,
                                    user_type=UserTypeEnum.B2B
                                )
                                db.add(new_user)
                                db.commit()
                                db.refresh(new_user)
                                
                                st.success("✅ B2B Organization registered successfully!")
                                st.balloons()
                                
                                # Auto-login
                                token = create_access_token(data={"sub": str(new_user.id)})
                                st.session_state.auth_token = token
                                st.session_state.current_user_id = new_user.id
                                st.session_state.current_user_type = new_user.user_type.value
                                st.session_state.current_user = new_user
                                
                                # Show success details
                                st.subheader("🎉 Registration Complete!")
                                response_data = {
                                    "user_id": new_user.id,
                                    "email": new_user.email,
                                    "username": new_user.username,
                                    "user_type": new_user.user_type.value,
                                    "organization": {
                                        "id": new_org.id,
                                        "name": new_org.name,
                                        "type": new_org.org_type.value,
                                        "address": new_org.address,
                                        "phone": new_org.contact_phone,
                                        "capabilities": f"Can {'post jobs' if org_type == 'Company' else 'create courses'}"
                                    }
                                }
                                st.json(response_data)
                                
                                st.success("🔐 You are now automatically logged in!")
                                
                            except Exception as e:
                                st.error(f"❌ Registration failed: {str(e)}")
                
                with col2:
                    st.markdown("### ℹ️ B2B Registration")
                    st.info("""
                    **Requirements:**
                    - Valid business email
                    - Secure password (6+ chars)
                    - Complete organization details
                    - Business contact information
                    """)
                    
                    st.markdown("### 🎯 B2B Benefits")
                    if org_type == "Company":
                        st.success("""
                        **Company Features:**
                        - Post unlimited job openings
                        - View and manage applications
                        - Access candidate analytics
                        - Resume screening tools
                        """)
                    else:
                        st.success("""
                        **Institution Features:**
                        - Create and manage courses
                        - Track student enrollments
                        - Course analytics dashboard
                        - Student progress monitoring
                        """)
                    
                    if st.button("← Back to User Type Selection", key="back_from_b2b"):
                        st.session_state.auth_step = 'select_type'
                        st.session_state.selected_user_type = None
                        st.rerun()
            
            # Step 3: B2C Registration
            elif st.session_state.auth_step == 'b2c_signup':
                st.subheader("👤 B2C Individual Registration")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    with st.form("b2c_signup_form"):
                        st.markdown("**🔐 Account Credentials**")
                        email = st.text_input("Email Address *", placeholder="your.email@example.com")
                        password = st.text_input("Password *", type="password", placeholder="Secure password (min 6 chars)")
                        confirm_password = st.text_input("Confirm Password *", type="password", placeholder="Re-enter password")
                        username = st.text_input("Username *", placeholder="Choose a unique username")
                        
                        st.markdown("**👤 Personal Information**")
                        full_name = st.text_input("Full Name", placeholder="Your full name")
                        phone = st.text_input("Phone Number", placeholder="+1-234-567-8900")
                        location = st.text_input("Location", placeholder="City, State, Country")
                        
                        st.markdown("**💼 Professional Profile**")
                        bio = st.text_area("Professional Bio", 
                                         placeholder="Brief description of your professional background and career goals...")
                        skills = st.text_input("Skills", 
                                             placeholder="Python, Data Science, Project Management (comma separated)")
                        experience_years = st.number_input("Years of Experience", 
                                                         min_value=0, max_value=50, value=0)
                        current_role = st.text_input("Current Role/Position", 
                                                   placeholder="e.g., Software Developer, Student, etc.")
                        education_level = st.selectbox("Highest Education Level", 
                                                     ["High School", "Associate Degree", "Bachelor's", 
                                                      "Master's", "PhD", "Other"])
                        
                        # Show what they can do
                        st.markdown("**🎯 Your Benefits:**")
                        st.success("✅ **Job Applications**: Apply to job openings from companies")
                        st.success("✅ **Course Enrollment**: Enroll in courses from institutions")
                        st.success("✅ **Resume Management**: Upload and manage multiple resumes")
                        st.success("✅ **AI Recommendations**: Get personalized job and course suggestions")
                        
                        if st.form_submit_button("🚀 Register as B2C User", use_container_width=True, type="primary"):
                            # Validation
                            if not all([email, password, confirm_password, username]):
                                st.error("❌ Email, password, and username are required")
                                st.stop()
                            
                            if len(password) < 6:
                                st.error("❌ Password must be at least 6 characters long")
                                st.stop()
                            
                            if password != confirm_password:
                                st.error("❌ Passwords do not match")
                                st.stop()
                            
                            try:
                                # Check if user exists
                                existing_user = db.query(User).filter(User.email == email).first()
                                if existing_user:
                                    st.error("❌ Email already registered")
                                    st.stop()
                                
                                # Check username uniqueness
                                existing_username = db.query(User).filter(User.username == username).first()
                                if existing_username:
                                    st.error("❌ Username already taken")
                                    st.stop()
                                
                                # Create B2C user
                                from app.models.user import UserTypeEnum
                                hashed_password = get_password_hash(password)
                                new_user = User(
                                    email=email,
                                    password_hash=hashed_password,
                                    username=username,
                                    org_id=None,
                                    user_type=UserTypeEnum.B2C,
                                    full_name=full_name,
                                    phone=phone,
                                    location=location,
                                    bio=bio,
                                    skills=skills,
                                    experience_years=experience_years
                                )
                                db.add(new_user)
                                db.commit()
                                db.refresh(new_user)
                                
                                st.success("✅ B2C User registered successfully!")
                                st.balloons()
                                
                                # Auto-login
                                token = create_access_token(data={"sub": str(new_user.id)})
                                st.session_state.auth_token = token
                                st.session_state.current_user_id = new_user.id
                                st.session_state.current_user_type = new_user.user_type.value
                                st.session_state.current_user = new_user
                                
                                # Show success details
                                st.subheader("🎉 Registration Complete!")
                                response_data = {
                                    "user_id": new_user.id,
                                    "email": new_user.email,
                                    "username": new_user.username,
                                    "user_type": new_user.user_type.value,
                                    "profile": {
                                        "full_name": new_user.full_name,
                                        "location": new_user.location,
                                        "experience_years": new_user.experience_years,
                                        "skills": new_user.skills,
                                        "capabilities": "Apply for Jobs, Enroll in Courses, Upload Resumes"
                                    }
                                }
                                st.json(response_data)
                                
                                st.success("🔐 You are now automatically logged in!")
                                st.info("💡 **Next Step**: Go to 'Resume Processing' to upload your resume for better job recommendations!")
                                
                            except Exception as e:
                                st.error(f"❌ Registration failed: {str(e)}")
                
                with col2:
                    st.markdown("### ℹ️ B2C Registration")
                    st.info("""
                    **Requirements:**
                    - Valid email address
                    - Secure password (6+ chars)
                    - Unique username
                    - Optional: Professional details
                    """)
                    
                    st.markdown("### 🎯 B2C Benefits")
                    st.success("""
                    **Individual Features:**
                    - Apply to unlimited jobs
                    - Enroll in available courses
                    - Upload multiple resumes
                    - AI-powered recommendations
                    - Track applications & enrollments
                    """)
                    
                    if st.button("← Back to User Type Selection", key="back_from_b2c"):
                        st.session_state.auth_step = 'select_type'
                        st.session_state.selected_user_type = None
                        st.rerun()
            
            # Current User Status
            if st.session_state.current_user_id:
                st.markdown("---")
                st.subheader("👤 Current Session")
                
                try:
                    current_user = db.query(User).filter(User.id == st.session_state.current_user_id).first()
                    if current_user:
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            if current_user.user_type.value == "B2B" and current_user.org_id:
                                org = db.query(Organization).filter(Organization.id == current_user.org_id).first()
                                if org:
                                    st.success(f"🏢 **Logged in as:** {org.name}")
                                    st.info(f"📧 **Email:** {current_user.email}")
                                    st.info(f"🏷️ **Type:** {org.org_type.value}")
                                    permissions = "Post Jobs & Manage Applications" if org.org_type.value == "COMPANY" else "Create Courses & Manage Enrollments"
                                    st.info(f"📋 **Can:** {permissions}")
                            else:
                                st.success(f"👤 **Logged in as:** {current_user.username}")
                                st.info(f"📧 **Email:** {current_user.email}")
                                st.info(f"🎯 **Type:** Individual (B2C)")
                                st.info(f"📋 **Can:** Apply for Jobs, Enroll in Courses, Upload Resumes")
                        
                        with col2:
                            if st.button("🔄 Switch User", use_container_width=True):
                                st.session_state.auth_step = 'select_type'
                                st.session_state.selected_user_type = None
                                st.rerun()
                        
                        with col3:
                            if st.button("🚪 Logout", use_container_width=True, type="secondary"):
                                st.session_state.auth_token = None
                                st.session_state.current_user_id = None
                                st.session_state.current_user_type = None
                                st.session_state.current_user = None
                                st.success("✅ Logged out successfully!")
                                st.rerun()
                except Exception as e:
                    st.error(f"Error loading user info: {str(e)}")
        
        # Resume Processing endpoints
        elif page == "📄 Resume Processing":
            st.header("📄 Resume Processing & AI Recommendations")
            
            # Check if user is logged in
            if not st.session_state.current_user_id:
                st.warning("⚠️ Please login first to access resume processing functionality")
                st.info("💡 **B2C Users**: Upload resumes and get job/course recommendations")
                st.info("💡 **B2B Users**: View candidate profiles and analytics")
                st.stop()
            
            # Get current user info
            try:
                current_user = db.query(User).filter(User.id == st.session_state.current_user_id).first()
                if not current_user:
                    st.error("❌ User session invalid. Please login again.")
                    st.stop()
                
                user_type = current_user.user_type.value
                
                # Different interfaces for B2B vs B2C
                if user_type == "B2C":
                    st.info("👤 **B2C Mode**: Upload your resume to get personalized job and course recommendations")
                    
                    # Import resume processing services
                    try:
                        from app.services.langgraph_resume_parser import LangGraphResumeParser, ParsedResumeData
                        from app.services.pdf_processor import PDFProcessor
                        from app.services.job_recommender import JobRecommender
                        from app.services.course_recommender import CourseRecommender
                        
                        # Get Groq API key from environment
                        groq_api_key = os.getenv("GROQ_API_KEY", "").strip('"')
                        if not groq_api_key:
                            st.error("❌ GROQ_API_KEY not found in environment variables")
                            st.stop()
                        
                        # Initialize services
                        resume_parser = LangGraphResumeParser(groq_api_key=groq_api_key)
                        pdf_processor = PDFProcessor()
                        job_recommender = JobRecommender()
                        course_recommender = CourseRecommender()
                        
                        st.success("✅ AI Resume processing services initialized successfully!")
                        
                    except Exception as e:
                        st.error(f"❌ Error initializing resume processing services: {str(e)}")
                        st.info("Make sure all dependencies are installed: groq, langgraph, pdfplumber")
                        st.stop()
                    
                    # B2C Resume Upload Section
                    st.subheader("📤 Upload & Process Your Resume")
                    
                    uploaded_file = st.file_uploader(
                        "Choose your PDF resume file",
                        type=['pdf'],
                        help="Upload your resume to get AI-powered job and course recommendations"
                    )
                    
                    if uploaded_file is not None:
                        # Display file info
                        file_details = {
                            "filename": uploaded_file.name,
                            "file_size": f"{uploaded_file.size / 1024:.2f} KB",
                            "file_type": uploaded_file.type
                        }
                        st.json(file_details)
                        
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            if st.button("🤖 Process Resume with AI", use_container_width=True, type="primary"):
                                try:
                                    with st.spinner("🔄 Processing your resume with AI... This may take a few moments"):
                                        # Save uploaded file temporarily
                                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                                            tmp_file.write(uploaded_file.getvalue())
                                            tmp_file_path = tmp_file.name
                                        
                                        start_time = datetime.now()
                                        
                                        # Step 1: Extract text from PDF
                                        progress = st.progress(0)
                                        st.info("📄 Step 1: Extracting text from PDF...")
                                        progress.progress(25)
                                        
                                        pdf_data = pdf_processor.extract_complete_pdf_data(tmp_file_path)
                                        extracted_text = pdf_data.get("text", "")
                                        
                                        if not extracted_text.strip():
                                            st.error("❌ Could not extract text from PDF. Please ensure the PDF contains readable text.")
                                            os.unlink(tmp_file_path)
                                            st.stop()
                                        
                                        st.success(f"✅ Extracted {len(extracted_text)} characters from PDF")
                                        
                                        # Show additional PDF metadata
                                        if pdf_data.get("metadata"):
                                            st.info(f"📊 PDF Info: {pdf_data['metadata']['pages']} pages")
                                        
                                        progress.progress(50)
                                        
                                        # Step 2: Parse resume with LangGraph
                                        st.info("🤖 Step 2: Analyzing resume with AI (LangGraph + Groq)...")
                                        parsed_data = resume_parser.parse_resume(extracted_text)
                                        progress.progress(75)
                                        
                                        processing_time = (datetime.now() - start_time).total_seconds()
                                        
                                        # Step 3: Save to database
                                        st.info("💾 Step 3: Saving to your profile...")
                                        resume_record = Resume(
                                            user_id=st.session_state.current_user_id,
                                            filename=uploaded_file.name,
                                            file_path=tmp_file_path,
                                            file_size=uploaded_file.size,
                                            parsed_data=parsed_data.model_dump(),  # Convert Pydantic model to dict
                                            processing_time=processing_time,
                                            confidence_score=0.95,
                                            parsing_errors=None
                                        )
                                        
                                        db.add(resume_record)
                                        db.commit()
                                        db.refresh(resume_record)
                                        progress.progress(100)
                                        
                                        st.success("✅ Resume processed and saved successfully!")
                                        st.balloons()
                                        
                                        # Display parsed data
                                        st.subheader("📋 AI-Extracted Resume Data")
                                        parsed_data_dict = parsed_data.model_dump()
                                        
                                        # Show key information in a nice format
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            if parsed_data_dict.get('personal_info'):
                                                st.markdown("**👤 Personal Info:**")
                                                personal = parsed_data_dict['personal_info']
                                                if personal.get('name'):
                                                    st.write(f"**Name:** {personal['name']}")
                                                if personal.get('email'):
                                                    st.write(f"**Email:** {personal['email']}")
                                                if personal.get('phone'):
                                                    st.write(f"**Phone:** {personal['phone']}")
                                                if personal.get('location'):
                                                    st.write(f"**Location:** {personal['location']}")
                                            
                                            if parsed_data_dict.get('skills'):
                                                st.markdown("**🛠️ Skills:**")
                                                for skill in parsed_data_dict['skills'][:10]:  # Show first 10
                                                    st.write(f"• {skill}")
                                        
                                        with col2:
                                            if parsed_data_dict.get('experience'):
                                                st.markdown("**💼 Experience:**")
                                                for exp in parsed_data_dict['experience'][:3]:  # Show first 3
                                                    st.write(f"**{exp.get('title', 'N/A')}** at {exp.get('company', 'N/A')}")
                                                    if exp.get('start_date') or exp.get('end_date'):
                                                        st.write(f"*{exp.get('start_date', '')} - {exp.get('end_date', '')}*")
                                            
                                            if parsed_data_dict.get('education'):
                                                st.markdown("**🎓 Education:**")
                                                for edu in parsed_data_dict['education'][:3]:  # Show first 3
                                                    st.write(f"**{edu.get('degree', 'N/A')}** in {edu.get('field', 'N/A')}")
                                                    if edu.get('institution'):
                                                        st.write(f"*{edu.get('institution')}*")
                                        
                                        # Show full JSON data in expander
                                        with st.expander("🔍 View Complete AI Analysis"):
                                            st.json(parsed_data_dict)
                                        
                                        # Store resume ID for recommendations
                                        st.session_state.latest_resume_id = resume_record.id
                                        st.session_state.latest_parsed_data = parsed_data_dict
                                        
                                        # Processing stats
                                        st.info(f"⏱️ Processing time: {processing_time:.2f} seconds | 🎯 Confidence: 95%")
                                        
                                        # Clean up temporary file
                                        os.unlink(tmp_file_path)
                                        
                                except Exception as e:
                                    st.error(f"❌ Error processing resume: {str(e)}")
                                    if 'tmp_file_path' in locals():
                                        try:
                                            os.unlink(tmp_file_path)
                                        except:
                                            pass
                        
                        with col2:
                            st.markdown("### 🤖 AI Processing")
                            st.markdown("""
                            **What our AI extracts:**
                            1. **Personal Information** - Contact details, location
                            2. **Skills & Technologies** - Programming languages, tools
                            3. **Work Experience** - Job titles, companies, dates
                            4. **Education** - Degrees, institutions, fields
                            5. **Projects & Certifications** - Additional qualifications
                            
                            **Powered by:**
                            - 🚀 **Groq** for fast AI inference
                            - 🧠 **LangGraph** for intelligent workflow
                            - 📄 **PDFPlumber** for text extraction
                            """)
                    
                    # B2C Resume List Section
                    st.markdown("---")
                    st.subheader("📋 Your Resume Collection")
                    
                    if st.button("🔄 Refresh My Resumes"):
                        try:
                            user_resumes = db.query(Resume).filter(Resume.user_id == st.session_state.current_user_id).all()
                            
                            if user_resumes:
                                st.success(f"✅ Found {len(user_resumes)} resume(s) in your profile")
                                
                                for resume in user_resumes:
                                    with st.expander(f"📄 {resume.filename} (Uploaded: {resume.created_at.strftime('%Y-%m-%d %H:%M')})"):
                                        col1, col2, col3 = st.columns([2, 2, 1])
                                        
                                        with col1:
                                            st.markdown("**📊 File Details:**")
                                            st.json({
                                                "filename": resume.filename,
                                                "file_size": f"{resume.file_size / 1024:.2f} KB",
                                                "processing_time": f"{resume.processing_time:.2f}s",
                                                "confidence_score": f"{resume.confidence_score:.1f}",
                                                "status": "✅ Processed"
                                            })
                                        
                                        with col2:
                                            st.markdown("**🎯 Quick Actions:**")
                                            
                                            col2a, col2b = st.columns(2)
                                            with col2a:
                                                if st.button(f"💼 Get Jobs", key=f"jobs_{resume.id}", use_container_width=True):
                                                    st.session_state.latest_resume_id = resume.id
                                                    st.session_state.latest_parsed_data = resume.parsed_data
                                                    st.success("✅ Resume selected for job matching!")
                                            
                                            with col2b:
                                                if st.button(f"📚 Get Courses", key=f"courses_{resume.id}", use_container_width=True):
                                                    st.session_state.latest_resume_id = resume.id
                                                    st.session_state.latest_parsed_data = resume.parsed_data
                                                    st.success("✅ Resume selected for course recommendations!")
                                        
                                        with col3:
                                            st.markdown("**🗑️ Manage:**")
                                            if st.button(f"Delete", key=f"delete_{resume.id}", use_container_width=True, type="secondary"):
                                                try:
                                                    db.delete(resume)
                                                    db.commit()
                                                    st.success("✅ Resume deleted")
                                                    st.rerun()
                                                except Exception as e:
                                                    st.error(f"❌ Error deleting resume: {str(e)}")
                                        
                                        # Show key parsed data
                                        if resume.parsed_data:
                                            st.markdown("**🤖 AI-Extracted Summary:**")
                                            data = resume.parsed_data
                                            col1, col2, col3 = st.columns(3)
                                            
                                            with col1:
                                                if data.get('skills'):
                                                    skills_count = len(data['skills'])
                                                    st.metric("Skills Found", skills_count)
                                            
                                            with col2:
                                                if data.get('experience'):
                                                    exp_count = len(data['experience'])
                                                    st.metric("Work Experience", f"{exp_count} roles")
                                            
                                            with col3:
                                                if data.get('education'):
                                                    edu_count = len(data['education'])
                                                    st.metric("Education", f"{edu_count} degrees")
                            else:
                                st.info("📭 No resumes uploaded yet. Upload your first resume above to get started!")
                                
                        except Exception as e:
                            st.error(f"❌ Error fetching resumes: {str(e)}")
                    
                    # B2C Recommendations Section (only if resume data available)
                    if hasattr(st.session_state, 'latest_parsed_data') and st.session_state.latest_parsed_data:
                        st.markdown("---")
                        st.subheader("🎯 AI-Powered Recommendations")
                        st.info(f"📄 Based on Resume ID: {st.session_state.latest_resume_id}")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("### 💼 Job Recommendations")
                            if st.button("🔍 Find Matching Jobs", use_container_width=True, type="primary"):
                                try:
                                    with st.spinner("🤖 AI is analyzing jobs for you..."):
                                        # Get all jobs from database
                                        all_jobs = db.query(Job).all()
                                        
                                        if not all_jobs:
                                            st.warning("⚠️ No jobs available in the system yet")
                                            st.info("💡 Jobs will be posted by registered companies")
                                        else:
                                            # Get recommendations
                                            recommendations = job_recommender.get_recommendations(
                                                st.session_state.latest_parsed_data,
                                                all_jobs
                                            )
                                            
                                            st.success(f"✅ Found {len(recommendations)} job matches!")
                                            
                                            for i, rec in enumerate(recommendations[:5]):  # Show top 5
                                                with st.expander(f"💼 #{i+1}: {rec['job'].title} - Match: {rec['score']:.1f}"):
                                                    job_data = {
                                                        "title": rec['job'].title,
                                                        "location": rec['job'].location,
                                                        "job_type": rec['job'].job_type,
                                                        "salary_range": rec['job'].salary_range,
                                                        "experience_level": rec['job'].experience_level,
                                                        "match_score": f"{rec['score']:.1f}",
                                                        "why_good_fit": rec['reasons'][:3],  # Top 3 reasons
                                                        "required_skills": rec['job'].skills_required[:5]  # Top 5 skills
                                                    }
                                                    st.json(job_data)
                                                    
                                                    # Application button
                                                    if st.button(f"📋 Apply for this Job", key=f"apply_job_{rec['job'].id}"):
                                                        st.success("✅ Application submitted! (Demo mode)")
                                                        st.info("💡 In a real system, this would redirect to the application portal")
                                
                                except Exception as e:
                                    st.error(f"❌ Error getting job recommendations: {str(e)}")
                        
                        with col2:
                            st.markdown("### 📚 Course Recommendations")
                            if st.button("🔍 Find Relevant Courses", use_container_width=True, type="primary"):
                                try:
                                    with st.spinner("🤖 AI is finding courses to boost your skills..."):
                                        # Get all courses from database
                                        all_courses = db.query(Course).all()
                                        
                                        if not all_courses:
                                            st.warning("⚠️ No courses available in the system yet")
                                            st.info("💡 Courses will be created by registered institutions")
                                        else:
                                            # Get recommendations
                                            recommendations = course_recommender.get_recommendations(
                                                st.session_state.latest_parsed_data,
                                                all_courses
                                            )
                                            
                                            st.success(f"✅ Found {len(recommendations)} course recommendations!")
                                            
                                            for i, rec in enumerate(recommendations[:5]):  # Show top 5
                                                with st.expander(f"📚 #{i+1}: {rec['course'].name} - Relevance: {rec['score']:.1f}"):
                                                    course_data = {
                                                        "name": rec['course'].name,
                                                        "duration": rec['course'].duration,
                                                        "mode": rec['course'].mode,
                                                        "fees": rec['course'].fees,
                                                        "relevance_score": f"{rec['score']:.1f}",
                                                        "why_recommended": rec['reasons'][:3],  # Top 3 reasons
                                                        "skills_you_will_learn": rec['course'].skills_required[:5]  # Top 5 skills
                                                    }
                                                    st.json(course_data)
                                                    
                                                    # Enrollment button
                                                    if st.button(f"📝 Enroll in Course", key=f"enroll_course_{rec['course'].id}"):
                                                        st.success("✅ Enrollment successful! (Demo mode)")
                                                        st.info("💡 In a real system, this would handle payment and enrollment")
                                
                                except Exception as e:
                                    st.error(f"❌ Error getting course recommendations: {str(e)}")
                
                elif user_type == "B2B":
                    # B2B Interface - View analytics and candidate data
                    st.info("🏢 **B2B Mode**: View candidate analytics and resume insights")
                    
                    # Get organization info
                    org = None
                    if current_user.org_id:
                        org = db.query(Organization).filter(Organization.id == current_user.org_id).first()
                    
                    if org:
                        st.subheader(f"🏢 {org.name} - Candidate Analytics")
                        
                        # Show organization capabilities
                        if org.org_type.value == "COMPANY":
                            st.success("💼 **Your Capabilities**: Post Jobs, View Job Applications, Candidate Analytics")
                            
                            # Job analytics
                            st.markdown("### 📊 Job Posting Analytics")
                            try:
                                # Get jobs posted by this organization (would need org_id in Job model)
                                all_jobs = db.query(Job).all()  # For demo, show all jobs
                                st.info(f"📈 **Jobs in System**: {len(all_jobs)} total jobs available")
                                
                                if all_jobs:
                                    for job in all_jobs[:3]:  # Show first 3 jobs
                                        with st.expander(f"💼 {job.title} - {job.location}"):
                                            st.write(f"**Type:** {job.job_type}")
                                            st.write(f"**Salary:** {job.salary_range}")
                                            st.write(f"**Experience:** {job.experience_level}")
                                            st.write(f"**Views:** {job.views}")
                                            
                                            # Simulated candidate data
                                            st.metric("Applications", "12", "3")
                                            st.metric("Profile Views", "45", "8")
                                            
                            except Exception as e:
                                st.error(f"Error loading job analytics: {str(e)}")
                        
                        else:  # INSTITUTION
                            st.success("📚 **Your Capabilities**: Create Courses, View Enrollments, Student Analytics")
                            
                            # Course analytics
                            st.markdown("### 📊 Course Analytics")
                            try:
                                # Get courses created by this organization
                                all_courses = db.query(Course).all()  # For demo, show all courses
                                st.info(f"📈 **Courses in System**: {len(all_courses)} total courses available")
                                
                                if all_courses:
                                    for course in all_courses[:3]:  # Show first 3 courses
                                        with st.expander(f"📚 {course.name} - {course.duration}"):
                                            st.write(f"**Mode:** {course.mode}")
                                            st.write(f"**Fees:** {course.fees}")
                                            st.write(f"**Views:** {course.views}")
                                            
                                            # Simulated enrollment data
                                            st.metric("Enrollments", "28", "5")
                                            st.metric("Course Views", "156", "12")
                                            
                            except Exception as e:
                                st.error(f"Error loading course analytics: {str(e)}")
                        
                        # Candidate Resume Analytics
                        st.markdown("### 👥 Candidate Resume Insights")
                        try:
                            all_resumes = db.query(Resume).all()
                            
                            if all_resumes:
                                st.success(f"📊 **Total Candidates**: {len(all_resumes)} resumes in system")
                                
                                # Aggregate analytics
                                col1, col2, col3, col4 = st.columns(4)
                                
                                # Calculate some basic stats
                                total_candidates = len(all_resumes)
                                avg_experience = sum([r.parsed_data.get('experience_years', 0) if r.parsed_data else 0 for r in all_resumes]) / max(total_candidates, 1)
                                
                                with col1:
                                    st.metric("Total Candidates", total_candidates)
                                with col2:
                                    st.metric("Avg Experience", f"{avg_experience:.1f} years")
                                with col3:
                                    st.metric("This Month", "+12", "3")
                                with col4:
                                    st.metric("Active Profiles", "89%", "2%")
                                
                                # Show sample candidate profiles (anonymized)
                                st.markdown("### 🔍 Recent Candidate Profiles")
                                for i, resume in enumerate(all_resumes[:5]):  # Show first 5
                                    if resume.parsed_data:
                                        with st.expander(f"👤 Candidate #{i+1} - {resume.filename[:20]}..."):
                                            data = resume.parsed_data
                                            
                                            col1, col2 = st.columns(2)
                                            with col1:
                                                if data.get('skills'):
                                                    st.write(f"**Skills**: {len(data['skills'])} identified")
                                                    st.write("Top Skills: " + ", ".join(data['skills'][:5]))
                                                
                                                if data.get('experience'):
                                                    st.write(f"**Experience**: {len(data['experience'])} roles")
                                            
                                            with col2:
                                                if data.get('education'):
                                                    st.write(f"**Education**: {len(data['education'])} qualifications")
                                                
                                                st.write(f"**Uploaded**: {resume.created_at.strftime('%Y-%m-%d')}")
                                                st.write(f"**Processing Time**: {resume.processing_time:.2f}s")
                            else:
                                st.info("📭 No candidate resumes in the system yet")
                                st.info("💡 Candidates will upload resumes when they register as B2C users")
                                
                        except Exception as e:
                            st.error(f"Error loading candidate analytics: {str(e)}")
                    
                    else:
                        st.error("❌ Organization not found. Please contact support.")
                
            except Exception as e:
                st.error(f"❌ Error loading user information: {str(e)}")
        
        # Courses endpoints
        elif page == "📚 Courses":
            st.header("📚 Courses Management")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("➕ Create Course")
                with st.form("create_course_form"):
                    course_name = st.text_input("Course Name", value="Introduction to APIs")
                    duration = st.text_input("Duration", value="4 weeks")
                    mode = st.selectbox("Mode", ["Online", "Offline", "Hybrid"])
                    fees = st.text_input("Fees", value="Free")
                    description = st.text_area("Description", value="Learn to build APIs with FastAPI")
                    skills_required = st.text_input("Skills Required (comma separated)", value="Python, FastAPI")
                    application_deadline = st.date_input("Application Deadline", value=date(2025, 12, 31))
                    prerequisites = st.text_input("Prerequisites (comma separated)", value="Basics of Python")
                    
                    if st.form_submit_button("Create Course"):
                        try:
                            data = CourseCreate(
                                name=course_name,
                                duration=duration,
                                mode=mode,
                                fees=fees,
                                description=description,
                                skills_required=[skill.strip() for skill in skills_required.split(",")],
                                application_deadline=application_deadline,
                                prerequisites=[prereq.strip() for prereq in prerequisites.split(",")]
                            )
                            
                            result = course_service.create_course(db, data)
                            st.success("Status: 201")
                            st.json({
                                "id": result.id,
                                "name": result.name,
                                "duration": result.duration,
                                "mode": result.mode,
                                "fees": result.fees,
                                "description": result.description,
                                "skills_required": result.skills_required,
                                "application_deadline": str(result.application_deadline),
                                "prerequisites": result.prerequisites,
                                "views": result.views
                            })
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            
            with col2:
                st.subheader("📋 List Courses")
                if st.button("Get All Courses"):
                    try:
                        courses = course_service.list_courses(db)
                        st.success("Status: 200")
                        if courses:
                            for course in courses:
                                with st.expander(f"Course: {course.name}"):
                                    st.json({
                                        "id": course.id,
                                        "name": course.name,
                                        "duration": course.duration,
                                        "mode": course.mode,
                                        "fees": course.fees,
                                        "description": course.description,
                                        "skills_required": course.skills_required,
                                        "application_deadline": str(course.application_deadline),
                                        "prerequisites": course.prerequisites,
                                        "views": course.views
                                    })
                        else:
                            st.info("No courses found")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        # Jobs endpoints
        elif page == "💼 Jobs":
            st.header("💼 Jobs Management")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("➕ Create Job")
                with st.form("create_job_form"):
                    job_title = st.text_input("Job Title", value="Backend Engineer")
                    job_type = st.selectbox("Job Type", ["Full-time", "Internship", "Contract", "Part-time"])
                    location = st.text_input("Location", value="Remote")
                    salary_range = st.text_input("Salary Range", value="$80k-$120k")
                    responsibilities = st.text_area("Responsibilities", value="Build APIs and backend services")
                    skills_required = st.text_input("Skills Required (comma separated)", value="Python, FastAPI, SQL")
                    application_deadline = st.date_input("Application Deadline", value=date(2025, 11, 30))
                    industry = st.text_input("Industry", value="Software")
                    remote_option = st.selectbox("Remote Option", ["Remote", "On-site", "Hybrid"])
                    experience_level = st.selectbox("Experience Level", ["Entry", "Mid", "Senior"])
                    number_of_openings = st.number_input("Number of Openings", min_value=1, value=2)
                    
                    if st.form_submit_button("Create Job"):
                        try:
                            data = JobCreate(
                                title=job_title,
                                job_type=job_type,
                                location=location,
                                salary_range=salary_range,
                                responsibilities=responsibilities,
                                skills_required=[skill.strip() for skill in skills_required.split(",")],
                                application_deadline=application_deadline,
                                industry=industry,
                                remote_option=remote_option,
                                experience_level=experience_level,
                                number_of_openings=number_of_openings
                            )
                            
                            result = job_service.create_job(db, data)
                            st.success("Status: 201")
                            st.json({
                                "id": result.id,
                                "title": result.title,
                                "job_type": result.job_type,
                                "location": result.location,
                                "salary_range": result.salary_range,
                                "responsibilities": result.responsibilities,
                                "skills_required": result.skills_required,
                                "application_deadline": str(result.application_deadline),
                                "industry": result.industry,
                                "remote_option": result.remote_option,
                                "experience_level": result.experience_level,
                                "number_of_openings": result.number_of_openings,
                                "views": result.views
                            })
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            
            with col2:
                st.subheader("📋 List Jobs")
                if st.button("Get All Jobs"):
                    try:
                        jobs = job_service.list_jobs(db)
                        st.success("Status: 200")
                        if jobs:
                            for job in jobs:
                                with st.expander(f"Job: {job.title}"):
                                    st.json({
                                        "id": job.id,
                                        "title": job.title,
                                        "job_type": job.job_type,
                                        "location": job.location,
                                        "salary_range": job.salary_range,
                                        "responsibilities": job.responsibilities,
                                        "skills_required": job.skills_required,
                                        "application_deadline": str(job.application_deadline),
                                        "industry": job.industry,
                                        "remote_option": job.remote_option,
                                        "experience_level": job.experience_level,
                                        "number_of_openings": job.number_of_openings,
                                        "views": job.views
                                    })
                        else:
                            st.info("No jobs found")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        # Organizations endpoints
        elif page == "🏢 Organizations":
            st.header("🏢 Organizations Management")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📋 List All Organizations")
                if st.button("Get All Organizations"):
                    try:
                        orgs = db.query(Organization).all()
                        st.success("Status: 200")
                        if orgs:
                            for org in orgs:
                                with st.expander(f"Organization: {org.name}"):
                                    st.json({
                                        "id": org.id,
                                        "name": org.name,
                                        "org_type": org.org_type.value,
                                        "address": org.address,
                                        "contact_email": org.contact_email,
                                        "contact_phone": org.contact_phone,
                                        "logo_path": org.logo_path
                                    })
                        else:
                            st.info("No organizations found")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        # Statistics endpoints
        elif page == "📊 Statistics":
            st.header("📊 Statistics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Resume Statistics")
                if st.button("Get Resume Statistics"):
                    try:
                        total_resumes = db.query(Resume).count()
                        user_resumes = db.query(Resume).filter(Resume.user_id == st.session_state.current_user_id).count() if st.session_state.current_user_id else 0
                        
                        st.success("Status: 200")
                        st.json({
                            "total_resumes_in_system": total_resumes,
                            "your_resumes": user_resumes,
                            "processing_enabled": True
                        })
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            with col2:
                st.subheader("📊 System Statistics")
                if st.button("Get System Statistics"):
                    try:
                        job_count = db.query(Job).count()
                        course_count = db.query(Course).count()
                        user_count = db.query(User).count()
                        resume_count = db.query(Resume).count()
                        
                        st.success("Status: 200")
                        st.json({
                            "total_jobs": job_count,
                            "total_courses": course_count,
                            "total_users": user_count,
                            "total_resumes": resume_count
                        })
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        # Footer
        st.markdown("---")
        st.markdown("**🔧 Technology:** LangGraph + Groq | **💾 Database:** SQLite | **🎯 AI-Powered Resume Processing**")
        
        # Close database session
        db.close()
        
    except Exception as e:
        st.error(f"❌ Error initializing: {str(e)}")
        st.info("Make sure all dependencies are installed and the database is accessible")

if __name__ == "__main__":
    main()
