from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import json


class DataSource(str, Enum):
    """Source of data for talent profile"""
    FORM = "form"
    RESUME = "resume"
    COMBINED = "combined"


class ContactInfo(BaseModel):
    """Comprehensive contact information from both sources"""
    email: str = Field(default="", description="Email address")
    phone: str = Field(default="", description="Phone number")
    location: str = Field(default="", description="Current location")
    linkedin: str = Field(default="", description="LinkedIn profile URL")
    github: str = Field(default="", description="GitHub profile URL")
    portfolio: str = Field(default="", description="Portfolio website URL")
    
    # Source tracking
    email_source: DataSource = Field(default=DataSource.FORM)
    phone_source: DataSource = Field(default=DataSource.FORM)
    location_source: DataSource = Field(default=DataSource.FORM)
    linkedin_source: DataSource = Field(default=DataSource.RESUME)
    github_source: DataSource = Field(default=DataSource.RESUME)
    portfolio_source: DataSource = Field(default=DataSource.RESUME)


class ProfessionalInfo(BaseModel):
    """Professional information combining form and resume data"""
    current_role: str = Field(default="", description="Current job title/role")
    current_company: str = Field(default="", description="Current company")
    experience_years: int = Field(default=0, description="Total years of experience")
    industry: str = Field(default="", description="Industry sector")
    career_level: str = Field(default="", description="Career level (Entry/Mid/Senior)")
    salary_expectation: str = Field(default="", description="Expected salary range")
    
    # Source tracking
    current_role_source: DataSource = Field(default=DataSource.FORM)
    current_company_source: DataSource = Field(default=DataSource.RESUME)
    experience_years_source: DataSource = Field(default=DataSource.COMBINED)


class SkillsProfile(BaseModel):
    """Comprehensive skills from form and resume"""
    technical_skills: List[str] = Field(default_factory=list, description="Technical skills")
    soft_skills: List[str] = Field(default_factory=list, description="Soft skills")
    programming_languages: List[str] = Field(default_factory=list, description="Programming languages")
    frameworks: List[str] = Field(default_factory=list, description="Frameworks and libraries")
    tools: List[str] = Field(default_factory=list, description="Tools and software")
    certifications: List[str] = Field(default_factory=list, description="Professional certifications")
    
    # Skill confidence levels (1-5 scale)
    skill_confidence: Dict[str, int] = Field(default_factory=dict, description="Confidence level for each skill")
    
    # Source tracking
    technical_skills_source: DataSource = Field(default=DataSource.COMBINED)
    soft_skills_source: DataSource = Field(default=DataSource.RESUME)


class EducationProfile(BaseModel):
    """Education information from both sources"""
    highest_degree: str = Field(default="", description="Highest education level")
    field_of_study: str = Field(default="", description="Major/field of study")
    institution: str = Field(default="", description="Educational institution")
    graduation_year: str = Field(default="", description="Graduation year")
    gpa: str = Field(default="", description="GPA if available")
    relevant_coursework: List[str] = Field(default_factory=list, description="Relevant courses")
    
    # Source tracking
    highest_degree_source: DataSource = Field(default=DataSource.FORM)
    field_of_study_source: DataSource = Field(default=DataSource.RESUME)


class WorkExperience(BaseModel):
    """Individual work experience entry"""
    title: str = Field(description="Job title")
    company: str = Field(description="Company name")
    location: str = Field(default="", description="Work location")
    start_date: str = Field(description="Start date")
    end_date: str = Field(description="End date or Present")
    description: str = Field(description="Job description and achievements")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")
    achievements: List[str] = Field(default_factory=list, description="Key achievements")
    source: DataSource = Field(default=DataSource.RESUME, description="Source of this data")


class ProjectExperience(BaseModel):
    """Project experience from resume"""
    name: str = Field(description="Project name")
    description: str = Field(description="Project description")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")
    url: str = Field(default="", description="Project URL if available")
    source: DataSource = Field(default=DataSource.RESUME)


class JobPreferences(BaseModel):
    """Job search preferences from form"""
    preferred_roles: List[str] = Field(default_factory=list, description="Preferred job titles")
    preferred_industries: List[str] = Field(default_factory=list, description="Preferred industries")
    preferred_locations: List[str] = Field(default_factory=list, description="Preferred work locations")
    remote_preference: str = Field(default="", description="Remote work preference")
    job_type_preference: List[str] = Field(default_factory=list, description="Preferred job types")
    salary_range: str = Field(default="", description="Expected salary range")
    availability: str = Field(default="", description="When available to start")


class LearningProfile(BaseModel):
    """Learning and development preferences"""
    learning_goals: List[str] = Field(default_factory=list, description="Learning objectives")
    preferred_learning_modes: List[str] = Field(default_factory=list, description="Online, Offline, Hybrid")
    skill_gaps: List[str] = Field(default_factory=list, description="Skills to develop")
    course_interests: List[str] = Field(default_factory=list, description="Course categories of interest")
    time_commitment: str = Field(default="", description="Time available for learning")


