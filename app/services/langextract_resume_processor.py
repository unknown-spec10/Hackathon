"""Enhanced Resume Processor using Google's LangExtract"""

import langextract as lx
import logging
import re
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class ResumeExtraction:
    personal_info: Dict[str, str]
    projects: List[Dict[str, Any]]
    experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    skills: List[str]
    certifications: List[Dict[str, str]]
    raw_extractions: List[Any]

class LangExtractResumeProcessor:
    
    def __init__(self, api_key: str = None, model_id: str = "gemini-2.0-flash-exp"):
        """
        Initialize LangExtract processor
        
        Args:
            api_key: Gemini API key (if not set in environment)
            model_id: Model to use for extraction
        """
        self.api_key = api_key or os.getenv("LANGEXTRACT_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.model_id = model_id
        self.logger = logging.getLogger(__name__)
        
        # Check if API key is available
        if not self.api_key:
            self.logger.warning("No API key found. LangExtract will not work without a valid Gemini API key.")
            self.api_available = False
        else:
            self.api_available = True
            self.logger.info(f"LangExtract initialized with model: {model_id}")
    
    def extract_resume_data(self, text: str) -> ResumeExtraction:
        """
        Extract structured data from resume text using LangExtract
        
        Args:
            text: Resume text content
            
        Returns:
            ResumeExtraction object with structured data
        """
        if not self.api_available:
            self.logger.error("Cannot extract - no API key available")
            return self._create_empty_extraction()
        
        try:
            # Define extraction prompt
            prompt = self._create_extraction_prompt()
            
            # Create examples for few-shot learning
            examples = self._create_extraction_examples()
            
            # Run LangExtract
            self.logger.info(f"Starting LangExtract processing on {len(text)} characters")
            
            result = lx.extract(
                text_or_documents=text,
                prompt_description=prompt,
                examples=examples,
                model_id=self.model_id,
                api_key=self.api_key,
                extraction_passes=2,  # Multiple passes for better recall
                max_workers=5,        # Parallel processing
                max_char_buffer=2000  # Smaller contexts for better accuracy
            )
            
            # Process the extraction results
            extraction = self._process_langextract_results(result, text)
            
            self.logger.info(f"LangExtract completed: {len(extraction.projects)} projects, "
                           f"{len(extraction.experience)} experiences, {len(extraction.skills)} skills")
            
            return extraction
            
        except Exception as e:
            self.logger.error(f"LangExtract processing failed: {e}")
            return self._create_empty_extraction()
    
    def _create_extraction_prompt(self) -> str:
        """Create the extraction prompt for LangExtract"""
        return """
        Extract structured information from this resume/CV text.
        
        Focus on these key areas:
        1. Personal Information: Name, email, phone, LinkedIn, GitHub, location
        2. Projects: Personal, academic, or work projects with descriptions and technologies
        3. Work Experience: Job titles, companies, dates, responsibilities
        4. Education: Degrees, institutions, graduation dates, relevant coursework
        5. Technical Skills: Programming languages, frameworks, tools, technologies
        6. Certifications: Professional certifications, licenses, courses completed
        
        Extract information exactly as written in the text. Do not paraphrase or infer.
        For projects, capture the project name, description, technologies used, and any URLs.
        For experience, capture job titles, company names, employment dates, and key responsibilities.
        For skills, extract specific technical skills, tools, and technologies mentioned.
        
        Maintain precise source grounding - each extraction should correspond to specific text in the resume.
        """
    
    def _create_extraction_examples(self) -> List[lx.data.ExampleData]:
        """Create few-shot examples for LangExtract"""
        examples = [
            lx.data.ExampleData(
                text="""
                DEEP PODDER
                Email: deep.podder@email.com | Phone: +1-234-567-8900
                LinkedIn: linkedin.com/in/deeppodder | GitHub: github.com/deeppodder
                
                PROJECTS
                1. GeneRACT - AI-Powered DNA Analysis Tool
                   ⋄ Built a Retrieval-Augmented Generation (RAG) app using LLaMA models and Ollama
                   ⋄ Technologies: Python, LangChain, Streamlit, Vector Databases
                   ⋄ URL: https://github.com/deeppodder/generact
                
                EXPERIENCE
                Data Scientist | TechCorp Inc. | Jan 2022 - Present
                • Developed machine learning models for customer segmentation
                • Built data pipelines using Python and Apache Spark
                
                EDUCATION
                Master of Science in Computer Science
                Stanford University | 2020-2022
                
                SKILLS
                Python, JavaScript, React, TensorFlow, PyTorch, AWS, Docker
                """,
                extractions=[
                    # Personal Information
                    lx.data.Extraction(
                        extraction_class="personal_info",
                        extraction_text="DEEP PODDER",
                        attributes={"type": "name"}
                    ),
                    lx.data.Extraction(
                        extraction_class="personal_info",
                        extraction_text="deep.podder@email.com",
                        attributes={"type": "email"}
                    ),
                    lx.data.Extraction(
                        extraction_class="personal_info",
                        extraction_text="+1-234-567-8900",
                        attributes={"type": "phone"}
                    ),
                    lx.data.Extraction(
                        extraction_class="personal_info",
                        extraction_text="linkedin.com/in/deeppodder",
                        attributes={"type": "linkedin"}
                    ),
                    lx.data.Extraction(
                        extraction_class="personal_info",
                        extraction_text="github.com/deeppodder",
                        attributes={"type": "github"}
                    ),
                    
                    # Projects
                    lx.data.Extraction(
                        extraction_class="project",
                        extraction_text="GeneRACT - AI-Powered DNA Analysis Tool",
                        attributes={
                            "type": "project_title",
                            "name": "GeneRACT",
                            "description": "AI-Powered DNA Analysis Tool"
                        }
                    ),
                    lx.data.Extraction(
                        extraction_class="project",
                        extraction_text="Built a Retrieval-Augmented Generation (RAG) app using LLaMA models and Ollama",
                        attributes={
                            "type": "project_description",
                            "project": "GeneRACT"
                        }
                    ),
                    lx.data.Extraction(
                        extraction_class="project",
                        extraction_text="Python, LangChain, Streamlit, Vector Databases",
                        attributes={
                            "type": "project_technologies",
                            "project": "GeneRACT"
                        }
                    ),
                    lx.data.Extraction(
                        extraction_class="project",
                        extraction_text="https://github.com/deeppodder/generact",
                        attributes={
                            "type": "project_url",
                            "project": "GeneRACT"
                        }
                    ),
                    
                    # Experience
                    lx.data.Extraction(
                        extraction_class="experience",
                        extraction_text="Data Scientist",
                        attributes={
                            "type": "job_title",
                            "company": "TechCorp Inc."
                        }
                    ),
                    lx.data.Extraction(
                        extraction_class="experience",
                        extraction_text="TechCorp Inc.",
                        attributes={
                            "type": "company",
                            "job_title": "Data Scientist"
                        }
                    ),
                    lx.data.Extraction(
                        extraction_class="experience",
                        extraction_text="Jan 2022 - Present",
                        attributes={
                            "type": "employment_duration",
                            "job_title": "Data Scientist",
                            "company": "TechCorp Inc."
                        }
                    ),
                    lx.data.Extraction(
                        extraction_class="experience",
                        extraction_text="Developed machine learning models for customer segmentation",
                        attributes={
                            "type": "responsibility",
                            "job_title": "Data Scientist",
                            "company": "TechCorp Inc."
                        }
                    ),
                    
                    # Education
                    lx.data.Extraction(
                        extraction_class="education",
                        extraction_text="Master of Science in Computer Science",
                        attributes={
                            "type": "degree",
                            "institution": "Stanford University"
                        }
                    ),
                    lx.data.Extraction(
                        extraction_class="education",
                        extraction_text="Stanford University",
                        attributes={
                            "type": "institution",
                            "degree": "Master of Science in Computer Science"
                        }
                    ),
                    lx.data.Extraction(
                        extraction_class="education",
                        extraction_text="2020-2022",
                        attributes={
                            "type": "graduation_period",
                            "degree": "Master of Science in Computer Science",
                            "institution": "Stanford University"
                        }
                    ),
                    
                    # Skills
                    lx.data.Extraction(
                        extraction_class="skill",
                        extraction_text="Python",
                        attributes={"type": "programming_language"}
                    ),
                    lx.data.Extraction(
                        extraction_class="skill",
                        extraction_text="JavaScript",
                        attributes={"type": "programming_language"}
                    ),
                    lx.data.Extraction(
                        extraction_class="skill",
                        extraction_text="React",
                        attributes={"type": "framework"}
                    ),
                    lx.data.Extraction(
                        extraction_class="skill",
                        extraction_text="TensorFlow",
                        attributes={"type": "ml_framework"}
                    ),
                    lx.data.Extraction(
                        extraction_class="skill",
                        extraction_text="AWS",
                        attributes={"type": "cloud_platform"}
                    ),
                ]
            )
        ]
        
        return examples
    
    def _process_langextract_results(self, result, original_text: str) -> ResumeExtraction:
        """Process LangExtract results into structured format"""
        
        # Get extractions from result
        if hasattr(result, 'extractions'):
            extractions = result.extractions
        elif hasattr(result, 'data') and hasattr(result.data, 'extractions'):
            extractions = result.data.extractions
        else:
            # Handle different result formats
            extractions = getattr(result, 'extractions', [])
        
        self.logger.info(f"Processing {len(extractions)} extractions from LangExtract")
        
        # Initialize structured data
        personal_info = {}
        projects = []
        experience = []
        education = []
        skills = []
        certifications = []
        
        # Group extractions by type
        current_project = None
        current_experience = None
        current_education = None
        
        for extraction in extractions:
            extraction_class = getattr(extraction, 'extraction_class', '')
            extraction_text = getattr(extraction, 'extraction_text', '')
            attributes = getattr(extraction, 'attributes', {})
            
            if extraction_class == 'personal_info':
                attr_type = attributes.get('type', 'unknown')
                if attr_type in ['name', 'email', 'phone', 'linkedin', 'github', 'location']:
                    personal_info[attr_type] = extraction_text
            
            elif extraction_class == 'project':
                attr_type = attributes.get('type', 'unknown')
                project_name = attributes.get('project', attributes.get('name', ''))
                
                if attr_type == 'project_title':
                    # Start new project
                    current_project = {
                        'name': attributes.get('name', extraction_text.split(' - ')[0] if ' - ' in extraction_text else extraction_text),
                        'description': attributes.get('description', extraction_text),
                        'technologies': [],
                        'url': '',
                        'duration': ''
                    }
                    projects.append(current_project)
                elif current_project:
                    if attr_type == 'project_description':
                        current_project['description'] += '. ' + extraction_text
                    elif attr_type == 'project_technologies':
                        techs = [tech.strip() for tech in extraction_text.split(',')]
                        current_project['technologies'].extend(techs)
                    elif attr_type == 'project_url':
                        current_project['url'] = extraction_text
            
            elif extraction_class == 'experience':
                attr_type = attributes.get('type', 'unknown')
                
                if attr_type == 'job_title':
                    # Start new experience
                    current_experience = {
                        'title': extraction_text,
                        'company': attributes.get('company', ''),
                        'duration': '',
                        'description': '',
                        'responsibilities': []
                    }
                    experience.append(current_experience)
                elif current_experience:
                    if attr_type == 'company':
                        current_experience['company'] = extraction_text
                    elif attr_type == 'employment_duration':
                        current_experience['duration'] = extraction_text
                    elif attr_type == 'responsibility':
                        current_experience['responsibilities'].append(extraction_text)
                        if current_experience['description']:
                            current_experience['description'] += '. ' + extraction_text
                        else:
                            current_experience['description'] = extraction_text
            
            elif extraction_class == 'education':
                attr_type = attributes.get('type', 'unknown')
                
                if attr_type == 'degree':
                    # Start new education
                    current_education = {
                        'degree': extraction_text,
                        'institution': attributes.get('institution', ''),
                        'year': '',
                        'details': ''
                    }
                    education.append(current_education)
                elif current_education:
                    if attr_type == 'institution':
                        current_education['institution'] = extraction_text
                    elif attr_type == 'graduation_period':
                        current_education['year'] = extraction_text
            
            elif extraction_class == 'skill':
                if extraction_text not in skills:
                    skills.append(extraction_text)
            
            elif extraction_class == 'certification':
                certifications.append({
                    'name': extraction_text,
                    'issuer': attributes.get('issuer', ''),
                    'year': attributes.get('year', '')
                })
        
        # Create final extraction object
        return ResumeExtraction(
            personal_info=personal_info,
            projects=projects,
            experience=experience,
            education=education,
            skills=skills,
            certifications=certifications,
            raw_extractions=extractions
        )
    
    def _create_empty_extraction(self) -> ResumeExtraction:
        """Create empty extraction result for fallback"""
        return ResumeExtraction(
            personal_info={},
            projects=[],
            experience=[],
            education=[],
            skills=[],
            certifications=[],
            raw_extractions=[]
        )
    
    def save_extraction_visualization(self, result, output_path: str = "resume_extraction.html"):
        """Save LangExtract visualization for debugging and review"""
        try:
            # Save JSONL file
            jsonl_path = output_path.replace('.html', '.jsonl')
            lx.io.save_annotated_documents([result], 
                                         output_name=jsonl_path.split('/')[-1].replace('.jsonl', ''), 
                                         output_dir=os.path.dirname(jsonl_path) or '.')
            
            # Generate HTML visualization
            html_content = lx.visualize(jsonl_path)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                if hasattr(html_content, 'data'):
                    f.write(html_content.data)
                else:
                    f.write(html_content)
            
            self.logger.info(f"Extraction visualization saved to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save visualization: {e}")
            return False

# Factory function
def create_langextract_processor(api_key: str = None) -> LangExtractResumeProcessor:
    """Create a LangExtract resume processor instance"""
    return LangExtractResumeProcessor(api_key=api_key)
