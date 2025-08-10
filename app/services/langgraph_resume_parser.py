"""
LangGraph Resume Parser with Groq AI Integration
Workflow: Text Extraction → AI Parsing → NLP Insights → Structured Output
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
from .nlp_insights import NLPInsightsAnalyzer, CareerInsights


logger = logging.getLogger(__name__)


class ResumeState(TypedDict):
    """Workflow state for resume parsing pipeline"""
    raw_text: str
    cleaned_text: str
    tables_data: List[Dict[str, Any]]
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
    """Personal information schema"""
    name: str = Field(description="Full name", default="")
    email: str = Field(description="Email address", default="")
    phone: str = Field(description="Phone number", default="")
    location: str = Field(description="Location (city, state/country)", default="")
    linkedin: str = Field(description="LinkedIn URL", default="")
    github: str = Field(description="GitHub URL", default="")
    portfolio: str = Field(description="Portfolio URL", default="")


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
    nlp_insights: Optional[Dict[str, Any]] = Field(default=None, description="AI-generated career insights")


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
        # Initialize NLP insights analyzer using factory method
        self.insights_analyzer = NLPInsightsAnalyzer.create_with_fallback()
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
        """Extract education using smart approach: tables when detected, OCR when images present, standard text otherwise"""
        try:
            education = []
            extraction_source = "standard_text"  # Track what method was used
            
            # Check if tables are available and contain data
            has_tables = state.get("tables_data") and len(state["tables_data"]) > 0
            
            # Check if OCR text is available (indicates images were processed)
            has_ocr_text = state.get("ocr_text") and state["ocr_text"].strip()
            
            logger.info(f"Education extraction - has_tables: {has_tables}, has_ocr_text: {bool(has_ocr_text)}")
            
            # Strategy 1: Extract from tables if tables are detected
            if has_tables:
                logger.info("Tables detected - extracting education from table data")
                table_education = self._extract_education_from_tables(state["tables_data"])
                if table_education:
                    education.extend(table_education)
                    extraction_source = "tables"
                    logger.info(f"Found {len(table_education)} education entries from tables")
            
            # Strategy 2: If no education from tables and OCR text is available, try OCR text
            if not education and has_ocr_text:
                logger.info("No education from tables, trying OCR text extraction")
                ocr_education = self._extract_education_from_text(state["ocr_text"])
                if ocr_education:
                    education.extend(ocr_education)
                    extraction_source = "ocr_text"
                    logger.info(f"Found {len(ocr_education)} education entries from OCR text")
            
            # Strategy 3: Standard text extraction (only if no education found yet)
            if not education:
                logger.info("No education found yet, extracting from standard text")
                text_education = self._extract_education_from_text(state['cleaned_text'])
                if text_education:
                    education.extend(text_education)
                    extraction_source = "standard_text"
                    logger.info(f"Found {len(text_education)} education entries from standard text")
            
            # Log education before deduplication
            logger.info(f"Before deduplication: {len(education)} education entries")
            for i, edu in enumerate(education):
                logger.info(f"  Pre-dedupe {i+1}: {edu}")
            
            # Remove duplicates and clean up
            education = self._deduplicate_education(education)
            
            # Log education after deduplication
            logger.info(f"After deduplication: {len(education)} education entries")
            for i, edu in enumerate(education):
                logger.info(f"  Post-dedupe {i+1}: {edu}")
            
            state["education"] = education
            state["processing_stage"] = "education_extracted"
            
            # Log for debugging
            logger.info(f"Education extraction: Found {len(education)} education entries using {extraction_source}")
            
        except Exception as e:
            state["errors"].append(f"Education extraction error: {str(e)}")
            state["education"] = []
            logger.error(f"Education extraction failed: {e}")
        
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
        """Extract skills using comprehensive regex patterns"""
        skills = []
        
        # Enhanced programming languages and technologies
        tech_patterns = [
            # Programming Languages
            r'\b(Python|Java|JavaScript|TypeScript|C\+\+|C#|PHP|Ruby|Go|Rust|Swift|Kotlin|Scala|R|MATLAB|Perl|Lua|Dart|Elixir|Clojure|Haskell|F#|VB\.NET|COBOL|Fortran|Assembly)\b',
            
            # Web Technologies
            r'\b(HTML5?|CSS3?|SCSS|Sass|Less|Bootstrap|Tailwind|React|Angular|Vue\.?js|Svelte|Next\.?js|Nuxt\.?js|Gatsby|jQuery|D3\.?js|Three\.?js)\b',
            
            # Backend Frameworks
            r'\b(Node\.?js|Express\.?js|Django|Flask|FastAPI|Spring|Spring Boot|Laravel|Symfony|Ruby on Rails|ASP\.NET|Phoenix|Gin|Echo|Fiber)\b',
            
            # Databases
            r'\b(MySQL|PostgreSQL|MongoDB|Redis|SQLite|Oracle|SQL Server|MariaDB|CouchDB|Neo4j|Elasticsearch|DynamoDB|Cassandra|InfluxDB)\b',
            
            # Cloud & DevOps
            r'\b(AWS|Azure|GCP|Google Cloud|Docker|Kubernetes|Jenkins|GitLab CI|GitHub Actions|Terraform|Ansible|Chef|Puppet|Vagrant|Helm)\b',
            
            # Data Science & ML
            r'\b(Machine Learning|Deep Learning|AI|Data Science|Pandas|NumPy|Scikit-learn|TensorFlow|PyTorch|Keras|OpenCV|NLTK|spaCy|Matplotlib|Seaborn|Plotly)\b',
            
            # Mobile Development
            r'\b(React Native|Flutter|Xamarin|Ionic|Cordova|PhoneGap|Android Studio|Xcode|Swift UI|Jetpack Compose)\b',
            
            # Tools & IDEs
            r'\b(Git|GitHub|GitLab|Bitbucket|SVN|VS Code|IntelliJ|Eclipse|PyCharm|WebStorm|Sublime|Atom|Vim|Emacs|Postman|Insomnia)\b',
            
            # Testing
            r'\b(Jest|Mocha|Chai|Cypress|Selenium|Playwright|JUnit|TestNG|PyTest|Unit Testing|Integration Testing|E2E Testing)\b',
            
            # Methodologies
            r'\b(Agile|Scrum|Kanban|DevOps|CI/CD|TDD|BDD|REST|GraphQL|Microservices|Serverless|API Design)\b',
            
            # Operating Systems
            r'\b(Linux|Ubuntu|CentOS|RHEL|Windows Server|macOS|Unix|FreeBSD|Debian)\b',
            
            # Business Tools
            r'\b(Jira|Confluence|Slack|Microsoft Office|Excel|PowerPoint|Word|Google Workspace|Notion|Figma|Adobe Creative Suite)\b'
        ]
        
        for pattern in tech_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                skill = match.group().strip()
                # Normalize skill name
                skill = re.sub(r'\.?js$', '.js', skill, flags=re.IGNORECASE)  # Normalize .js
                if skill not in skills:
                    skills.append(skill)
        
        # Look for skills sections and extract from lists
        skills_section_patterns = [
            r'(?:skills?|technologies?|tools?|programming|technical|competencies)[\s:]*\n(.*?)(?=\n\s*(?:experience|education|projects|certifications?|awards|achievements)|\Z)',
            r'(?:technical skills?)[\s:]*[:\-]?\s*(.*?)(?=\n\s*[A-Z]|$)'
        ]
        
        for pattern in skills_section_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                skills_text = match.group(1)
                # Extract skills from bullet points or comma-separated lists
                skill_items = re.findall(r'[•·▪▫◦‣⁃-]\s*([^•·▪▫◦‣⁃\n]+)', skills_text)
                if not skill_items:
                    # Try comma-separated
                    skill_items = re.split(r'[,;|]', skills_text)
                
                for item in skill_items:
                    item = item.strip()
                    if len(item) > 2 and len(item) < 50:  # Reasonable skill name length
                        skills.append(item)
        
        return list(set(skills))  # Remove duplicates
    
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
    
    def _extract_education_from_tables(self, tables_data: List[Dict]) -> List[Dict]:
        """Extract education information from table structures"""
        education_entries = []
        
        for table_data in tables_data:
            if not table_data.get("dataframe_dict"):
                continue
                
            # Check if this table contains education data
            headers = [str(h).lower() for h in table_data.get("headers", [])]
            education_keywords = ['education', 'degree', 'university', 'college', 'school', 'qualification', 'academic']
            
            # Check if table contains education-related headers
            has_education_headers = any(keyword in ' '.join(headers) for keyword in education_keywords)
            
            if has_education_headers:
                rows = table_data.get("dataframe_dict", [])
                
                for row in rows:
                    education_entry = self._parse_education_from_row(row, headers)
                    if education_entry:
                        education_entries.append(education_entry)
            
            # Also check rows for education patterns even without education headers
            else:
                rows = table_data.get("dataframe_dict", [])
                for row in rows:
                    row_values = [str(v).strip() for v in row.values() if v and str(v).strip()]
                    row_text = ' '.join(row_values).lower()
                    
                    # Look for degree patterns
                    degree_patterns = [
                        r'\b(bachelor|master|phd|doctorate|diploma|certificate|b\.?s\.?|m\.?s\.?|b\.?a\.?|m\.?a\.?|b\.?tech|m\.?tech)\b',
                        r'\b(undergraduate|graduate|postgraduate)\b'
                    ]
                    
                    has_degree = any(re.search(pattern, row_text) for pattern in degree_patterns)
                    
                    if has_degree:
                        education_entry = self._parse_education_from_row(row, headers)
                        if education_entry:
                            education_entries.append(education_entry)
        
        return education_entries
    
    def _parse_education_from_row(self, row: Dict, headers: List[str]) -> Dict:
        """Parse a single table row to extract education information"""
        education = {
            "degree": "",
            "field": "",
            "institution": "",
            "graduation_date": "",
            "gpa": "",
            "location": ""
        }
        
        # Convert headers to lowercase for matching
        headers_lower = [str(h).lower() for h in headers]
        
        # Map headers to education fields
        header_mappings = {
            'degree': ['degree', 'qualification', 'program', 'course'],
            'field': ['field', 'major', 'specialization', 'subject', 'stream'],
            'institution': ['university', 'college', 'school', 'institution', 'institute'],
            'graduation_date': ['year', 'date', 'graduation', 'completion', 'passed'],
            'gpa': ['gpa', 'grade', 'marks', 'score', 'cgpa'],
            'location': ['location', 'city', 'place']
        }
        
        # Extract information based on header mappings
        for field, keywords in header_mappings.items():
            for i, header in enumerate(headers_lower):
                if any(keyword in header for keyword in keywords):
                    value = list(row.values())[i] if i < len(row.values()) else ""
                    if value and str(value).strip():
                        education[field] = str(value).strip()
                        break
        
        # If no header mapping worked, try to extract from row values using patterns
        row_values = [str(v).strip() for v in row.values() if v and str(v).strip()]
        combined_text = ' '.join(row_values)
        
        # Extract degree using patterns
        if not education["degree"]:
            degree_patterns = [
                r'\b(Bachelor[\'s]?\s+of\s+\w+|B\.?[AS]\.?(?:\s+\w+)?|Bachelor[\'s]?)\b',
                r'\b(Master[\'s]?\s+of\s+\w+|M\.?[AS]\.?(?:\s+\w+)?|Master[\'s]?)\b',
                r'\b(Ph\.?D\.?|Doctor\s+of\s+\w+|Doctorate)\b',
                r'\b(Diploma|Certificate)\b'
            ]
            
            for pattern in degree_patterns:
                match = re.search(pattern, combined_text, re.IGNORECASE)
                if match:
                    education["degree"] = match.group().strip()
                    break
        
        # Extract institution using patterns
        if not education["institution"]:
            words = combined_text.split()
            for i, word in enumerate(words):
                if len(word) > 3 and word[0].isupper():
                    potential_institution = []
                    for j in range(i, min(i + 4, len(words))):
                        if words[j][0].isupper() or words[j].lower() in ['of', 'and', 'the']:
                            potential_institution.append(words[j])
                        else:
                            break
                    
                    if len(potential_institution) >= 2:
                        education["institution"] = ' '.join(potential_institution)
                        break
        
        # Extract year/date patterns
        if not education["graduation_date"]:
            year_pattern = r'\b(19|20)\d{2}\b'
            year_match = re.search(year_pattern, combined_text)
            if year_match:
                education["graduation_date"] = year_match.group()
        
        # Only return if we found meaningful information
        if education["degree"] or education["institution"] or education["field"]:
            return education
        
        return None
    
    def _deduplicate_education(self, education_list: List[Dict]) -> List[Dict]:
        """Remove duplicate education entries"""
        seen = set()
        unique_education = []
        
        for edu in education_list:
            # Create a signature for this education entry
            signature = f"{edu.get('degree', '').lower()}|{edu.get('institution', '').lower()}|{edu.get('field', '').lower()}"
            
            if signature not in seen and any(edu.get(field) for field in ['degree', 'institution', 'field']):
                seen.add(signature)
                unique_education.append(edu)
        
        return unique_education
    
    async def parse_resume_async(self, resume_text: str, tables_data: List[Dict] = None) -> Dict[str, Any]:
        """Parse resume asynchronously using the LangGraph workflow"""
        initial_state = ResumeState(
            raw_text=resume_text,
            cleaned_text="",
            tables_data=tables_data or [],  # Include table data
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
        
        # Prepare result data
        result_data = {
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
        
        # Generate NLP insights
        try:
            insights = self.insights_analyzer.analyze_resume_sync(result_data)
            # Convert CareerInsights dataclass to dictionary for JSON serialization
            if hasattr(insights, '__dict__'):
                insights_dict = {}
                for key, value in insights.__dict__.items():
                    if hasattr(value, '__dict__'):
                        # Nested object, convert to dict
                        insights_dict[key] = value.__dict__
                    else:
                        insights_dict[key] = value
            else:
                insights_dict = insights
                
            result_data["nlp_insights"] = {
                "career_insights": insights_dict,
                "insights_report": self.insights_analyzer.generate_insights_report(insights)
            }
        except Exception as e:
            logger.warning(f"Failed to generate NLP insights: {e}")
            result_data["nlp_insights"] = None
        
        return result_data
    
    def _extract_education_from_text(self, text: str) -> List[Dict]:
        """Extract education from text using enhanced Groq AI prompting with NLP fallback"""
        try:
            # First try AI extraction
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content="""You are an expert at extracting education information from resumes. Extract ALL education entries including:
                - University/College degrees (Bachelor's, Master's, PhD, etc.)
                - High school education
                - Certifications and courses
                - Professional training programs
                - Online courses from platforms like Coursera, edX, etc.
                
                Look for patterns like:
                - Degree names (Bachelor of Science, Master of Arts, PhD, B.Tech, M.Tech, etc.)
                - Institution names (Universities, Colleges, Schools)
                - Graduation years or date ranges
                - Fields of study (Computer Science, Engineering, etc.)
                - GPAs or grades if mentioned
                
                Return ONLY a JSON array of education objects. Even if you find partial information, include it:
                [{
                    "degree": "Bachelor's of Science" or "High School Diploma" or "Certificate" etc.,
                    "field": "Computer Science" or "Mathematics" or subject area,
                    "institution": "University/College/School name",
                    "graduation_date": "YYYY" or "MM/YYYY" or "YYYY-YYYY",
                    "gpa": "GPA/Grade if mentioned or empty string",
                    "location": "City, State if mentioned or empty string"
                }]
                
                Look carefully through the ENTIRE text. Education might be in paragraph form, bullet points, or structured sections.
                If no education found, return empty array []."""),
                HumanMessage(content=f"Text to analyze:\n{text}")
            ])
            
            response = self.llm.invoke(prompt.format_messages())
            education = self._extract_json_from_response(response.content, fallback=[])
            
            if isinstance(education, list) and len(education) > 0:
                return education
            else:
                # If AI extraction fails or returns empty, use NLP fallback
                logger.info("AI extraction failed or returned empty, using NLP fallback")
                return self._extract_education_with_nlp(text)
            
        except Exception as e:
            error_msg = str(e)
            if "invalid_api_key" in error_msg.lower():
                logger.info("Using NLP fallback (no valid Groq API key)")
            else:
                logger.error(f"AI education extraction failed: {e}, using NLP fallback")
            # Fall back to NLP extraction
            return self._extract_education_with_nlp(text)

    def _extract_education_with_nlp(self, text: str) -> List[Dict]:
        """Advanced education extraction using NLP and pattern matching"""
        try:
            education = []
            
            # Split text into lines for better processing
            lines = text.split('\n')
            
            # Find education section
            education_section = []
            in_education = False
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Check if we're entering education section
                if 'EDUCATION' in line.upper():
                    in_education = True
                    education_section.append(line)
                    continue
                
                # If we're in education section, collect relevant lines
                if in_education:
                    # Stop if we hit another major section
                    if any(section in line.upper() for section in ['SKILLS', 'EXPERIENCE', 'PROJECTS', 'CERTIFICATIONS']):
                        break
                    education_section.append(line)
            
            # Join education section for processing
            education_text = ' '.join(education_section)
            
            # Extract degree information using advanced patterns
            degree_info = self._extract_degree_info(education_text)
            
            if degree_info:
                education.append(degree_info)
                
            return education
            
        except Exception as e:
            logger.error(f"NLP education extraction failed: {e}")
            return []
    
    def _extract_degree_info(self, text: str) -> Dict:
        """Extract structured degree information from education text"""
        try:
            # Initialize result
            result = {
                "degree": "",
                "field": "",
                "institution": "",
                "graduation_date": "",
                "gpa": "",
                "location": ""
            }
            
            # Clean and normalize text
            text = ' '.join(text.split())  # Remove extra whitespace
            
            # Extract degree
            degree_patterns = [
                r'Bachelor\s+of\s+Computer\s+Applications\s*\([A-Z]+\)',
                r'Bachelor[\'s]*\s+of\s+[\w\s]+',
                r'Master[\'s]*\s+of\s+[\w\s]+',
                r'B\.?Tech|M\.?Tech|B\.?Sc|M\.?Sc|B\.?A|M\.?A|BCA|MCA|PhD|Doctorate'
            ]
            
            for pattern in degree_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    result["degree"] = match.group(0).strip()
                    break
            
            # Extract field/specialization
            if 'Computer Applications' in text:
                result["field"] = "Computer Applications"
            elif 'Computer Science' in text:
                result["field"] = "Computer Science"
            elif 'Engineering' in text:
                result["field"] = "Engineering"
            
            # Extract institution
            institution_patterns = [
                r'Institute\s+of\s+Engineering\s+and\s+Management',
                r'(University|College|Institute|School)\s+[\w\s,]+?(?=\s*[,\(]|$)'
            ]
            
            for pattern in institution_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    institution = match.group(0).strip()
                    # Clean up institution name
                    result["institution"] = re.sub(r'\s*[,\(].*$', '', institution)
                    break
            
            # Extract graduation date
            year_patterns = [
                r'Expected\s+Graduation[:\s]*(\d{4})',
                r'Graduation[:\s]*(\d{4})',
                r'\(.*?(\d{4})\)',
                r'(\d{4})\s*\)'
            ]
            
            for pattern in year_patterns:
                year_match = re.search(pattern, text, re.IGNORECASE)
                if year_match:
                    year = year_match.group(1)
                    # Validate it's a reasonable year (between 1900 and 2030)
                    if 1900 <= int(year) <= 2030:
                        result["graduation_date"] = year
                        break
            
            # Extract location (city names, avoiding phone numbers)
            location_patterns = [
                r'Institute[^,]*,\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r',\s*(Kolkata|Mumbai|Delhi|Bangalore|Chennai|Hyderabad|Pune|[A-Z][a-z]{3,})',
            ]
            
            for pattern in location_patterns:
                location_match = re.search(pattern, text)
                if location_match:
                    location = location_match.group(1).strip()
                    # Avoid phone numbers and ensure it's a valid city name
                    if not re.search(r'\d{4,}', location) and len(location) > 2:
                        result["location"] = location
                        break
            
            # Only return if we found at least degree or institution
            if result["degree"] or result["institution"]:
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"Degree info extraction failed: {e}")
            return None
    
    def generate_nlp_insights(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive NLP insights from parsed resume data"""
        try:
            insights = self.insights_analyzer.analyze_resume_sync(resume_data)
            # Convert CareerInsights dataclass to dictionary for JSON serialization
            insights_dict = insights.__dict__ if hasattr(insights, '__dict__') else insights
            return {
                "career_insights": insights_dict,
                "insights_report": self.insights_analyzer.generate_insights_report(insights)
            }
        except Exception as e:
            logger.error(f"Error generating NLP insights: {e}")
            return None

    def parse_resume(self, resume_text: str, tables_data: List[Dict] = None) -> ParsedResumeData:
        """Synchronous wrapper for resume parsing"""
        try:
            result = asyncio.run(self.parse_resume_async(resume_text, tables_data))
            
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
                summary=None,
                nlp_insights=result.get("nlp_insights")
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
                summary=None,
                nlp_insights=None
            )


# Factory function for creating parser instance
def create_resume_parser(groq_api_key: str = None) -> LangGraphResumeParser:
    """Create a resume parser instance"""
    if not groq_api_key:
        groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY environment variable is required")
    
    return LangGraphResumeParser(groq_api_key)