class ComprehensiveTalentProfile(BaseModel):
    """Combined talent profile from form and resume data"""
    # Basic Info
    user_id: int = Field(description="User ID")
    full_name: str = Field(description="Full name")
    username: str = Field(description="Username")
    
    # Contact & Personal
    contact_info: ContactInfo = Field(default_factory=ContactInfo)
    bio: str = Field(default="", description="Professional bio/summary")
    
    # Professional Information
    professional_info: ProfessionalInfo = Field(default_factory=ProfessionalInfo)
    
    # Skills & Expertise
    skills_profile: SkillsProfile = Field(default_factory=SkillsProfile)
    
    # Education
    education_profile: EducationProfile = Field(default_factory=EducationProfile)
    
    # Experience
    work_experience: List[WorkExperience] = Field(default_factory=list)
    project_experience: List[ProjectExperience] = Field(default_factory=list)
    
    # Preferences
    job_preferences: JobPreferences = Field(default_factory=JobPreferences)
    learning_profile: LearningProfile = Field(default_factory=LearningProfile)
    
    # Metadata
    profile_completeness: float = Field(default=0.0, description="Profile completion percentage")
    last_updated: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Last update timestamp")
    resume_file_path: str = Field(default="", description="Path to uploaded resume")
    resume_confidence_score: float = Field(default=0.0, description="AI extraction confidence")
    
    # Data Source Tracking
    data_sources: Dict[str, DataSource] = Field(default_factory=dict, description="Source tracking for each field")
    extraction_errors: List[str] = Field(default_factory=list, description="Any errors during data extraction")
    
    model_config = {"from_attributes": True}
    
    def to_json_safe(self) -> dict:
        """Convert to JSON-safe dictionary for database storage"""
        data = self.model_dump()
        
        # Ensure all datetime objects are converted to strings
        def convert_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, dict):
                return {k: convert_datetime(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_datetime(item) for item in obj]
            else:
                return obj
        
        return convert_datetime(data)


class TalentProfileMerger:
    """Utility class to merge form data with resume extracted data"""
    
    @staticmethod
    def merge_profiles(form_data: dict, resume_data: dict) -> ComprehensiveTalentProfile:
        """
        Merge form data with resume extracted data
        Priority: Form data takes precedence over resume data for overlapping fields
        """
        
        # Initialize with form data
        profile = ComprehensiveTalentProfile(
            user_id=form_data.get('user_id', 0),
            full_name=form_data.get('full_name', ''),
            username=form_data.get('username', ''),
            bio=form_data.get('bio', '')
        )
        
        # Merge contact information
        profile.contact_info = TalentProfileMerger._merge_contact_info(form_data, resume_data)
        
        # Merge professional information
        profile.professional_info = TalentProfileMerger._merge_professional_info(form_data, resume_data)
        
        # Merge skills
        profile.skills_profile = TalentProfileMerger._merge_skills(form_data, resume_data)
        
        # Merge education
        profile.education_profile = TalentProfileMerger._merge_education(form_data, resume_data)
        
        # Add work experience from resume
        profile.work_experience = TalentProfileMerger._extract_work_experience(resume_data)
        
        # Add project experience from resume
        profile.project_experience = TalentProfileMerger._extract_project_experience(resume_data)
        
        # Set job preferences from form
        profile.job_preferences = TalentProfileMerger._set_job_preferences(form_data)
        
        # Set learning preferences from form
        profile.learning_profile = TalentProfileMerger._set_learning_preferences(form_data)
        
        # Calculate profile completeness
        profile.profile_completeness = TalentProfileMerger._calculate_completeness(profile)
        
        # Set metadata
        profile.resume_confidence_score = resume_data.get('confidence_score', 0.0)
        profile.extraction_errors = resume_data.get('errors', [])
        
        return profile
    
    @staticmethod
    def _merge_contact_info(form_data: dict, resume_data: dict) -> ContactInfo:
        """Merge contact information prioritizing form data"""
        personal_info = resume_data.get('personal_info', {})
        
        return ContactInfo(
            email=form_data.get('email') or personal_info.get('email', ''),
            phone=form_data.get('phone') or personal_info.get('phone', ''),
            location=form_data.get('location') or personal_info.get('location', ''),
            linkedin=personal_info.get('linkedin', ''),
            github=personal_info.get('github', ''),
            portfolio=personal_info.get('portfolio', ''),
            email_source=DataSource.FORM if form_data.get('email') else DataSource.RESUME,
            phone_source=DataSource.FORM if form_data.get('phone') else DataSource.RESUME,
            location_source=DataSource.FORM if form_data.get('location') else DataSource.RESUME
        )
    
    @staticmethod
    def _merge_professional_info(form_data: dict, resume_data: dict) -> ProfessionalInfo:
        """Merge professional information"""
        experience_list = resume_data.get('experience', [])
        current_role = form_data.get('current_role', '')
        
        # Extract current role from most recent experience if not in form
        if not current_role and experience_list:
            current_exp = experience_list[0]  # Assuming first is most recent
            current_role = current_exp.get('title', '')
        
        return ProfessionalInfo(
            current_role=current_role,
            current_company=experience_list[0].get('company', '') if experience_list else '',
            experience_years=form_data.get('experience_years', 0),
            industry=form_data.get('industry', ''),
            career_level=form_data.get('career_level', ''),
            salary_expectation=form_data.get('salary_expectation', ''),
            current_role_source=DataSource.FORM if form_data.get('current_role') else DataSource.RESUME
        )
    
    @staticmethod
    def _merge_skills(form_data: dict, resume_data: dict) -> SkillsProfile:
        """Merge skills from both sources"""
        form_skills = form_data.get('skills', '').split(',') if form_data.get('skills') else []
        form_skills = [skill.strip() for skill in form_skills if skill.strip()]
        
        resume_skills = resume_data.get('skills', [])
        
        # Combine and deduplicate skills
        all_skills = list(set(form_skills + resume_skills))
        
        return SkillsProfile(
            technical_skills=all_skills,
            programming_languages=[skill for skill in all_skills if any(lang in skill.lower() 
                                 for lang in ['python', 'java', 'javascript', 'c++', 'c#', 'go', 'rust'])],
            frameworks=[skill for skill in all_skills if any(fw in skill.lower() 
                       for fw in ['react', 'angular', 'vue', 'django', 'flask', 'fastapi', 'spring'])],
            technical_skills_source=DataSource.COMBINED if form_skills and resume_skills else 
                                  (DataSource.FORM if form_skills else DataSource.RESUME)
        )
    
    @staticmethod
    def _merge_education(form_data: dict, resume_data: dict) -> EducationProfile:
        """Merge education information"""
        education_list = resume_data.get('education', [])
        highest_education = education_list[0] if education_list else {}
        
        return EducationProfile(
            highest_degree=form_data.get('education_level') or highest_education.get('degree', ''),
            field_of_study=highest_education.get('field', ''),
            institution=highest_education.get('institution', ''),
            graduation_year=highest_education.get('year', ''),
            highest_degree_source=DataSource.FORM if form_data.get('education_level') else DataSource.RESUME
        )
    
    @staticmethod
    def _extract_work_experience(resume_data: dict) -> List[WorkExperience]:
        """Extract work experience from resume data"""
        experience_list = resume_data.get('experience', [])
        
        return [
            WorkExperience(
                title=exp.get('title', ''),
                company=exp.get('company', ''),
                location=exp.get('location', ''),
                start_date=exp.get('start_date', ''),
                end_date=exp.get('end_date', ''),
                description=exp.get('description', ''),
                technologies=exp.get('technologies', []),
                achievements=exp.get('achievements', [])
            )
            for exp in experience_list
        ]
    
    @staticmethod
    def _extract_project_experience(resume_data: dict) -> List[ProjectExperience]:
        """Extract project experience from resume data"""
        projects_list = resume_data.get('projects', [])
        
        return [
            ProjectExperience(
                name=proj.get('name', ''),
                description=proj.get('description', ''),
                technologies=proj.get('technologies', []),
                url=proj.get('url', '')
            )
            for proj in projects_list
        ]
    
    @staticmethod
    def _set_job_preferences(form_data: dict) -> JobPreferences:
        """Set job preferences from form data"""
        return JobPreferences(
            preferred_roles=form_data.get('preferred_roles', []),
            preferred_industries=form_data.get('preferred_industries', []),
            preferred_locations=form_data.get('preferred_locations', []),
            remote_preference=form_data.get('remote_preference', ''),
            job_type_preference=form_data.get('job_type_preference', []),
            salary_range=form_data.get('salary_range', ''),
            availability=form_data.get('availability', '')
        )
    
    @staticmethod
    def _set_learning_preferences(form_data: dict) -> LearningProfile:
        """Set learning preferences from form data"""
        return LearningProfile(
            learning_goals=form_data.get('learning_goals', []),
            preferred_learning_modes=form_data.get('preferred_learning_modes', []),
            skill_gaps=form_data.get('skill_gaps', []),
            course_interests=form_data.get('course_interests', []),
            time_commitment=form_data.get('time_commitment', '')
        )
    
    @staticmethod
    def _calculate_completeness(profile: ComprehensiveTalentProfile) -> float:
        """Calculate profile completeness percentage"""
        total_fields = 0
        filled_fields = 0
        
        # Count basic info
        basic_fields = [profile.full_name, profile.contact_info.email, profile.bio]
        total_fields += len(basic_fields)
        filled_fields += sum(1 for field in basic_fields if field)
        
        # Count professional info
        prof_fields = [profile.professional_info.current_role, profile.professional_info.experience_years]
        total_fields += len(prof_fields)
        filled_fields += sum(1 for field in prof_fields if field)
        
        # Count skills
        if profile.skills_profile.technical_skills:
            filled_fields += 1
        total_fields += 1
        
        # Count education
        if profile.education_profile.highest_degree:
            filled_fields += 1
        total_fields += 1
        
        # Count experience
        if profile.work_experience:
            filled_fields += 1
        total_fields += 1
        
        return round((filled_fields / total_fields) * 100, 2) if total_fields > 0 else 0.0
