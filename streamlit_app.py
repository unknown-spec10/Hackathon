import streamlit as st
import requests
from typing import List, Dict, Any, Optional
from datetime import date
import re
from datetime import datetime as dt

API_BASE_URL = "http://localhost:8000"

def _auth_headers() -> Dict[str, str]:
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def _api_get(path: str, auth: bool = False, params: Optional[Dict[str, Any]] = None):
    url = f"{API_BASE_URL}{path}"
    headers = _auth_headers() if auth else {}
    resp = requests.get(url, headers=headers, params=params, timeout=20)
    resp.raise_for_status()
    return resp.json()


def _api_post(path: str, json: Optional[Dict[str, Any]] = None, files: Optional[Dict[str, Any]] = None, auth: bool = False, params: Optional[Dict[str, Any]] = None):
    url = f"{API_BASE_URL}{path}"
    headers = _auth_headers() if auth else {}
    resp = requests.post(url, headers=headers, json=json, files=files, params=params, timeout=60)
    resp.raise_for_status()
    return resp.json()


def _api_put(path: str, json: Dict[str, Any], auth: bool = False):
    url = f"{API_BASE_URL}{path}"
    headers = _auth_headers() if auth else {}
    resp = requests.put(url, headers=headers, json=json, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _api_delete(path: str, auth: bool = False):
    url = f"{API_BASE_URL}{path}"
    headers = _auth_headers() if auth else {}
    resp = requests.delete(url, headers=headers, timeout=20)
    resp.raise_for_status()
    return resp.json() if resp.content else {"message": "deleted"}


def _load_user_context(force: bool = False):
    """Load /auth/me and optional org profile (org_type) into session state."""
    if not st.session_state.get("token"):
        return
    if not force and st.session_state.get("me"):
        return
    try:
        me = _api_get("/auth/me", auth=True)
        st.session_state["me"] = me
        st.session_state["user_type"] = me.get("user_type")
        st.session_state["org_id"] = me.get("org_id")
        # Load org profile to know if Company vs Institution
        if me.get("user_type") == "B2B" and me.get("org_id"):
            try:
                prof = _api_get(f"/profile/{int(me['org_id'])}")
                st.session_state["org_type"] = prof.get("org_type")
            except Exception:
                st.session_state["org_type"] = None
    except Exception:
        pass


def _comma_list(value: str) -> List[str]:
    return [s.strip() for s in value.split(",") if s.strip()] if value else []


def _iso(d: date) -> str:
    return d.isoformat() if isinstance(d, date) else str(d)


def _parse_date_guess(s: str) -> Optional[dt]:
    """Parse common date strings like MM/YYYY, Mon YYYY, or YYYY; return datetime or None."""
    if not s:
        return None
    s = str(s).strip()
    if not s or s.lower() == "present":
        return None
    # MM/YYYY or M/YYYY
    m = re.match(r"^(\d{1,2})[\-/](\d{4})$", s)
    if m:
        month = int(m.group(1)); year = int(m.group(2))
        month = 1 if month < 1 or month > 12 else month
        return dt(year, month, 1)
    # Mon YYYY
    m = re.match(r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})$", s, re.IGNORECASE)
    if m:
        mon_map = {m: i for i, m in enumerate(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"], start=1)}
        month = mon_map[m.group(1)[:3].title()]; year = int(m.group(2))
        return dt(year, month, 1)
    # YYYY
    m = re.match(r"^(19|20)\d{2}$", s)
    if m:
        year = int(s)
        return dt(year, 1, 1)
    return None


def _estimate_years_of_experience(exps: List[Dict[str, Any]]) -> float:
    """Estimate total years of experience using min(start) to max(end/present)."""
    starts: List[dt] = []
    ends: List[dt] = []
    today = dt.today()
    for exp in exps or []:
        sd = _parse_date_guess(exp.get("start_date", ""))
        ed_raw = exp.get("end_date", "")
        ed = _parse_date_guess(ed_raw)
        if sd:
            starts.append(sd)
        if ed_raw and isinstance(ed_raw, str) and ed_raw.lower() == "present":
            ends.append(today)
        elif ed:
            ends.append(ed)
    if not starts:
        return 0.0
    start = min(starts)
    end = max(ends) if ends else today
    years = (end - start).days / 365.25
    return round(max(years, 0.0), 1)


def _render_extracted_summary(detail: Dict[str, Any]):
    """Render comprehensive extracted details instead of just compact summary."""
    pdata = detail.get("parsed_data") or {}
    
    if not isinstance(pdata, dict):
        st.error("No parsed data available")
        return
    
    st.subheader("📄 Extracted Resume Details")
    
    # Personal Information
    personal = pdata.get("personal_info", {})
    if personal:
        st.subheader("👤 Personal Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Name:** {personal.get('name', 'Not found')}")
            st.write(f"**Email:** {personal.get('email', 'Not found')}")
            st.write(f"**Phone:** {personal.get('phone', 'Not found')}")
        
        with col2:
            st.write(f"**Location:** {personal.get('location', 'Not found')}")
            if personal.get('linkedin'):
                st.write(f"**LinkedIn:** [Profile]({personal['linkedin']})")
            if personal.get('github'):
                st.write(f"**GitHub:** [Profile]({personal['github']})")
    
    # Skills
    skills = pdata.get("skills", [])
    if skills:
        st.subheader("🔧 Skills")
        # Show skills in a nice grid
        cols = st.columns(3)
        for i, skill in enumerate(skills):
            with cols[i % 3]:
                st.write(f"• {skill}")
    
    # Experience
    experience = pdata.get("experience", [])
    if experience:
        st.subheader("💼 Work Experience")
        for i, exp in enumerate(experience):
            with st.expander(f"{exp.get('title', 'Position')} at {exp.get('company', 'Company')}", expanded=i==0):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Title:** {exp.get('title', 'Not specified')}")
                    st.write(f"**Company:** {exp.get('company', 'Not specified')}")
                    st.write(f"**Location:** {exp.get('location', 'Not specified')}")
                with col2:
                    st.write(f"**Start Date:** {exp.get('start_date', 'Not specified')}")
                    st.write(f"**End Date:** {exp.get('end_date', 'Not specified')}")
                
                if exp.get('description'):
                    st.write(f"**Description:** {exp['description']}")
                
                if exp.get('technologies'):
                    st.write(f"**Technologies:** {', '.join(exp['technologies'])}")
    else:
        st.subheader("💼 Work Experience")
        st.info("No work experience found in the resume")
    
    # Education
    education = pdata.get("education", [])
    if education:
        st.subheader("🎓 Education")
        for i, edu in enumerate(education):
            with st.expander(f"{edu.get('degree', 'Degree')} - {edu.get('institution', 'Institution')}", expanded=i==0):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Degree:** {edu.get('degree', 'Not specified')}")
                    st.write(f"**Field:** {edu.get('field', 'Not specified')}")
                    st.write(f"**Institution:** {edu.get('institution', 'Not specified')}")
                with col2:
                    st.write(f"**Graduation Date:** {edu.get('graduation_date', 'Not specified')}")
                    if edu.get('gpa'):
                        st.write(f"**GPA:** {edu['gpa']}")
                    if edu.get('location'):
                        st.write(f"**Location:** {edu['location']}")
    else:
        st.subheader("🎓 Education")
        st.info("No education information found in the resume")
    
    # Projects
    projects = pdata.get("projects", [])
    if projects:
        st.subheader("🚀 Projects")
        for proj in projects:
            with st.expander(f"{proj.get('name', 'Project')}"):
                st.write(f"**Description:** {proj.get('description', 'Not specified')}")
                if proj.get('technologies'):
                    st.write(f"**Technologies:** {', '.join(proj['technologies'])}")
                if proj.get('url'):
                    st.write(f"**URL:** [Link]({proj['url']})")
                if proj.get('duration'):
                    st.write(f"**Duration:** {proj['duration']}")
    
    # Certifications
    certifications = pdata.get("certifications", [])
    if certifications:
        st.subheader("🏆 Certifications")
        for cert in certifications:
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"• **{cert.get('name', 'Certification')}**")
            with col2:
                st.write(f"*{cert.get('issuer', 'Unknown Issuer')}* ({cert.get('date', 'Date not specified')})")
    
    # Languages
    languages = pdata.get("languages", [])
    if languages:
        st.subheader("🌍 Languages")
        st.write(", ".join(languages))
    
    # Summary statistics
    exps = pdata.get("experience", [])
    years = _estimate_years_of_experience(exps)
    
    st.subheader("📊 Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Years of Experience", f"{years}")
    with col2:
        st.metric("Skills", len(skills))
    with col3:
        st.metric("Education", len(education))
    with col4:
        st.metric("Projects", len(projects))


def require_login():
    if not st.session_state.get("token"):
        st.warning("Please login to continue.")
        st.stop()


# -------------------------
# Auth UI
# -------------------------
def ui_auth():
    st.subheader("Login")
    # If flagged, clear the password field before rendering widgets
    if st.session_state.get("clear_login_password"):
        st.session_state.pop("login_password", None)
        st.session_state.pop("clear_login_password", None)
    # Quick-fill default credentials
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Use default credentials"):
            st.session_state["login_email"] = "testuser@example.com"
            st.session_state["login_password"] = "password123"
            st.session_state["last_email"] = "testuser@example.com"
            st.rerun()
    with col2:
        st.caption("Fills email/password with testuser@example.com / password123")

    with st.form("login_form", clear_on_submit=False):
        email = st.text_input(
            "Email",
            key="login_email",
            value=st.session_state.get("login_email", st.session_state.get("last_email", "")),
        )
        password = st.text_input(
            "Password",
            type="password",
            key="login_password",
            value=st.session_state.get("login_password", ""),
        )
        submitted = st.form_submit_button("Login")
        if submitted:
            try:
                data = {
                    "email": st.session_state.get("login_email", email),
                    "password": st.session_state.get("login_password", password),
                }
                resp = _api_post("/auth/login", json=data)
                st.session_state.token = resp.get("access_token")
                st.session_state.last_email = data["email"]
                # Clear password field safely on next rerun
                st.session_state["clear_login_password"] = True
                # Load user context and rerun
                _load_user_context(force=True)
                st.success("Logged in!")
                st.rerun()
            except requests.HTTPError as e:
                st.error(f"Login failed: {e.response.text}")

    st.divider()
    st.subheader("Register")
    register_type = st.selectbox("User Type", ["B2C", "B2B"], index=0)
    with st.form("register_form"):
        email_r = st.text_input("Email")
        password_r = st.text_input("Password", type="password")
        if register_type == "B2C":
            username = st.text_input("Username")
            full_name = st.text_input("Full name", "")
            phone = st.text_input("Phone", "")
            location = st.text_input("Location", "")
            bio = st.text_area("Bio", "")
            skills = st.text_input("Skills (comma-separated)", "")
            exp = st.number_input("Experience (years)", 0, 50, 0)
        else:
            username = st.text_input("Username (optional)", "")
            org_name = st.text_input("Org name")
            org_type = st.selectbox("Org type", ["Company", "Institution"]) 
            org_address = st.text_input("Org address")
            org_contact_phone = st.text_input("Org contact phone")
        r_submit = st.form_submit_button("Create account")
        if r_submit:
            try:
                payload = {
                    "email": email_r,
                    "password": password_r,
                    "user_type": "B2C" if register_type == "B2C" else "B2B",
                }
                if register_type == "B2C":
                    payload.update({
                        "username": username,
                        "full_name": full_name,
                        "phone": phone,
                        "location": location,
                        "bio": bio,
                        "skills": ",".join(_comma_list(skills)) if skills else None,
                        "experience_years": int(exp),
                    })
                else:
                    payload.update({
                        "username": username or None,
                        "org_name": org_name,
                        "org_type": org_type,
                        "org_address": org_address,
                        "org_contact_phone": org_contact_phone,
                    })
                user = _api_post("/auth/register", json=payload)
                st.success("Account created. You can login now.")
            except requests.HTTPError as e:
                st.error(f"Registration failed: {e.response.text}")


def ui_account():
    require_login()
    st.subheader("Account")
    try:
        _load_user_context(force=True)
        me = st.session_state.get("me", {})
        st.json(me)
        if me.get("user_type") == "B2B":
            st.info(f"B2B user. Org ID: {me.get('org_id')} | Org Type: {st.session_state.get('org_type')}")
        else:
            st.info("B2C user. You can process resumes and browse jobs/courses.")
    except requests.HTTPError as e:
        st.error(e.response.text)
    if st.button("Logout"):
        st.session_state.pop("token", None)
        st.session_state.pop("me", None)
        st.session_state.pop("user_type", None)
        st.session_state.pop("org_id", None)
        st.session_state.pop("org_type", None)
        st.experimental_rerun()


# -------------------------
# Resume & Recommendations
# -------------------------
def ui_resume():
    require_login()
    if st.session_state.get("user_type") != "B2C":
        st.info("Resume processing is available for B2C users only.")
        return
    st.subheader("Upload Resume (PDF)")
    file = st.file_uploader("Choose a PDF", type=["pdf"], accept_multiple_files=False)
    if file is not None:
        if st.button("Upload & Process"):
            try:
                files = {"file": (file.name, file.read(), "application/pdf")}
                resp = _api_post("/resume/upload", files=files, auth=True)
                st.success(f"Processed: {resp.get('filename')} (Confidence: {resp.get('confidence_score'):.2f})")
                # Show compact extracted summary immediately
                rid = resp.get("id")
                if rid:
                    try:
                        detail = _api_get(f"/resume/{rid}", auth=True)
                        _render_extracted_summary(detail)
                    except requests.HTTPError as e:
                        st.warning(f"Couldn't load details: {e.response.text}")
            except requests.HTTPError as e:
                st.error(f"Upload failed: {e.response.text}")

    st.divider()
    st.subheader("My Resumes")
    try:
        resumes = _api_get("/resume/", auth=True)
        if not resumes:
            st.info("No resumes yet. Upload one above.")
        else:
            for r in resumes:
                with st.expander(f"{r['filename']} | Score: {r['confidence_score']} | Uploaded: {r['uploaded_at']}"):
                    cols = st.columns(3)
                    with cols[0]:
                        if st.button("View details", key=f"view_{r['id']}"):
                            try:
                                detail = _api_get(f"/resume/{r['id']}", auth=True)
                                _render_extracted_summary(detail)
                            except requests.HTTPError as e:
                                st.error(e.response.text)
                    with cols[1]:
                        if st.button("Delete", key=f"del_{r['id']}"):
                            try:
                                _api_delete(f"/resume/{r['id']}", auth=True)
                                st.success("Deleted.")
                                st.experimental_rerun()
                            except requests.HTTPError as e:
                                st.error(e.response.text)
                    with cols[2]:
                        if st.button("Get recommendations", key=f"recs_{r['id']}"):
                            try:
                                recs = _api_get("/resume/recommendations", auth=True)
                                st.write("Based on:", recs.get("based_on_resume"))
                                st.write("Jobs:")
                                st.json(recs.get("job_recommendations", []))
                                st.write("Courses:")
                                st.json(recs.get("course_recommendations", []))
                            except requests.HTTPError as e:
                                st.error(e.response.text)
    except requests.HTTPError as e:
        st.error(e.response.text)


# -------------------------
# Jobs
# -------------------------
JOB_TYPES = ["Full-time", "Internship", "Contract", "Part-time"]
REMOTE_OPTIONS = ["Remote", "On-site", "Hybrid"]
EXPERIENCE_LEVELS = ["Entry", "Mid", "Senior"]


def ui_jobs():
    st.subheader("Jobs")
    query = st.text_input("Search jobs (title/company/location)", "")
    # List jobs
    try:
        jobs = _api_get("/jobs/")
        # Client-side filter
        if query:
            q = query.lower()
            jobs = [j for j in jobs if q in (j.get('title','').lower() + ' ' + (j.get('company_name') or '').lower() + ' ' + (j.get('location') or '').lower())]
        st.write(f"Jobs found: {len(jobs)}")
        for j in jobs:
            with st.expander(f"{j['title']} @ {j.get('company_name') or ''}"):
                st.json(j)
                # Stats
                stats_col1, stats_col2 = st.columns(2)
                with stats_col1:
                    job_id = j['id']
                    if st.button("View stats", key=f"jobstats_{job_id}"):
                        try:
                            stats = _api_get(f"/stats/jobs/{job_id}")
                            st.json(stats)
                        except requests.HTTPError:
                            st.info("No stats available.")
    except requests.HTTPError as e:
        st.error(e.response.text)

    st.divider()
    # Create/Update only for B2B Company users
    if st.session_state.get("token") and st.session_state.get("user_type") == "B2B" and (st.session_state.get("org_type") in (None, "Company")):
        st.subheader("Create / Update Job")
    else:
        return
    with st.form("job_form"):
        mode = st.selectbox("Mode", ["Create", "Update"], index=0)
        job_id_update = st.number_input("Job ID (for Update)", min_value=1, step=1, value=1)
        title = st.text_input("Title")
        company_name = st.text_input("Company Name", "")
        job_type = st.selectbox("Job Type", JOB_TYPES)
        location = st.text_input("Location")
        salary_range = st.text_input("Salary Range")
        responsibilities = st.text_area("Responsibilities", "")
        skills_required = st.text_input("Skills Required (comma-separated)")
        application_deadline = st.date_input("Application Deadline")
        industry = st.text_input("Industry", "")
        remote_option = st.selectbox("Remote Option", ["", *REMOTE_OPTIONS])
        experience_level = st.selectbox("Experience Level", ["", *EXPERIENCE_LEVELS])
        contact_email = st.text_input("Contact Email", "")
        application_url = st.text_input("Application URL", "")
        posted_date = st.date_input("Posted Date", value=date.today())
        updated_date = st.date_input("Updated Date", value=date.today())
        openings = st.number_input("Number of openings", 1, 1000, 1)
        submit = st.form_submit_button("Submit")
        if submit:
            payload = {
                "title": title,
                "company_name": company_name or None,
                "job_type": job_type,
                "location": location,
                "salary_range": salary_range,
                "responsibilities": responsibilities or None,
                "skills_required": _comma_list(skills_required),
                "application_deadline": _iso(application_deadline),
                "industry": industry or None,
                "remote_option": remote_option or None,
                "experience_level": experience_level or None,
                "contact_email": contact_email or None,
                "application_url": application_url or None,
                "posted_date": _iso(posted_date),
                "updated_date": _iso(updated_date),
                "number_of_openings": int(openings),
            }
            try:
                if mode == "Create":
                    created = _api_post("/jobs/", json=payload, auth=True)
                    st.success(f"Created job #{created['id']}")
                else:
                    updated = _api_put(f"/jobs/{int(job_id_update)}", json=payload, auth=True)
                    st.success(f"Updated job #{updated['id']}")
            except requests.HTTPError as e:
                st.error(e.response.text)


# -------------------------
# Courses
# -------------------------
COURSE_MODES = ["Online", "Offline", "Hybrid"]


def ui_courses():
    st.subheader("Courses")
    query = st.text_input("Search courses (name/provider)", "")
    # List courses
    try:
        courses = _api_get("/courses/")
        if query:
            q = query.lower()
            courses = [c for c in courses if q in (c.get('name','').lower() + ' ' + (c.get('provider') or '').lower())]
        st.write(f"Courses found: {len(courses)}")
        for c in courses:
            with st.expander(c['name']):
                st.json(c)
                course_id = c['id']
                if st.button("View stats", key=f"coursestats_{course_id}"):
                    try:
                        stats = _api_get(f"/stats/courses/{course_id}")
                        st.json(stats)
                    except requests.HTTPError:
                        st.info("No stats available.")
    except requests.HTTPError as e:
        st.error(e.response.text)

    st.divider()
    # Create/Update only for B2B Institution users
    if st.session_state.get("token") and st.session_state.get("user_type") == "B2B" and st.session_state.get("org_type") == "Institution":
        st.subheader("Create / Update Course")
    else:
        return
    with st.form("course_form"):
        mode = st.selectbox("Mode", ["Create", "Update"], index=0)
        course_id_update = st.number_input("Course ID (for Update)", min_value=1, step=1, value=1)
        name = st.text_input("Name")
        provider = st.text_input("Provider", "")
        duration = st.text_input("Duration (e.g., 3 months)")
        cmode = st.selectbox("Mode", COURSE_MODES)
        fees = st.text_input("Fees", "")
        description = st.text_area("Description")
        skills_required = st.text_input("Skills Required (comma-separated)")
        application_deadline = st.date_input("Application Deadline")
        prerequisites = st.text_input("Prerequisites (comma-separated)")
        submit = st.form_submit_button("Submit")
        if submit:
            payload = {
                "name": name,
                "provider": provider or None,
                "duration": duration,
                "mode": cmode,
                "fees": fees or None,
                "description": description,
                "skills_required": _comma_list(skills_required),
                "application_deadline": _iso(application_deadline),
                "prerequisites": _comma_list(prerequisites),
            }
            try:
                if mode == "Create":
                    created = _api_post("/courses/", json=payload, auth=True)
                    st.success(f"Created course #{created['id']}")
                else:
                    updated = _api_put(f"/courses/{int(course_id_update)}", json=payload, auth=True)
                    st.success(f"Updated course #{updated['id']}")
            except requests.HTTPError as e:
                st.error(e.response.text)


# -------------------------
# Profile (Org)
# -------------------------
def ui_profile():
    st.subheader("Organization Profile")
    require_login()
    org_id = None
    try:
        me = _api_get("/auth/me", auth=True)
        org_id = me.get("org_id")
    except Exception:
        pass
    org_id = st.number_input("Org ID", min_value=1, value=int(org_id) if org_id else 1)
    cols = st.columns(2)
    with cols[0]:
        if st.button("Load Profile"):
            try:
                prof = _api_get(f"/profile/{int(org_id)}")
                st.session_state["profile_data"] = prof
                st.success("Profile loaded.")
            except requests.HTTPError as e:
                st.error(e.response.text)
    with cols[1]:
        if st.button("Clear"):
            st.session_state.pop("profile_data", None)

    prof_data = st.session_state.get("profile_data")
    if prof_data:
        st.json(prof_data)
        st.divider()
        st.subheader("Update Profile")
        with st.form("profile_update"):
            name = st.text_input("Name", prof_data.get("name", ""))
            address = st.text_input("Address", prof_data.get("address", ""))
            contact_email = st.text_input("Contact Email", prof_data.get("contact_email", ""))
            contact_phone = st.text_input("Contact Phone", prof_data.get("contact_phone", ""))
            logo_path = st.text_input("Logo Path/URL", prof_data.get("logo_path") or "")
            submit = st.form_submit_button("Update")
            if submit:
                payload = {
                    "name": name,
                    "address": address,
                    "contact_email": contact_email,
                    "contact_phone": contact_phone or None,
                    "logo_path": logo_path or None,
                }
                try:
                    updated = _api_put(f"/profile/{int(org_id)}", json=payload, auth=True)
                    st.session_state["profile_data"] = updated
                    st.success("Profile updated.")
                except requests.HTTPError as e:
                    st.error(e.response.text)


# -------------------------
# Interview
# -------------------------
def ui_interview():
    require_login()
    st.subheader("Technical Interview Practice")
    try:
        info = _api_get("/interview/domains")
    except requests.HTTPError as e:
        st.error(e.response.text)
        return

    domains = info.get("domains", [])
    diff_levels = info.get("difficulty_levels", [])
    domain_labels = {d["label"]: d["value"] for d in domains}

    domain_label = st.selectbox("Domain", list(domain_labels.keys()))
    years = st.slider("Years of Experience", 0, 20, 2)

    if st.button("Start Interview"):
        try:
            req = {"domain": domain_labels[domain_label], "years_of_experience": years}
            start = _api_post("/interview/start", json=req, auth=True)
            st.session_state["iv_session"] = start
            st.success(f"Started session #{start['session_id']}")
        except requests.HTTPError as e:
            st.error(e.response.text)

    session = st.session_state.get("iv_session")
    if session:
        st.info(f"Session: {session['session_id']} | {session['domain']} | {session['difficulty_level']} | Questions: {session['total_questions']}")
        with st.form("answers_form"):
            answers_out: List[Dict[str, Any]] = []
            for q in session.get("questions", []):
                ans = st.text_area(f"Q{q['id']}: {q['question']}", key=f"ans_{q['id']}")
                answers_out.append({"question_id": q["id"], "answer": ans})
            submit = st.form_submit_button("Submit Answers")
            if submit:
                try:
                    res = _api_post("/interview/submit", json={"session_id": session["session_id"], "answers": answers_out}, auth=True)
                    st.session_state["iv_result"] = res
                    st.success("Evaluation complete.")
                except requests.HTTPError as e:
                    st.error(e.response.text)

    result = st.session_state.get("iv_result")
    if result:
        st.subheader("Results")
        st.metric("Overall Score", f"{result['overall_score']}%")
        st.write("Grade:", result.get("grade"))
        st.write("Strengths:")
        st.write(result.get("strengths", []))
        st.write("Weaknesses:")
        st.write(result.get("weaknesses", []))
        st.write("Recommendations:")
        st.write(result.get("recommendations", []))
        st.write("Detailed Evaluations:")
        st.json(result.get("question_evaluations", []))

        st.divider()
        st.subheader("Feedback")
        rating = st.slider("Rate this interview experience", 1, 5, 5)
        feedback_text = st.text_area("Feedback")
        suggestions = st.text_area("Suggestions")
        if st.button("Submit Feedback"):
            try:
                _api_post(f"/interview/feedback/{result['session_id']}", params={"rating": rating, "feedback_text": feedback_text, "suggestions": suggestions}, auth=True)
                st.success("Thanks for your feedback!")
            except requests.HTTPError as e:
                st.error(e.response.text)

    st.divider()
    st.subheader("History")
    try:
        hist = _api_get("/interview/history", auth=True)
        st.json(hist)
    except requests.HTTPError:
        st.info("No interview history yet.")


# -------------------------
# App Layout
# -------------------------
st.set_page_config(page_title="AI Talent Platform", page_icon="🧠", layout="wide")

# Keep user context fresh if logged in
if st.session_state.get("token"):
    _load_user_context()

st.title("AI Talent Platform")
st.caption("End-to-end resume intelligence, recommendations, jobs & courses, and interview practice")

with st.sidebar:
    st.header("Navigation")
    authed = bool(st.session_state.get("token"))
    user_type = st.session_state.get("user_type")
    org_type = st.session_state.get("org_type")
    # Build role-based navigation
    if authed and user_type == "B2B":
        if org_type == "Institution":
            options = ["Home", "Courses", "Profile", "Account"]
        else:
            options = ["Home", "Jobs", "Profile", "Account"]
    elif authed and user_type == "B2C":
        options = ["Home", "Resume & Recommendations", "Jobs", "Courses", "Interview", "Account"]
    else:
        options = ["Home", "Jobs", "Courses", "Account"]
    page = st.radio("Go to", options=options, index=0)
    st.markdown("---")
    if authed:
        role = f"{user_type or ''}{' / ' + org_type if org_type else ''}"
        st.success(f"Logged in ({role.strip()})")
    else:
        st.info("Not logged in")

if page == "Home":
    st.write("Welcome! Use the sidebar to explore features. Start by logging in from Account.")
    st.write("API:", API_BASE_URL)
    st.write("Quick links: Resume upload, Recommendations, Jobs/Courses, Interview practice.")
elif page == "Account":
    ui_auth() if not st.session_state.get("token") else ui_account()
elif page == "Resume & Recommendations":
    ui_resume()
elif page == "Jobs":
    ui_jobs()
elif page == "Courses":
    ui_courses()
elif page == "Interview":
    ui_interview()
elif page == "Profile":
    ui_profile()
