import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from collections import Counter
import json

from app.models.course import Course
from app.models.resume import CourseRecommendation
from app.schemas.resume_schema import CourseRecommendationResponse, ParsedResumeData


logger = logging.getLogger(__name__)


class CourseRecommender:
    """Course recommendation system for skill development and career advancement"""
    
    def __init__(self):
        # Industry skill requirements mapping
        self.industry_skills = {
            'software_development': [
                'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js',
                'sql', 'mongodb', 'postgresql', 'git', 'docker', 'kubernetes',
                'aws', 'azure', 'gcp', 'machine learning', 'data structures',
                'algorithms', 'system design', 'agile', 'scrum'
            ],
            'data_science': [
                'python', 'r', 'sql', 'machine learning', 'deep learning',
                'tensorflow', 'pytorch', 'pandas', 'numpy', 'matplotlib',
                'tableau', 'power bi', 'hadoop', 'spark', 'kafka',
                'statistics', 'data visualization', 'big data'
            ],
            'devops': [
                'docker', 'kubernetes', 'jenkins', 'git', 'aws', 'azure',
                'terraform', 'ansible', 'linux', 'bash', 'python',
                'monitoring', 'ci/cd', 'infrastructure as code'
            ],
            'cybersecurity': [
                'network security', 'penetration testing', 'ethical hacking',
                'cissp', 'ceh', 'security+', 'firewall', 'intrusion detection',
                'risk assessment', 'compliance', 'incident response'
            ],
            'web_development': [
                'html', 'css', 'javascript', 'react', 'angular', 'vue',
                'php', 'python', 'node.js', 'sql', 'mongodb', 'git',
                'responsive design', 'web accessibility', 'seo'
            ],
            'mobile_development': [
                'swift', 'kotlin', 'flutter', 'react native', 'xamarin',
                'ios development', 'android development', 'mobile ui/ux',
                'app store optimization', 'mobile testing'
            ],
            'cloud_computing': [
                'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
                'serverless', 'microservices', 'cloud architecture',
                'cloud security', 'devops', 'ci/cd'
            ],
            'ai_ml': [
                'machine learning', 'deep learning', 'neural networks',
                'tensorflow', 'pytorch', 'python', 'r', 'statistics',
                'computer vision', 'nlp', 'reinforcement learning'
            ]
        }
        
        # Career progression paths
        self.career_paths = {
            'junior_developer': ['software_development', 'web_development'],
            'senior_developer': ['software_development', 'cloud_computing', 'devops'],
            'data_analyst': ['data_science', 'ai_ml'],
            'data_scientist': ['data_science', 'ai_ml', 'cloud_computing'],
            'devops_engineer': ['devops', 'cloud_computing', 'cybersecurity'],
            'security_analyst': ['cybersecurity', 'devops'],
            'mobile_developer': ['mobile_development', 'cloud_computing'],
            'full_stack_developer': ['web_development', 'software_development', 'cloud_computing']
        }
    
    def get_recommendations(
        self, 
        parsed_resume: Dict[str, Any], 
        courses_list: List[Course] = None,
        db: Session = None,
        limit: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Get course recommendations based on parsed resume data
        
        Args:
            parsed_resume: Parsed resume data from LangGraph
            courses_list: List of courses to evaluate (if provided, used instead of db query)
            db: Database session (optional if courses_list is provided)
            limit: Maximum number of recommendations
            
        Returns:
            List of course recommendations with relevance scores in dictionary format
        """
        try:
            # Analyze candidate profile
            candidate_analysis = self._analyze_candidate_profile(parsed_resume)
            
            # Get courses list
            if courses_list is not None:
                courses = courses_list
            elif db is not None:
                # Get all available courses
                courses = db.query(Course).all()  # Remove is_active filter since Course model doesn't have it
            else:
                raise ValueError("Either courses_list or db must be provided")
            
            if not courses:
                return []
            
            # Calculate course relevance scores
            course_scores = []
            for course in courses:
                relevance_score, skill_gaps, career_impact = self._calculate_course_relevance(
                    candidate_analysis, course
                )
                
                if relevance_score > 0.1:  # Only include relevant courses
                    course_scores.append({
                        'course': course,
                        'score': relevance_score,
                        'relevance_score': relevance_score,
                        'skill_gaps_addressed': skill_gaps,
                        'career_impact': career_impact,
                        'reasons': [career_impact]
                    })
            
            # Sort by relevance score
            course_scores.sort(key=lambda x: x['score'], reverse=True)
            
            return course_scores[:limit]
            
        except Exception as e:
            logger.error(f"Error getting course recommendations: {e}")
            return []
    
    def _analyze_candidate_profile(self, parsed_resume: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze candidate profile to identify strengths and gaps"""
        analysis = {
            'current_skills': [],
            'experience_level': 'entry',
            'career_focus': [],
            'skill_gaps': [],
            'learning_priorities': [],
            'industries': []
        }
        
        # Extract current skills
        analysis['current_skills'] = [skill.lower() for skill in parsed_resume.get('skills', [])]
        
        # Determine experience level
        experience = parsed_resume.get('experience', [])
        if experience:
            total_years = self._calculate_total_experience(experience)
            if total_years >= 5:
                analysis['experience_level'] = 'senior'
            elif total_years >= 2:
                analysis['experience_level'] = 'mid'
            else:
                analysis['experience_level'] = 'entry'
        
        # Identify career focus areas
        analysis['career_focus'] = self._identify_career_focus(analysis['current_skills'])
        
        # Identify skill gaps
        analysis['skill_gaps'] = self._identify_skill_gaps(
            analysis['current_skills'], 
            analysis['career_focus']
        )
        
        # Determine learning priorities
        analysis['learning_priorities'] = self._determine_learning_priorities(
            analysis['experience_level'],
            analysis['career_focus'],
            analysis['skill_gaps']
        )
        
        return analysis
    
    def _calculate_course_relevance(
        self, 
        candidate_analysis: Dict[str, Any], 
        course: Course
    ) -> tuple[float, List[str], str]:
        """
        Calculate how relevant a course is for the candidate
        
        Returns:
            (relevance_score, skill_gaps_addressed, career_impact)
        """
        try:
            course_skills = self._extract_course_skills(course)
            
            # Calculate different relevance factors
            skill_gap_score = self._calculate_skill_gap_coverage(
                candidate_analysis['skill_gaps'], 
                course_skills
            )
            
            # For course category, try to infer from course name/description since Course model doesn't have category
            course_category = self._infer_course_category(course)
            
            career_alignment_score = self._calculate_career_alignment(
                candidate_analysis['career_focus'],
                course_skills,
                course_category
            )
            
            # Since Course model doesn't have difficulty_level, we'll use a default score
            experience_appropriateness = self._calculate_experience_appropriateness(
                candidate_analysis['experience_level'],
                None  # No difficulty level available
            )
            
            learning_priority_score = self._calculate_learning_priority_match(
                candidate_analysis['learning_priorities'],
                course_skills,
                course_category
            )
            
            # Calculate weighted overall relevance score
            relevance_score = (
                skill_gap_score * 0.35 +          # Most important: addresses skill gaps
                career_alignment_score * 0.30 +    # Career path alignment
                learning_priority_score * 0.20 +   # Learning priorities
                experience_appropriateness * 0.15  # Appropriate difficulty
            )
            
            # Identify which skill gaps this course addresses
            skill_gaps_addressed = []
            for gap in candidate_analysis['skill_gaps']:
                if any(gap.lower() in skill.lower() or skill.lower() in gap.lower() 
                       for skill in course_skills):
                    skill_gaps_addressed.append(gap)
            
            # Generate career impact description
            career_impact = self._generate_career_impact(
                course, candidate_analysis['career_focus'], 
                candidate_analysis['experience_level']
            )
            
            return relevance_score, skill_gaps_addressed, career_impact
            
        except Exception as e:
            logger.error(f"Error calculating course relevance: {e}")
            return 0.0, [], "Unable to assess career impact"
    
    def _extract_course_skills(self, course: Course) -> List[str]:
        """Extract skills taught in the course"""
        course_text = f"{course.name} {course.description}".lower()
        
        # Common technical skills
        all_skills = []
        for industry_skills in self.industry_skills.values():
            all_skills.extend(industry_skills)
        
        # Find skills mentioned in course content
        found_skills = []
        for skill in set(all_skills):
            if skill.lower() in course_text:
                found_skills.append(skill)
        
        # Also extract from skills_required field if it exists
        try:
            if hasattr(course, 'skills_required') and course.skills_required:
                if isinstance(course.skills_required, str):
                    # Try to parse as JSON
                    try:
                        skills_list = json.loads(course.skills_required)
                        if isinstance(skills_list, list):
                            found_skills.extend([skill.lower() for skill in skills_list])
                    except:
                        # If not JSON, treat as comma-separated
                        skills_list = course.skills_required.split(',')
                        found_skills.extend([skill.strip().lower() for skill in skills_list])
                elif isinstance(course.skills_required, list):
                    found_skills.extend([skill.lower() for skill in course.skills_required])
        except:
            pass
        
        return list(set(found_skills))
    
    def _infer_course_category(self, course: Course) -> str:
        """Infer course category from name and description"""
        course_text = f"{course.name} {course.description}".lower()
        
        # Category keywords mapping
        category_keywords = {
            'programming': ['programming', 'coding', 'software', 'development'],
            'data science': ['data', 'analytics', 'machine learning', 'ai', 'statistics'],
            'web development': ['web', 'frontend', 'backend', 'html', 'css', 'javascript'],
            'cloud': ['cloud', 'aws', 'azure', 'gcp', 'devops'],
            'cybersecurity': ['security', 'cyber', 'ethical hacking', 'penetration'],
            'mobile': ['mobile', 'android', 'ios', 'app development'],
            'business': ['business', 'management', 'leadership', 'marketing'],
            'design': ['design', 'ui', 'ux', 'graphic']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in course_text for keyword in keywords):
                return category
        
        return 'general'
    
    def _calculate_skill_gap_coverage(
        self, 
        candidate_gaps: List[str], 
        course_skills: List[str]
    ) -> float:
        """Calculate how well the course covers candidate's skill gaps"""
        if not candidate_gaps:
            return 0.3  # Neutral score if no gaps identified
        
        gaps_covered = 0
        for gap in candidate_gaps:
            if any(gap.lower() in skill or skill in gap.lower() for skill in course_skills):
                gaps_covered += 1
        
        return min(gaps_covered / len(candidate_gaps), 1.0)
    
    def _calculate_career_alignment(
        self, 
        career_focus: List[str], 
        course_skills: List[str],
        course_category: str
    ) -> float:
        """Calculate alignment with candidate's career focus"""
        if not career_focus:
            return 0.5  # Neutral if no clear focus
        
        alignment_score = 0
        
        # Check if course category aligns with career focus
        if course_category:
            category_lower = course_category.lower()
            for focus in career_focus:
                if focus in category_lower or category_lower in focus:
                    alignment_score += 0.5
        
        # Check skill alignment
        for focus in career_focus:
            if focus in self.industry_skills:
                focus_skills = self.industry_skills[focus]
                skill_matches = len(set(course_skills) & set(focus_skills))
                if focus_skills:
                    alignment_score += (skill_matches / len(focus_skills)) * 0.5
        
        return min(alignment_score, 1.0)
    
    def _calculate_experience_appropriateness(
        self, 
        experience_level: str, 
        course_difficulty: str = None
    ) -> float:
        """Calculate if course difficulty matches experience level"""
        if not course_difficulty:
            return 0.7  # Neutral if difficulty not specified
        
        difficulty_mapping = {
            'beginner': 1,
            'intermediate': 2,
            'advanced': 3,
            'expert': 4
        }
        
        experience_mapping = {
            'entry': 1,
            'mid': 2,
            'senior': 3
        }
        
        course_level = difficulty_mapping.get(course_difficulty.lower(), 2)
        candidate_level = experience_mapping.get(experience_level, 2)
        
        # Perfect match
        if course_level == candidate_level:
            return 1.0
        # One level difference
        elif abs(course_level - candidate_level) == 1:
            return 0.8
        # Two levels difference
        elif abs(course_level - candidate_level) == 2:
            return 0.5
        else:
            return 0.2
    
    def _calculate_learning_priority_match(
        self, 
        learning_priorities: List[str], 
        course_skills: List[str],
        course_category: str
    ) -> float:
        """Calculate match with learning priorities"""
        if not learning_priorities:
            return 0.5
        
        priority_match = 0
        for priority in learning_priorities:
            # Check if priority matches course category
            if course_category and priority.lower() in course_category.lower():
                priority_match += 0.5
            
            # Check if priority matches course skills
            for skill in course_skills:
                if priority.lower() in skill or skill in priority.lower():
                    priority_match += 0.3
                    break
        
        return min(priority_match, 1.0)
    
    def _identify_career_focus(self, current_skills: List[str]) -> List[str]:
        """Identify candidate's career focus areas based on skills"""
        focus_scores = {}
        
        for industry, skills in self.industry_skills.items():
            matches = len(set(current_skills) & set(skills))
            if matches > 0:
                focus_scores[industry] = matches / len(skills)
        
        # Return top focus areas (score > 0.2)
        return [industry for industry, score in focus_scores.items() if score > 0.2]
    
    def _identify_skill_gaps(
        self, 
        current_skills: List[str], 
        career_focus: List[str]
    ) -> List[str]:
        """Identify skill gaps based on career focus"""
        gaps = []
        
        for focus in career_focus:
            if focus in self.industry_skills:
                required_skills = set(self.industry_skills[focus])
                current_skills_set = set(current_skills)
                
                # Find missing skills
                missing_skills = required_skills - current_skills_set
                gaps.extend(list(missing_skills))
        
        return list(set(gaps))  # Remove duplicates
    
    def _determine_learning_priorities(
        self, 
        experience_level: str, 
        career_focus: List[str], 
        skill_gaps: List[str]
    ) -> List[str]:
        """Determine learning priorities based on experience and goals"""
        priorities = []
        
        # Experience-based priorities
        if experience_level == 'entry':
            priorities.extend(['fundamentals', 'programming basics', 'version control'])
        elif experience_level == 'mid':
            priorities.extend(['advanced concepts', 'system design', 'leadership'])
        else:  # senior
            priorities.extend(['architecture', 'team leadership', 'emerging technologies'])
        
        # Career focus priorities
        for focus in career_focus:
            priorities.append(focus.replace('_', ' '))
        
        # High-demand skill priorities
        high_demand_skills = [
            'cloud computing', 'machine learning', 'cybersecurity', 
            'devops', 'data science', 'mobile development'
        ]
        
        for skill in skill_gaps:
            if skill in high_demand_skills:
                priorities.append(skill)
        
        return list(set(priorities))
    
    def _generate_career_impact(
        self, 
        course: Course, 
        career_focus: List[str], 
        experience_level: str
    ) -> str:
        """Generate career impact description"""
        impacts = []
        
        # General impact based on course category (inferred)
        course_category = self._infer_course_category(course)
        if 'leadership' in course_category or 'management' in course_category:
            impacts.append("Enhance leadership and management capabilities")
        elif 'programming' in course_category or 'development' in course_category:
            impacts.append("Strengthen technical expertise")
        elif 'data' in course_category:
            impacts.append("Develop data analysis and insights skills")
        elif 'cloud' in course_category:
            impacts.append("Build modern cloud architecture skills")
        
        # Experience level specific impact
        if experience_level == 'entry':
            impacts.append("Build foundational skills for career growth")
        elif experience_level == 'mid':
            impacts.append("Advance to senior-level responsibilities")
        else:
            impacts.append("Stay current with emerging technologies")
        
        # Career focus specific impact
        for focus in career_focus:
            if focus == 'software_development':
                impacts.append("Enhance software engineering practices")
            elif focus == 'data_science':
                impacts.append("Advance data science and analytics capabilities")
            elif focus == 'devops':
                impacts.append("Improve infrastructure and deployment skills")
            elif focus == 'cybersecurity':
                impacts.append("Strengthen security expertise")
        
        if not impacts:
            impacts.append("Expand professional skill set")
        
        return "; ".join(impacts[:3])  # Limit to 3 impacts
    
    def _calculate_total_experience(self, experience: List[Dict[str, Any]]) -> int:
        """Calculate total years of experience"""
        total_years = 0
        current_year = 2025
        
        for exp in experience:
            try:
                start_year = self._extract_year(exp.get('start_date', ''))
                end_year = self._extract_year(exp.get('end_date', '')) or current_year
                
                if start_year and end_year:
                    years = end_year - start_year
                    total_years = max(total_years, years)  # Take the longest experience
            except:
                continue
        
        return total_years
    
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
        recommendations: List[CourseRecommendationResponse],
        db: Session
    ) -> None:
        """Save course recommendations to database"""
        try:
            # Clear existing recommendations for this resume
            db.query(CourseRecommendation).filter(
                CourseRecommendation.resume_id == resume_id
            ).delete()
            
            # Save new recommendations
            for rec in recommendations:
                course_rec = CourseRecommendation(
                    resume_id=resume_id,
                    course_id=rec.course_id,
                    relevance_score=rec.relevance_score,
                    skill_gaps_addressed=rec.skill_gaps_addressed,
                    career_impact=rec.career_impact
                )
                db.add(course_rec)
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error saving course recommendations: {e}")
            db.rollback()
