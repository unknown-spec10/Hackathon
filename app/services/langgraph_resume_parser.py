"""
LangGraph-based Resume Parser using Groq for fast inference
"""
import json
import re
import os
import logging
from typing import Dict, Any, List, TypedDict, Annotated, Optional
from dataclasses import dataclass
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
import operator
import asyncio
from concurrent.futures import ThreadPoolExecutor


logger = logging.getLogger(__name__)


class ResumeState(TypedDict):
    """State object for the resume parsing workflow"""
    raw_text: str
    cleaned_text: str
    personal_info: Dict[str, Any]
    skills: List[str]
    experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    certifications: List[Dict[str, Any]]
    projects: List[Dict[str, Any]]
    languages: List[str]
    errors: Annotated[List[str], operator.add]
    processing_stage: str


class PersonalInfo(BaseModel):
    """Schema for personal information"""
    name: str = Field(description="Full name of the person", default="")
    email: str = Field(description="Email address", default="")
    phone: str = Field(description="Phone number", default="")
    location: str = Field(description="Current location (city, state/country)", default="")
    linkedin: str = Field(description="LinkedIn profile URL", default="")
    github: str = Field(description="GitHub profile URL", default="")
    portfolio: str = Field(description="Portfolio website URL", default="")


class Experience(BaseModel):
    """Schema for work experience"""
    title: str = Field(description="Job title", default="")
    company: str = Field(description="Company name", default="")
    location: str = Field(description="Work location", default="")
    start_date: str = Field(description="Start date (MM/YYYY format)", default="")
    end_date: str = Field(description="End date (MM/YYYY or Present)", default="")
    description: str = Field(description="Job description and achievements", default="")
    technologies: List[str] = Field(description="Technologies used", default_factory=list)


class Education(BaseModel):
    """Schema for education"""
    degree: str = Field(description="Degree type (Bachelor's, Master's, etc.)", default="")
    field: str = Field(description="Field of study", default="")
    institution: str = Field(description="University/College name", default="")
    graduation_date: str = Field(description="Graduation date (MM/YYYY)", default="")
    gpa: str = Field(description="GPA if mentioned", default="")
    location: str = Field(description="Institution location", default="")


class Certification(BaseModel):
    """Schema for certifications"""
    name: str = Field(description="Certification name", default="")
    issuer: str = Field(description="Issuing organization", default="")
    date: str = Field(description="Certification date", default="")
    expiry: str = Field(description="Expiry date if applicable", default="")


class Project(BaseModel):
    """Schema for projects"""
    name: str = Field(description="Project name", default="")
    description: str = Field(description="Project description", default="")
    technologies: List[str] = Field(description="Technologies used", default_factory=list)
    url: str = Field(description="Project URL if available", default="")
    duration: str = Field(description="Project duration", default="")


class ParsedResumeData(BaseModel):
    """Complete parsed resume data"""
    personal_info: PersonalInfo
    education: List[Education]
    experience: List[Experience]
    skills: List[str]
    certifications: List[Certification]
    languages: List[str]
    projects: List[Project]
    achievements: List[str] = Field(default_factory=list)
    summary: Optional[str] = None


