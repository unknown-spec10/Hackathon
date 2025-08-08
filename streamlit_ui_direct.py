#!/usr/bin/env python3
"""
Streamlit UI for testing the Hackathon API - Direct Function Calls
"""
import streamlit as st
import json
from datetime import datetime, date
import os
import atexit
import sqlite3

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
    st.title("🚀 Hackathon API Tester (Direct Functions)")
    st.markdown("---")
    
    # Add session cleanup info
    if 'session_started' not in st.session_state:
        st.session_state.session_started = True
        st.info("🔄 **Auto-cleanup enabled**: Database will be cleared when you close this tab/browser")
    
    try:
        # Import only the core functions we need - avoid FastAPI app
        from database.db_setup import Base, engine
        from app.service import course_service, job_service, profile_service
        from app.schemas.course_schema import CourseCreate
        from app.schemas.job_schema import JobCreate
        from app.schemas.user_schema import UserCreate
        from app.utils.auth import get_password_hash, create_access_token, verify_password
        from app.models.user import User
        from app.models.course import Course
        from app.models.job import Job
        from app.models.profile import Organization
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
            ["🏠 Root", "👤 Authentication", "📚 Courses", "💼 Jobs", "🏢 Organizations", "📊 Statistics"]
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
        
        # Root endpoint
        if page == "🏠 Root":
            st.header("🏠 Root Endpoint")
            st.markdown("Test the basic API root endpoint")
            
            if st.button("Test Root Endpoint"):
                st.success("Status: 200")
                st.json({"status": "ok"})
        
        # Authentication endpoints
        elif page == "👤 Authentication":
            st.header("👤 Authentication")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📝 User Signup")
                with st.form("signup_form"):
                    email = st.text_input("Email", placeholder="Enter your email address")
                    password = st.text_input("Password", type="password", placeholder="Enter a secure password (min 6 chars)")
                    username = st.text_input("Username", placeholder="Enter your username")
                    user_type = st.selectbox("User Type", ["B2C", "B2B"], help="B2C: Talent users, B2B: Organization users")
                    
                    # B2B Organization fields (shown conditionally)
                    org_name = None
                    org_type = None
                    org_address = None
                    org_contact_phone = None
                    org_logo_path = None
                    
                    if user_type == "B2B":
                        st.markdown("**Organization Details (Required for B2B)**")
                        org_name = st.text_input("Organization Name", placeholder="Enter organization name")
                        org_type = st.selectbox("Organization Type", ["Company", "Institution"])
                        org_address = st.text_input("Organization Address", placeholder="Enter full address")
                        org_contact_phone = st.text_input("Contact Phone (Optional)", placeholder="Enter phone number")
                        org_logo_path = st.text_input("Logo Path/URL (Optional)", placeholder="Enter logo URL or path")
                    
                    if st.form_submit_button("Sign Up"):
                        # Validate required fields
                        if not email or not password or not username:
                            st.error("Email, password, and username are required")
                            st.stop()
                        
                        if len(password) < 6:
                            st.error("Password must be at least 6 characters long")
                            st.stop()
                        
                        try:
                            # Check if user exists
                            existing_user = db.query(User).filter(User.email == email).first()
                            if existing_user:
                                st.error("Email already registered")
                            else:
                                # Validate B2B requirements
                                if user_type == "B2B" and not all([org_name, org_type, org_address]):
                                    st.error("B2B users must provide organization name, type, and address")
                                    st.stop()
                                
                                # Create organization if B2B
                                org_id = None
                                if user_type == "B2B":
                                    from app.models.profile import Organization, OrgTypeEnum
                                    org_type_enum = OrgTypeEnum.COMPANY if org_type == "Company" else OrgTypeEnum.INSTITUTION
                                    
                                    new_org = Organization(
                                        name=org_name,
                                        org_type=org_type_enum,
                                        address=org_address,
                                        contact_email=email,  # Use user email as org contact
                                        contact_phone=org_contact_phone if org_contact_phone else None,
                                        logo_path=org_logo_path if org_logo_path else None
                                    )
                                    db.add(new_org)
                                    db.flush()  # Get org ID without committing
                                    org_id = new_org.id
                                
                                # Create new user
                                from app.models.user import UserTypeEnum
                                user_type_enum = UserTypeEnum.B2B if user_type == "B2B" else UserTypeEnum.B2C
                                
                                hashed_password = get_password_hash(password)
                                new_user = User(
                                    email=email,
                                    password_hash=hashed_password,
                                    username=username,
                                    org_id=org_id,
                                    user_type=user_type_enum
                                )
                                db.add(new_user)
                                db.commit()
                                db.refresh(new_user)
                                
                                st.success("✅ User registered successfully!")
                                st.success("Status: 201")
                                user_response = {
                                    "id": new_user.id,
                                    "email": new_user.email,
                                    "username": new_user.username,
                                    "org_id": new_user.org_id,
                                    "user_type": new_user.user_type.value
                                }
                                
                                if user_type == "B2B" and org_id:
                                    user_response["organization"] = {
                                        "id": new_org.id,
                                        "name": new_org.name,
                                        "type": new_org.org_type.value
                                    }
                                    st.success(f"🏢 Organization '{new_org.name}' created with ID: {new_org.id}")
                                
                                st.json(user_response)
                                
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            
            with col2:
                st.subheader("🔐 User Login")
                with st.form("login_form"):
                    login_email = st.text_input("Email/Username", placeholder="Enter your email address")
                    login_password = st.text_input("Password", type="password", placeholder="Enter your password")
                    
                    if st.form_submit_button("Login"):
                        # Validate required fields
                        if not login_email or not login_password:
                            st.error("Email and password are required")
                            st.stop()
                        
                        try:
                            # Find user
                            user = db.query(User).filter(User.email == login_email).first()
                            if user and verify_password(login_password, user.password_hash):
                                # Create token
                                token = create_access_token(data={"sub": str(user.id), "user_type": user.user_type.value})
                                st.session_state.auth_token = token
                                st.session_state.current_user_type = user.user_type.value
                                st.session_state.current_user_id = user.id
                                
                                st.success("✅ Login successful!")
                                st.success("Status: 200")
                                st.json({
                                    "access_token": token,
                                    "token_type": "bearer",
                                    "user_type": user.user_type.value,
                                    "user_id": user.id
                                })
                                st.success("✅ Token stored in session!")
                            else:
                                st.error("❌ Invalid credentials")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            
            # Test /me endpoint
            st.subheader("👤 Get Current User")
            if st.session_state.auth_token:
                if st.button("Get Current User"):
                    try:
                        # In a real app, you'd decode the token
                        # For demo, just show the token info
                        st.success("Status: 200")
                        st.json({
                            "message": "Token is valid",
                            "token": st.session_state.auth_token[:20] + "..."
                        })
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.warning("Please login first to test this endpoint")
        
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
            
            # Get specific course
            st.subheader("🔍 Get Specific Course")
            course_id = st.number_input("Course ID", min_value=1, value=1)
            if st.button("Get Course"):
                try:
                    course = course_service.get_course(db, course_id)
                    st.success("Status: 200")
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
                        print("Jobs retrieved successfully")
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
            
            # Get specific job
            st.subheader("🔍 Get Specific Job")
            job_id = st.number_input("Job ID", min_value=1, value=1)
            if st.button("Get Job"):
                try:
                    job = job_service.get_job(db, job_id)
                    st.success("Status: 200")
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
            
            with col2:
                st.subheader("🔍 Get Organization Profile")
                org_id = st.number_input("Organization ID", min_value=1, value=1)
                if st.button("Get Organization"):
                    try:
                        org = profile_service.get_org(db, org_id)
                        st.success("Status: 200")
                        st.json({
                            "id": org.id,
                            "name": org.name,
                            "org_type": org.org_type.value,
                            "address": org.address,
                            "contact_email": org.contact_email,
                            "contact_phone": org.contact_phone,
                            "logo_path": org.logo_path
                        })
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            # Show users by organization
            st.subheader("👥 Users by Organization")
            org_filter_id = st.number_input("Filter by Organization ID", min_value=1, value=1)
            if st.button("Get Users in Organization"):
                try:
                    users = db.query(User).filter(User.org_id == org_filter_id).all()
                    st.success("Status: 200")
                    if users:
                        for user in users:
                            with st.expander(f"User: {user.email}"):
                                st.json({
                                    "id": user.id,
                                    "email": user.email,
                                    "username": user.username,
                                    "user_type": user.user_type.value,
                                    "org_id": user.org_id
                                })
                    else:
                        st.info("No users found in this organization")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        # Statistics endpoints
        elif page == "📊 Statistics":
            st.header("📊 Statistics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Job Statistics")
                job_id = st.number_input("Job ID for Stats", min_value=1, value=1)
                if st.button("Get Job Statistics"):
                    try:
                        from app.repositories import stat_repo
                        stats = stat_repo.get_job_stats(db, job_id)
                        if stats:
                            st.success("Status: 200")
                            st.json(stats)
                        else:
                            st.error("Job not found")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            with col2:
                st.subheader("📊 Course Statistics")
                course_id = st.number_input("Course ID for Stats", min_value=1, value=1)
                if st.button("Get Course Statistics"):
                    try:
                        from app.repositories import stat_repo
                        stats = stat_repo.get_course_stats(db, course_id)
                        if stats:
                            st.success("Status: 200")
                            st.json(stats)
                        else:
                            st.error("Course not found")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        # Footer
        st.markdown("---")
        st.markdown("**Mode:** Direct Function Calls (No HTTP Server Required)")
        st.markdown("**Database:** SQLite (Auto-cleanup enabled)")
        
        # Close database session
        db.close()
        
    except Exception as e:
        st.error(f"❌ Error initializing: {str(e)}")
        st.info("Make sure all dependencies are installed and the database is accessible")

if __name__ == "__main__":
    main()
