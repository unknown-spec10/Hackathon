import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, func
import json
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models.job import Job
from app.models.resume import JobRecommendation
from app.schemas.resume_schema import JobRecommendationResponse, ParsedResumeData


logger = logging.getLogger(__name__)


class JobRecommender:
    """Advanced job recommendation system using skills matching and ML techniques"""
    
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        
    def get_recommendations(
        self, 
        parsed_resume: Dict[str, Any], 
        jobs_list: List[Job] = None,
        db: Session = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get job recommendations based on parsed resume data
        
        Args:
            parsed_resume: Parsed resume data from LangGraph
            jobs_list: List of jobs to evaluate (if provided, used instead of db query)
            db: Database session (optional if jobs_list is provided)
            limit: Maximum number of recommendations
            
        Returns:
            List of job recommendations with match scores in dictionary format
        """
        try:
            # Extract candidate profile
            candidate_profile = self._extract_candidate_profile(parsed_resume)
            
            # Get jobs list
            if jobs_list is not None:
                jobs = jobs_list
            elif db is not None:
                # Get all active jobs (use application_deadline to filter active jobs)
                from datetime import date
                current_date = date.today()
                jobs = db.query(Job).filter(Job.application_deadline >= current_date).all()
            else:
                raise ValueError("Either jobs_list or db must be provided")
            
            if not jobs:
                return []
            
            # Calculate match scores for all jobs
            job_scores = []
            for job in jobs:
                match_score, matching_skills, skill_gaps, reason = self._calculate_job_match(
                    candidate_profile, job
                )
                
                if match_score > 0.1:  # Only include jobs with decent match
                    job_scores.append({
                        'job': job,
                        'score': match_score,
                        'match_score': match_score,
                        'matching_skills': matching_skills,
                        'skill_gaps': skill_gaps,
                        'reasons': [reason],
                        'recommendation_reason': reason
                    })
            
            # Sort by match score
            job_scores.sort(key=lambda x: x['score'], reverse=True)
            
            return job_scores[:limit]
            
        except Exception as e:
            logger.error(f"Error getting job recommendations: {e}")
            return []
    
    def _extract_candidate_profile(self, parsed_resume: Dict[str, Any]) -> Dict[str, Any]:
        """Extract candidate profile from parsed resume"""
        profile = {
            'skills': [],
            'experience_years': 0,
            'education_level': '',
            'industries': [],
            'job_titles': [],
            'technologies': [],
            'certifications': [],
            'experience_descriptions': [],
            'summary': ''
        }
        
        # Extract skills (ensure they are strings and not None)
        skills = parsed_resume.get('skills', [])
        profile['skills'] = [str(skill) for skill in skills if skill is not None] if skills else []
        
        # Extract experience data
        experience = parsed_resume.get('experience', [])
        if experience:
            # Calculate total experience years
            current_year = 2025  # Current year
            years_exp = []
            
            for exp in experience:
                try:
                    start_year = self._extract_year(exp.get('start_date', ''))
                    end_year = self._extract_year(exp.get('end_date', '')) or current_year
                    
                    if start_year and end_year:
                        years_exp.append(end_year - start_year)
                        
                    # Extract job titles and descriptions
                    if exp.get('title') is not None:
                        profile['job_titles'].append(str(exp['title']).lower())
                    
                    if exp.get('description') is not None:
                        profile['experience_descriptions'].append(str(exp['description']))
                        
                except:
                    continue
            
            profile['experience_years'] = max(years_exp) if years_exp else 0
        
        # Extract education level
        education = parsed_resume.get('education', [])
        if education:
            degrees = [
                str(edu.get('degree', '')).lower() 
                for edu in education 
                if edu and edu.get('degree') is not None
            ]
            if any('phd' in deg or 'doctorate' in deg for deg in degrees):
                profile['education_level'] = 'doctorate'
            elif any('master' in deg or 'mba' in deg or 'ms' in deg or 'ma' in deg for deg in degrees):
                profile['education_level'] = 'masters'
            elif any('bachelor' in deg or 'bs' in deg or 'ba' in deg or 'be' in deg for deg in degrees):
                profile['education_level'] = 'bachelors'
            else:
                profile['education_level'] = 'other'
        
        # Extract certifications
        certifications = parsed_resume.get('certifications', [])
        if certifications:
            profile['certifications'] = [
                str(cert.get('name', '')) for cert in certifications 
                if cert and cert.get('name') is not None
            ]
        else:
            profile['certifications'] = []
        
        # Extract summary
        profile['summary'] = parsed_resume.get('summary', '')
        
        # Identify technologies from skills and experience
        tech_keywords = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node',
            'sql', 'mongodb', 'postgresql', 'mysql', 'aws', 'azure', 'gcp',
            'docker', 'kubernetes', 'jenkins', 'git', 'linux', 'windows',
            'machine learning', 'ai', 'data science', 'tensorflow', 'pytorch',
            'hadoop', 'spark', 'kafka', 'redis', 'elasticsearch'
        ]
        
        all_text = ' '.join([
            ' '.join(profile['skills']),
            ' '.join(profile['experience_descriptions']),
            profile['summary']
        ]).lower()
        
        profile['technologies'] = [tech for tech in tech_keywords if tech in all_text]
        
        return profile
    
    def _calculate_job_match(
        self, 
        candidate_profile: Dict[str, Any], 
        job: Job
    ) -> tuple[float, List[str], List[str], str]:
        """
        Calculate match score between candidate and job
        
        Returns:
            (match_score, matching_skills, skill_gaps, recommendation_reason)
        """
        try:
            # Parse job requirements
            job_requirements = self._parse_job_requirements(job)
            
            # Skills matching
            skills_score, matching_skills, skill_gaps = self._calculate_skills_match(
                candidate_profile['skills'], 
                job_requirements['required_skills']
            )
            
            # Experience level matching
            experience_score = self._calculate_experience_match(
                candidate_profile['experience_years'],
                job_requirements['min_experience'],
                job_requirements['max_experience']
            )
            
            # Education matching
            education_score = self._calculate_education_match(
                candidate_profile['education_level'],
                job_requirements['education_level']
            )
            
            # Technology matching
            tech_score = self._calculate_technology_match(
                candidate_profile['technologies'],
                job_requirements['technologies']
            )
            
            # Text similarity (job description vs candidate experience)
            text_score = self._calculate_text_similarity(
                candidate_profile['experience_descriptions'] + [candidate_profile['summary']],
                [job.responsibilities or "", job.title or ""]  # Handle None values properly
            )
            
            # Calculate weighted overall score
            overall_score = (
                skills_score * 0.35 +      # Skills are most important
                experience_score * 0.25 +   # Experience level
                tech_score * 0.20 +         # Technology match
                text_score * 0.15 +         # Text similarity
                education_score * 0.05      # Education (least weight)
            )
            
            # Generate recommendation reason
            reason = self._generate_recommendation_reason(
                skills_score, experience_score, education_score, 
                tech_score, text_score, matching_skills
            )
            
            return overall_score, matching_skills, skill_gaps, reason
            
        except Exception as e:
            logger.error(f"Error calculating job match: {e}")
            return 0.0, [], [], "Error calculating match"
    
    def _parse_job_requirements(self, job: Job) -> Dict[str, Any]:
        """Parse job requirements from job object"""
        requirements = {
            'required_skills': [],
            'min_experience': 0,
            'max_experience': 20,
            'education_level': 'bachelors',
            'technologies': []
        }
        
        # Extract skills from job responsibilities and skills_required (handle None values)
        responsibilities_text = job.responsibilities or ''
        
        # Handle skills_required which can be None, list, or other types
        if job.skills_required:
            if isinstance(job.skills_required, list):
                # Filter out None values from the list
                skills_list = [str(skill) for skill in job.skills_required if skill is not None]
                skills_text = ' '.join(skills_list)
            else:
                skills_text = str(job.skills_required)
        else:
            skills_text = ''
            
        job_text = f"{responsibilities_text} {skills_text}".lower()
        
        # Common skill patterns
        skill_patterns = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js',
            'sql', 'mongodb', 'postgresql', 'mysql', 'aws', 'azure', 'gcp',
            'docker', 'kubernetes', 'jenkins', 'git', 'linux', 'windows',
            'machine learning', 'artificial intelligence', 'data science',
            'tensorflow', 'pytorch', 'hadoop', 'spark', 'kafka', 'redis',
            'html', 'css', 'bootstrap', 'jquery', 'php', 'ruby', 'c++', 'c#',
            'swift', 'kotlin', 'flutter', 'react native', 'django', 'flask',
            'spring', 'express', 'laravel', 'rails', 'asp.net', 'xamarin'
        ]
        
        found_skills = [skill for skill in skill_patterns if skill in job_text]
        requirements['required_skills'] = found_skills
        requirements['technologies'] = found_skills
        
        # Extract experience requirements
        import re
        exp_pattern = r'(\d+)\s*(?:\+|\-|to|\-\s*\d+)?\s*years?\s*(?:of\s*)?(?:experience|exp)'
        exp_matches = re.findall(exp_pattern, job_text, re.IGNORECASE)
        
        if exp_matches:
            try:
                min_exp = min([int(match) for match in exp_matches])
                max_exp = max([int(match) for match in exp_matches])
                requirements['min_experience'] = min_exp
                requirements['max_experience'] = max_exp
            except:
                pass
        
        # Extract education requirements
        if any(word in job_text for word in ['phd', 'doctorate', 'ph.d']):
            requirements['education_level'] = 'doctorate'
        elif any(word in job_text for word in ['master', 'mba', 'ms', 'ma']):
            requirements['education_level'] = 'masters'
        elif any(word in job_text for word in ['bachelor', 'bs', 'ba', 'be']):
            requirements['education_level'] = 'bachelors'
        
        return requirements
    
    def _calculate_skills_match(
        self, 
        candidate_skills: List[str], 
        job_skills: List[str]
    ) -> tuple[float, List[str], List[str]]:
        """Calculate skills matching score"""
        if not job_skills:
            return 0.5, [], []
        
        candidate_skills_lower = [skill.lower() for skill in candidate_skills]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        # Find exact matches
        exact_matches = set(candidate_skills_lower) & set(job_skills_lower)
        
        # Find partial matches (substring matching)
        partial_matches = set()
        for job_skill in job_skills_lower:
            for candidate_skill in candidate_skills_lower:
                if (job_skill in candidate_skill or candidate_skill in job_skill) and \
                   len(job_skill) > 2 and len(candidate_skill) > 2:
                    partial_matches.add(job_skill)
        
        # Calculate score
        total_matches = len(exact_matches) + (len(partial_matches) * 0.5)
        score = min(total_matches / len(job_skills), 1.0)
        
        # Get matching skills (preserving original case)
        matching_skills = []
        for skill in candidate_skills:
            if skill.lower() in exact_matches or \
               any(skill.lower() in pm or pm in skill.lower() for pm in partial_matches):
                matching_skills.append(skill)
        
        # Get skill gaps
        skill_gaps = []
        for job_skill in job_skills:
            if job_skill.lower() not in exact_matches and \
               not any(job_skill.lower() in cs or cs in job_skill.lower() 
                      for cs in candidate_skills_lower):
                skill_gaps.append(job_skill)
        
        return score, matching_skills, skill_gaps
    
    def _calculate_experience_match(
        self, 
        candidate_years: int, 
        min_required: int, 
        max_required: int
    ) -> float:
        """Calculate experience level matching score"""
        if candidate_years >= min_required and candidate_years <= max_required:
            return 1.0
        elif candidate_years < min_required:
            # Penalize lack of experience more heavily
            gap = min_required - candidate_years
            return max(0.0, 1.0 - (gap * 0.2))
        else:
            # Over-qualified is less of a penalty
            excess = candidate_years - max_required
            return max(0.7, 1.0 - (excess * 0.05))
    
    def _calculate_education_match(
        self, 
        candidate_education: str, 
        required_education: str
    ) -> float:
        """Calculate education level matching score"""
        education_hierarchy = {
            'doctorate': 4,
            'masters': 3,
            'bachelors': 2,
            'other': 1
        }
        
        candidate_level = education_hierarchy.get(candidate_education, 1)
        required_level = education_hierarchy.get(required_education, 2)
        
        if candidate_level >= required_level:
            return 1.0
        else:
            # Partial credit for lower education
            return max(0.3, candidate_level / required_level)
    
    def _calculate_technology_match(
        self, 
        candidate_technologies: List[str], 
        job_technologies: List[str]
    ) -> float:
        """Calculate technology matching score"""
        if not job_technologies:
            return 0.5
        
        candidate_tech_lower = [tech.lower() for tech in candidate_technologies]
        job_tech_lower = [tech.lower() for tech in job_technologies]
        
        matches = len(set(candidate_tech_lower) & set(job_tech_lower))
        return min(matches / len(job_tech_lower), 1.0)
    
    def _calculate_text_similarity(
        self, 
        candidate_texts: List[str], 
        job_texts: List[str]
    ) -> float:
        """Calculate text similarity using TF-IDF and cosine similarity"""
        try:
            # Filter out None values and convert to strings
            candidate_text = ' '.join([str(text) for text in candidate_texts if text is not None and str(text).strip()])
            job_text = ' '.join([str(text) for text in job_texts if text is not None and str(text).strip()])
            
            if not candidate_text or not job_text:
                return 0.0
            
            # Create TF-IDF vectors
            texts = [candidate_text, job_text]
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return similarity
            
        except Exception as e:
            logger.error(f"Error in text similarity calculation: {e}")
            return 0.0
    
    def _generate_recommendation_reason(
        self,
        skills_score: float,
        experience_score: float,
        education_score: float,
        tech_score: float,
        text_score: float,
        matching_skills: List[str]
    ) -> str:
        """Generate human-readable recommendation reason"""
        reasons = []
        
        if skills_score > 0.7:
            reasons.append(f"Strong skills match ({len(matching_skills)} matching skills)")
        elif skills_score > 0.4:
            reasons.append(f"Good skills match ({len(matching_skills)} matching skills)")
        
        if experience_score > 0.8:
            reasons.append("Experience level aligns well")
        elif experience_score < 0.5:
            reasons.append("May need additional experience")
        
        if tech_score > 0.6:
            reasons.append("Good technology stack match")
        
        if education_score > 0.8:
            reasons.append("Education requirements met")
        
        if text_score > 0.3:
            reasons.append("Experience description matches job requirements")
        
        if not reasons:
            reasons.append("Basic qualifications match")
        
        return "; ".join(reasons)
    
    def _extract_year(self, date_str: str) -> Optional[int]:
        """Extract year from date string"""
        if not date_str:
            return None
        
        try:
            import re
            year_match = re.search(r'\b(19|20)\d{2}\b', str(date_str))
            if year_match:
                return int(year_match.group())
        except:
            pass
        
        return None
    
    def save_recommendations(
        self, 
        resume_id: int, 
        recommendations: List[JobRecommendationResponse],
        db: Session
    ) -> None:
        """Save recommendations to database"""
        try:
            # Clear existing recommendations for this resume
            db.query(JobRecommendation).filter(
                JobRecommendation.resume_id == resume_id
            ).delete()
            
            # Save new recommendations
            for rec in recommendations:
                job_rec = JobRecommendation(
                    resume_id=resume_id,
                    job_id=rec.job_id,
                    match_score=rec.match_score,
                    matching_skills=rec.matching_skills,
                    skill_gaps=rec.skill_gaps,
                    recommendation_reason=rec.recommendation_reason
                )
                db.add(job_rec)
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error saving recommendations: {e}")
            db.rollback()