class LangGraphResumeParser:
    """Resume parser using LangGraph workflow with Groq"""
    
    def __init__(self, groq_api_key: str, model_name: str = "mixtral-8x7b-32768"):
        self.groq_api_key = groq_api_key
        self.model_name = model_name
        self.llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name=model_name,
            temperature=0.1,
            max_tokens=4000
        )
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow for resume parsing"""
        workflow = StateGraph(ResumeState)
        
        # Add nodes
        workflow.add_node("clean_text", self._clean_text_node)
        workflow.add_node("extract_personal", self._extract_personal_info_node)
        workflow.add_node("extract_skills", self._extract_skills_node)
        workflow.add_node("extract_experience", self._extract_experience_node)
        workflow.add_node("extract_education", self._extract_education_node)
        workflow.add_node("extract_certifications", self._extract_certifications_node)
        workflow.add_node("extract_projects", self._extract_projects_node)
        workflow.add_node("extract_languages", self._extract_languages_node)
        workflow.add_node("validate_results", self._validate_results_node)
        
        # Define the workflow
        workflow.set_entry_point("clean_text")
        
        # Sequential flow for main extractions
        workflow.add_edge("clean_text", "extract_personal")
        workflow.add_edge("extract_personal", "extract_skills")
        workflow.add_edge("extract_skills", "extract_experience")
        workflow.add_edge("extract_experience", "extract_education")
        workflow.add_edge("extract_education", "extract_certifications")
        workflow.add_edge("extract_certifications", "extract_projects")
        workflow.add_edge("extract_projects", "extract_languages")
        workflow.add_edge("extract_languages", "validate_results")
        workflow.add_edge("validate_results", END)
        
        return workflow.compile()
    
    def _clean_text_node(self, state: ResumeState) -> ResumeState:
        """Clean and preprocess the resume text"""
        try:
            raw_text = state["raw_text"]
            
            # Remove extra whitespace and normalize
            cleaned = re.sub(r'\s+', ' ', raw_text)
            
            # Remove special characters but keep important punctuation
            cleaned = re.sub(r'[^\w\s@.,/-]', '', cleaned)
            
            # Remove page separators and common PDF artifacts
            cleaned = re.sub(r'--- Page \d+ ---', '', cleaned)
            cleaned = re.sub(r'\f', ' ', cleaned)  # Form feed
            
            state["cleaned_text"] = cleaned.strip()
            state["processing_stage"] = "text_cleaned"
            
        except Exception as e:
            state["errors"].append(f"Text cleaning error: {str(e)}")
            state["cleaned_text"] = state["raw_text"]
        
        return state
    
    def _extract_personal_info_node(self, state: ResumeState) -> ResumeState:
        """Extract personal information using Groq"""
        try:
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content="""Extract personal information from this resume text. Return ONLY a valid JSON object.
                
                Required JSON format:
                {
                    "name": "Full Name",
                    "email": "email@example.com",
                    "phone": "phone number",
                    "location": "city, state/country",
                    "linkedin": "linkedin url or empty string",
                    "github": "github url or empty string",
                    "portfolio": "portfolio url or empty string"
                }
                
                If information is not found, use empty string. Ensure valid JSON format."""),
                HumanMessage(content=f"Resume Text:\n{state['cleaned_text'][:2000]}")
            ])
            
            response = self.llm.invoke(prompt.format_messages())
            result = self._extract_json_from_response(response.content, fallback={})
            state["personal_info"] = result
            state["processing_stage"] = "personal_extracted"
            
        except Exception as e:
            state["errors"].append(f"Personal info extraction error: {str(e)}")
            state["personal_info"] = self._fallback_personal_info(state["cleaned_text"])
        
        return state
    
    def _extract_skills_node(self, state: ResumeState) -> ResumeState:
        """Extract skills using Groq"""
        try:
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content="""Extract ALL technical skills, programming languages, frameworks, tools, and technologies from this resume.
                Focus on: Programming languages, frameworks, databases, cloud platforms, tools, methodologies.
                
                Return ONLY a JSON array of skills:
                ["Python", "JavaScript", "React", "SQL", "AWS", "Docker", "Git", ...]
                
                Include both explicit skills and those mentioned in project/work descriptions."""),
                HumanMessage(content=f"Resume Text:\n{state['cleaned_text']}")
            ])
            
            response = self.llm.invoke(prompt.format_messages())
            skills = self._extract_json_from_response(response.content, fallback=[])
            
            if not isinstance(skills, list):
                skills = []
            
            # Add regex-based skill extraction as backup
            regex_skills = self._extract_skills_regex(state["cleaned_text"])
            all_skills = list(set(skills + regex_skills))
            
            state["skills"] = all_skills
            state["processing_stage"] = "skills_extracted"
            
        except Exception as e:
            state["errors"].append(f"Skills extraction error: {str(e)}")
            state["skills"] = self._extract_skills_regex(state["cleaned_text"])
        
        return state
    
    def _extract_experience_node(self, state: ResumeState) -> ResumeState:
        """Extract work experience using Groq"""
        try:
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content="""Extract work experience from this resume. Look for job titles, companies, dates, and descriptions.
                
                Return ONLY a JSON array of experience objects:
                [{
                    "title": "Job Title",
                    "company": "Company Name",
                    "location": "City, State",
                    "start_date": "MM/YYYY",
                    "end_date": "MM/YYYY or Present",
                    "description": "Job description and key achievements",
                    "technologies": ["tech1", "tech2"]
                }]
                
                If no experience found, return empty array []."""),
                HumanMessage(content=f"Resume Text:\n{state['cleaned_text']}")
            ])
            
            response = self.llm.invoke(prompt.format_messages())
            experience = self._extract_json_from_response(response.content, fallback=[])
            
            if not isinstance(experience, list):
                experience = []
            
            state["experience"] = experience
            state["processing_stage"] = "experience_extracted"
            
        except Exception as e:
            state["errors"].append(f"Experience extraction error: {str(e)}")
            state["experience"] = []
        
        return state
    
    def _extract_education_node(self, state: ResumeState) -> ResumeState:
        """Extract education using Groq"""
        try:
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content="""Extract education information from this resume.
                
                Return ONLY a JSON array of education objects:
                [{
                    "degree": "Bachelor's/Master's/PhD/etc.",
                    "field": "Field of Study",
                    "institution": "University/College Name",
                    "graduation_date": "MM/YYYY",
                    "gpa": "GPA if mentioned or empty string",
                    "location": "City, State or empty string"
                }]
                
                If no education found, return empty array []."""),
                HumanMessage(content=f"Resume Text:\n{state['cleaned_text']}")
            ])
            
            response = self.llm.invoke(prompt.format_messages())
            education = self._extract_json_from_response(response.content, fallback=[])
            
            if not isinstance(education, list):
                education = []
            
            state["education"] = education
            state["processing_stage"] = "education_extracted"
            
        except Exception as e:
            state["errors"].append(f"Education extraction error: {str(e)}")
            state["education"] = []
        
        return state
    
    def _extract_certifications_node(self, state: ResumeState) -> ResumeState:
        """Extract certifications using both Groq and regex"""
        try:
            # Use regex for common certifications
            certifications = self._extract_certifications_regex(state["cleaned_text"])
            
            # Enhance with Groq if needed
            if len(certifications) < 3:  # Only use Groq if we didn't find many
                prompt = ChatPromptTemplate.from_messages([
                    SystemMessage(content="""Extract certifications and professional credentials from this resume.
                    
                    Return ONLY a JSON array of certification objects:
                    [{
                        "name": "Certification Name",
                        "issuer": "Issuing Organization",
                        "date": "MM/YYYY or empty string",
                        "expiry": "MM/YYYY or empty string"
                    }]
                    
                    If no certifications found, return empty array []."""),
                    HumanMessage(content=f"Resume Text:\n{state['cleaned_text']}")
                ])
                
                response = self.llm.invoke(prompt.format_messages())
                llm_certs = self._extract_json_from_response(response.content, fallback=[])
                
                if isinstance(llm_certs, list):
                    certifications.extend(llm_certs)
            
            state["certifications"] = certifications
            state["processing_stage"] = "certifications_extracted"
            
        except Exception as e:
            state["errors"].append(f"Certifications extraction error: {str(e)}")
            state["certifications"] = []
        
        return state
    
    def _extract_projects_node(self, state: ResumeState) -> ResumeState:
        """Extract projects using Groq"""
        try:
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content="""Extract personal projects, academic projects, or significant work projects from this resume.
                
                Return ONLY a JSON array of project objects:
                [{
                    "name": "Project Name",
                    "description": "Brief project description",
                    "technologies": ["tech1", "tech2"],
                    "url": "project URL or empty string",
                    "duration": "project duration or empty string"
                }]
                
                If no projects found, return empty array []."""),
                HumanMessage(content=f"Resume Text:\n{state['cleaned_text']}")
            ])
            
            response = self.llm.invoke(prompt.format_messages())
            projects = self._extract_json_from_response(response.content, fallback=[])
            
            if not isinstance(projects, list):
                projects = []
            
            state["projects"] = projects
            state["processing_stage"] = "projects_extracted"
            
        except Exception as e:
            state["errors"].append(f"Projects extraction error: {str(e)}")
            state["projects"] = []
        
        return state
    
    def _extract_languages_node(self, state: ResumeState) -> ResumeState:
        """Extract spoken languages using regex"""
        try:
            languages = self._extract_languages_regex(state["cleaned_text"])
            state["languages"] = languages
            state["processing_stage"] = "languages_extracted"
            
        except Exception as e:
            state["errors"].append(f"Languages extraction error: {str(e)}")
            state["languages"] = []
        
        return state
    
    def _validate_results_node(self, state: ResumeState) -> ResumeState:
        """Validate and clean up extracted results"""
        try:
            # Ensure personal info has at least a name
            if not state["personal_info"].get("name") or state["personal_info"]["name"] == "":
                # Try to extract name from text
                name = self._extract_name_fallback(state["cleaned_text"])
                state["personal_info"]["name"] = name
            
            # Remove duplicate skills
            state["skills"] = list(set(state["skills"]))
            
            # Sort experience by dates (most recent first)
            state["experience"] = self._sort_experience_by_date(state["experience"])
            
            state["processing_stage"] = "completed"
            
        except Exception as e:
            state["errors"].append(f"Validation error: {str(e)}")
        
        return state
    
    # Helper methods
    def _extract_json_from_response(self, response: str, fallback=None):
        """Extract JSON from LLM response"""
        try:
            # Find JSON in the response
            json_match = re.search(r'\{.*\}|\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return fallback
        except Exception:
            return fallback
    
    def _fallback_personal_info(self, text: str) -> Dict[str, str]:
        """Fallback personal info extraction using regex"""
        info = {
            "name": "",
            "email": "",
            "phone": "",
            "location": "",
            "linkedin": "",
            "github": "",
            "portfolio": ""
        }
        
        # Email
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if email_match:
            info["email"] = email_match.group()
        
        # Phone
        phone_match = re.search(r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})', text)
        if phone_match:
            info["phone"] = phone_match.group()
        
        # LinkedIn
        linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', text, re.IGNORECASE)
        if linkedin_match:
            info["linkedin"] = f"https://{linkedin_match.group()}"
        
        # GitHub
        github_match = re.search(r'github\.com/[\w-]+', text, re.IGNORECASE)
        if github_match:
            info["github"] = f"https://{github_match.group()}"
        
        # Name (first line or before email)
        lines = text.split('\n')[:5]  # First 5 lines
        for line in lines:
            line = line.strip()
            if len(line) > 3 and len(line) < 50 and not '@' in line:
                # Simple heuristic for name
                words = line.split()
                if 2 <= len(words) <= 4 and all(word.isalpha() for word in words):
                    info["name"] = line
                    break
        
        return info
    
    def _extract_skills_regex(self, text: str) -> List[str]:
        """Extract skills using regex patterns"""
        skills = []
        
        # Common programming languages and technologies
        tech_patterns = [
            r'\b(Python|Java|JavaScript|TypeScript|C\+\+|C#|PHP|Ruby|Go|Rust|Swift|Kotlin)\b',
            r'\b(React|Angular|Vue|Node\.js|Express|Django|Flask|Spring|Laravel)\b',
            r'\b(HTML|CSS|SCSS|Sass|Bootstrap|Tailwind)\b',
            r'\b(MySQL|PostgreSQL|MongoDB|Redis|SQLite|Oracle|SQL Server)\b',
            r'\b(AWS|Azure|GCP|Google Cloud|Docker|Kubernetes|Jenkins|Git|GitHub)\b',
            r'\b(Machine Learning|AI|Data Science|Pandas|NumPy|TensorFlow|PyTorch)\b'
        ]
        
        for pattern in tech_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                skill = match.group().strip()
                if skill not in skills:
                    skills.append(skill)
        
        return skills
    
    def _extract_certifications_regex(self, text: str) -> List[Dict[str, str]]:
        """Extract certifications using regex patterns"""
        certifications = []
        
        cert_patterns = [
            r'(AWS|Amazon)\s+(Certified|Certificate)',
            r'(Microsoft|Azure)\s+(Certified|Certificate)',
            r'(Google|GCP)\s+(Certified|Certificate)',
            r'(PMP|Project Management Professional)',
            r'(CISSP|CISA|CEH|CISM)',
            r'(Scrum Master|Agile)',
            r'(CPA|Certified Public Accountant)',
            r'(Six Sigma|Lean)',
        ]
        
        for pattern in cert_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                certifications.append({
                    "name": match.group().strip(),
                    "issuer": "Unknown",
                    "date": "",
                    "expiry": ""
                })
        
        return certifications
    
    def _extract_languages_regex(self, text: str) -> List[str]:
        """Extract spoken languages using regex"""
        languages = []
        
        lang_pattern = r'\b(English|Spanish|French|German|Chinese|Mandarin|Japanese|Korean|Hindi|Arabic|Portuguese|Russian|Italian|Dutch|Swedish|Norwegian)\b'
        matches = re.finditer(lang_pattern, text, re.IGNORECASE)
        
        for match in matches:
            lang = match.group().title()
            if lang not in languages:
                languages.append(lang)
        
        return languages
    
    def _extract_name_fallback(self, text: str) -> str:
        """Fallback name extraction"""
        lines = text.split('\n')[:10]
        for line in lines:
            line = line.strip()
            words = line.split()
            if 2 <= len(words) <= 4 and all(word.replace('.', '').isalpha() for word in words):
                return line
        return "Unknown"
    
    def _sort_experience_by_date(self, experience: List[Dict]) -> List[Dict]:
        """Sort experience by end date (most recent first)"""
        def date_sort_key(exp):
            end_date = exp.get("end_date", "")
            if end_date.lower() == "present":
                return "9999/12"  # Sort present jobs first
            return end_date
        
        try:
            return sorted(experience, key=date_sort_key, reverse=True)
        except:
            return experience
    
    async def parse_resume_async(self, resume_text: str) -> Dict[str, Any]:
        """Parse resume asynchronously using the LangGraph workflow"""
        initial_state = ResumeState(
            raw_text=resume_text,
            cleaned_text="",
            personal_info={},
            skills=[],
            experience=[],
            education=[],
            certifications=[],
            projects=[],
            languages=[],
            errors=[],
            processing_stage="initialized"
        )
        
        # Run the workflow
        final_state = await self.workflow.ainvoke(initial_state)
        
        return {
            "personal_info": final_state["personal_info"],
            "skills": final_state["skills"],
            "experience": final_state["experience"],
            "education": final_state["education"],
            "certifications": final_state["certifications"],
            "projects": final_state["projects"],
            "languages": final_state["languages"],
            "processing_stage": final_state["processing_stage"],
            "errors": final_state["errors"]
        }
    
    def parse_resume(self, resume_text: str) -> ParsedResumeData:
        """Synchronous wrapper for resume parsing"""
        try:
            result = asyncio.run(self.parse_resume_async(resume_text))
            
            # Convert to Pydantic models
            personal_info = PersonalInfo(**result["personal_info"])
            
            education = [Education(**edu) for edu in result["education"]]
            experience = [Experience(**exp) for exp in result["experience"]]
            certifications = [Certification(**cert) for cert in result["certifications"]]
            projects = [Project(**proj) for proj in result["projects"]]
            
            return ParsedResumeData(
                personal_info=personal_info,
                education=education,
                experience=experience,
                skills=result["skills"],
                certifications=certifications,
                languages=result["languages"],
                projects=projects,
                achievements=[],
                summary=None
            )
        except Exception as e:
            logger.error(f"Error in parse_resume: {e}")
            return ParsedResumeData(
                personal_info=PersonalInfo(),
                education=[],
                experience=[],
                skills=[],
                certifications=[],
                languages=[],
                projects=[],
                achievements=[],
                summary=None
            )


# Factory function for creating parser instance
def create_resume_parser(groq_api_key: str = None) -> LangGraphResumeParser:
    """Create a resume parser instance"""
    if not groq_api_key:
        groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY environment variable is required")
    
    return LangGraphResumeParser(groq_api_key)

