"""
Agentic Interview Service
Handles question generation, answer evaluation, and scoring using LLM APIs.
"""
import json
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime, timedelta
import os
from dataclasses import dataclass

from app.models.interview import DifficultyLevel, InterviewDomain
from app.schemas.interview_schema import QuestionSchema, QuestionEvaluation, InterviewResultResponse


logger = logging.getLogger(__name__)


@dataclass
class InterviewConfig:
    """Configuration for interview generation"""
    domain: str = "python"
    difficulty_level: str = "intermediate"
    years_of_experience: int = 3
    num_questions: int = 10
    max_questions: int = 20
    question_types: List[str] = None
    time_per_question: int = 3  # minutes
    
    def __post_init__(self):
        if self.question_types is None:
            self.question_types = ["conceptual", "practical", "problem_solving", "coding"]


class QuestionGeneratorAgent:
    """Agent responsible for generating domain-specific questions"""
    
    def __init__(self, groq_api_key: str):
        self.groq_api_key = groq_api_key
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama3-70b-8192"
    
    async def generate_questions(
        self, 
        domain: InterviewDomain, 
        difficulty: DifficultyLevel, 
        years_experience: int,
        config: InterviewConfig = None
    ) -> List[Dict[str, Any]]:
        """Generate interview questions with ideal answers"""
        
        if config is None:
            config = InterviewConfig()
        
        prompt = self._build_question_generation_prompt(
            domain, difficulty, years_experience, config
        )
        
        try:
            response = await self._call_groq_api(prompt)
            questions = self._parse_questions_response(response)
            return questions[:config.max_questions]
            
        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            raise Exception(f"Failed to generate questions: {str(e)}. Please check your API key and connection.")
    
    def _build_question_generation_prompt(
        self, 
        domain: InterviewDomain, 
        difficulty: DifficultyLevel, 
        years_experience: int,
        config: InterviewConfig
    ) -> str:
        """Build the prompt for question generation"""
        
        difficulty_mapping = {
            DifficultyLevel.FRESHER: "basic concepts and fundamentals",
            DifficultyLevel.JUNIOR: "practical applications and simple problem solving",
            DifficultyLevel.INTERMEDIATE: "complex scenarios and system design basics",
            DifficultyLevel.SENIOR: "advanced concepts and architectural decisions", 
            DifficultyLevel.EXPERT: "expert-level system design and leadership scenarios"
        }
        
        domain_context = {
            InterviewDomain.PYTHON: "Python programming, libraries, frameworks, best practices",
            InterviewDomain.DATA_SCIENCE: "data analysis, statistics, ML algorithms, data visualization",
            InterviewDomain.MACHINE_LEARNING: "ML algorithms, model training, evaluation, deployment",
            InterviewDomain.CLOUD_COMPUTING: "AWS/Azure/GCP, containerization, serverless, scaling",
            InterviewDomain.DEVOPS: "CI/CD, infrastructure, monitoring, automation",
            InterviewDomain.WEB_DEVELOPMENT: "frontend/backend, frameworks, APIs, security",
            InterviewDomain.CYBERSECURITY: "security principles, threat analysis, penetration testing",
            InterviewDomain.BLOCKCHAIN: "blockchain technology, smart contracts, DeFi, cryptocurrencies"
        }
        
        return f"""
You are an expert technical interviewer. Generate {config.max_questions} interview questions with their ideal answers.

**Domain**: {domain.value.replace('_', ' ').title()}
**Focus Areas**: {domain_context.get(domain, domain.value)}
**Difficulty Level**: {difficulty.value.title()} ({difficulty_mapping[difficulty]})
**Candidate Experience**: {years_experience} years

**Requirements**:
1. Questions appropriate for {years_experience} years of experience
2. Mix of conceptual, practical, and coding questions
3. Each question MUST have a detailed ideal answer
4. Progressive difficulty within the set

**Output Format** (JSON):
```json
[
  {{
    "id": 1,
    "question": "Question text here",
    "type": "conceptual|practical|coding",
    "ideal_answer": "Detailed ideal answer that covers all key points",
    "key_points": ["point1", "point2", "point3"]
  }}
]
```

Make sure each question has a comprehensive ideal_answer that can be used for comparison.
"""
    
    async def _call_groq_api(self, prompt: str) -> str:
        """Make API call to Groq"""
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an expert technical interviewer. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.base_url, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
                elif response.status == 401:
                    error_text = await response.text()
                    raise Exception(f"API authentication failed (401). Please check your Groq API key. Make sure it's valid and has sufficient credits. Error: {error_text}")
                elif response.status == 429:
                    error_text = await response.text()
                    raise Exception(f"API rate limit exceeded (429). Please wait a moment and try again. Error: {error_text}")
                elif response.status == 402:
                    error_text = await response.text()
                    raise Exception(f"API quota exceeded (402). Please check your Groq account credits. Error: {error_text}")
                else:
                    error_text = await response.text()
                    raise Exception(f"API call failed with status {response.status}. Error: {error_text}")
    
    def _parse_questions_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response to extract questions with ideal answers"""
        try:
            # Clean the response to extract JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            
            questions = json.loads(response)
            
            # Validate and clean questions
            cleaned_questions = []
            for i, q in enumerate(questions):
                cleaned_q = {
                    "id": i + 1,
                    "question": q.get("question", ""),
                    "type": q.get("type", "conceptual"),
                    "ideal_answer": q.get("ideal_answer", ""),
                    "key_points": q.get("key_points", []),
                    "answer": ""  # Empty answer field for frontend
                }
                cleaned_questions.append(cleaned_q)
            
            return cleaned_questions
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse questions JSON: {e}")
            raise Exception("Invalid JSON response from LLM")


class AnswerEvaluationAgent:
    """Agent responsible for evaluating user answers against ideal answers"""
    
    def __init__(self, groq_api_key: str):
        self.groq_api_key = groq_api_key
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama3-70b-8192"
    
    async def evaluate_answers(
        self,
        questions: List[Dict[str, Any]],
        answers: List[Dict[str, Any]]
    ) -> List[QuestionEvaluation]:
        """Evaluate all answers against ideal answers"""
        
        evaluations = []
        
        # Create question-answer mapping
        answer_map = {ans["question_id"]: ans["answer"] for ans in answers}
        
        for question in questions:
            question_id = question["id"]
            user_answer = answer_map.get(question_id, "")
            
            if user_answer.strip():
                evaluation = await self._evaluate_single_answer(question, user_answer)
            else:
                evaluation = self._create_empty_answer_evaluation(question)
            
            evaluations.append(evaluation)
        
        return evaluations
    
    async def _evaluate_single_answer(
        self,
        question: Dict[str, Any],
        user_answer: str
    ) -> QuestionEvaluation:
        """Evaluate a single answer against the ideal answer"""
        
        ideal_answer = question.get("ideal_answer", "")
        
        prompt = f"""
Compare the user's answer with the ideal answer and provide a score.

**Question**: {question['question']}

**Ideal Answer**: {ideal_answer}

**User's Answer**: {user_answer}

**Instructions**:
1. Compare how well the user's answer matches the ideal answer
2. Give a score from 0-10 based on:
   - Accuracy of content (40%)
   - Completeness compared to ideal (30%)
   - Understanding demonstrated (20%)
   - Clarity of explanation (10%)

**Output Format** (JSON):
```json
{{
  "score": 7.5,
  "feedback": "Brief feedback explaining the score",
  "covered_points": ["point1", "point2"],
  "missing_points": ["missing1", "missing2"]
}}
```
"""
        
        try:
            response = await self._call_groq_api(prompt)
            evaluation_data = self._parse_evaluation_response(response)
            
            return QuestionEvaluation(
                question_id=question["id"],
                question=question["question"],
                user_answer=user_answer,
                score=evaluation_data["score"],
                feedback=evaluation_data["feedback"],
                key_points_covered=evaluation_data["covered_points"],
                missing_points=evaluation_data["missing_points"]
            )
            
        except Exception as e:
            logger.error(f"Answer evaluation failed: {e}")
            raise Exception(f"Failed to evaluate answer: {str(e)}. Please check your API key and connection.")
    
    async def _call_groq_api(self, prompt: str) -> str:
        """Make API call to Groq for evaluation"""
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an expert interviewer. Respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1500
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.base_url, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
                elif response.status == 401:
                    error_text = await response.text()
                    raise Exception(f"API authentication failed (401). Please check your Groq API key. Make sure it's valid and has sufficient credits. Error: {error_text}")
                elif response.status == 429:
                    error_text = await response.text()
                    raise Exception(f"API rate limit exceeded (429). Please wait a moment and try again. Error: {error_text}")
                elif response.status == 402:
                    error_text = await response.text()
                    raise Exception(f"API quota exceeded (402). Please check your Groq account credits. Error: {error_text}")
                else:
                    error_text = await response.text()
                    raise Exception(f"API call failed with status {response.status}. Error: {error_text}")
    
    def _parse_evaluation_response(self, response: str) -> Dict[str, Any]:
        """Parse evaluation response from LLM"""
        try:
            # Clean the response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            
            evaluation = json.loads(response)
            
            # Ensure required fields exist
            return {
                "score": min(10, max(0, evaluation.get("score", 5))),
                "feedback": evaluation.get("feedback", "No feedback available"),
                "covered_points": evaluation.get("covered_points", []),
                "missing_points": evaluation.get("missing_points", [])
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse evaluation JSON: {e}")
            # Return a basic score based on answer length
            return {
                "score": 5.0,
                "feedback": "Unable to parse evaluation. Manual review needed.",
                "covered_points": [],
                "missing_points": []
            }
    
    def _create_empty_answer_evaluation(self, question: Dict[str, Any]) -> QuestionEvaluation:
        """Create evaluation for empty/missing answer"""
        return QuestionEvaluation(
            question_id=question["id"],
            question=question["question"],
            user_answer="",
            score=0.0,
            feedback="No answer provided",
            key_points_covered=[],
            missing_points=question.get("key_points", [])
        )
    
    def _create_empty_answer_evaluation(self, question: Dict[str, Any]) -> QuestionEvaluation:
        """Create evaluation for empty/missing answers"""
        return QuestionEvaluation(
            question_id=question["id"],
            question=question["question"],
            user_answer="",
            score=0.0,
            feedback="No answer provided",
            key_points_covered=[],
            missing_points=question.get("key_points", [])
        )


class ScoringAgent:
    """Agent responsible for overall scoring and recommendations"""
    
    def __init__(self, groq_api_key: str):
        self.groq_api_key = groq_api_key
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama3-70b-8192"
    
    def calculate_overall_score(self, evaluations: List[QuestionEvaluation]) -> Dict[str, Any]:
        """Calculate overall interview score and metrics"""
        
        if not evaluations:
            return {"overall_score": 0, "grade": "F", "accuracy_rate": 0}
        
        # Calculate scores
        total_score = sum(eval.score for eval in evaluations)
        max_possible = len(evaluations) * 10
        overall_percentage = (total_score / max_possible) * 100
        
        # Calculate accuracy rate (questions with score >= 6)
        passing_answers = sum(1 for eval in evaluations if eval.score >= 6)
        accuracy_rate = (passing_answers / len(evaluations)) * 100
        
        # Determine grade
        grade = self._calculate_grade(overall_percentage)
        
        return {
            "overall_score": round(overall_percentage, 2),
            "grade": grade,
            "accuracy_rate": round(accuracy_rate, 2),
            "total_questions": len(evaluations),
            "questions_passed": passing_answers
        }
    
    def _calculate_grade(self, percentage: float) -> str:
        """Convert percentage to letter grade"""
        if percentage >= 95: return "A+"
        elif percentage >= 90: return "A"
        elif percentage >= 85: return "A-"
        elif percentage >= 80: return "B+"
        elif percentage >= 75: return "B"
        elif percentage >= 70: return "B-"
        elif percentage >= 65: return "C+"
        elif percentage >= 60: return "C"
        elif percentage >= 55: return "C-"
        elif percentage >= 50: return "D"
        else: return "F"
    
    async def generate_recommendations(
        self,
        evaluations: List[QuestionEvaluation],
        overall_score: float,
        domain: InterviewDomain,
        difficulty: DifficultyLevel,
        years_experience: int
    ) -> Dict[str, Any]:
        """Generate comprehensive recommendations and analysis"""
        
        prompt = self._build_recommendation_prompt(
            evaluations, overall_score, domain, difficulty, years_experience
        )
        
        try:
            response = await self._call_groq_api(prompt)
            recommendations = self._parse_recommendation_response(response)
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            raise Exception(f"Failed to generate recommendations: {str(e)}. Please check your API key and connection.")
    
    def _build_recommendation_prompt(
        self,
        evaluations: List[QuestionEvaluation],
        overall_score: float,
        domain: InterviewDomain,
        difficulty: DifficultyLevel,
        years_experience: int
    ) -> str:
        """Build prompt for generating recommendations"""
        
        # Prepare evaluation summary
        evaluation_summary = []
        for eval in evaluations:
            evaluation_summary.append({
                "question": eval.question[:100] + "...",  # Truncate for prompt
                "score": eval.score,
                "covered_points": eval.key_points_covered,
                "missing_points": eval.missing_points
            })
        
        return f"""
You are a senior technical interviewer analyzing a candidate's performance.

**Interview Details**:
- Domain: {domain.value.replace('_', ' ').title()}
- Difficulty Level: {difficulty.value.title()}
- Candidate Experience: {years_experience} years
- Overall Score: {overall_score}%

**Question Performance Summary**:
{json.dumps(evaluation_summary, indent=2)}

**Analysis Required**:
1. **Strengths**: What the candidate did well
2. **Weaknesses**: Areas needing improvement
3. **Recommendations**: Specific learning suggestions
4. **Resources**: Books, courses, projects to improve
5. **Readiness**: Assessment for next difficulty level
6. **Career Advice**: Industry-specific guidance

**Output Format** (JSON):
```json
{{
  "strengths": ["strength1", "strength2", "strength3"],
  "weaknesses": ["weakness1", "weakness2", "weakness3"],
  "recommendations": [
    "Specific actionable recommendation 1",
    "Specific actionable recommendation 2"
  ],
  "suggested_resources": [
    {{"type": "book", "title": "Book Title", "description": "Why this helps"}},
    {{"type": "course", "title": "Course Name", "description": "Skills covered"}},
    {{"type": "project", "title": "Project Idea", "description": "What to build"}}
  ],
  "next_level_readiness": true/false,
  "readiness_explanation": "Explanation of readiness assessment",
  "focus_areas": ["area1", "area2", "area3"],
  "estimated_study_time": "X weeks/months to improve"
}}
```

Provide constructive, actionable feedback that helps the candidate improve.
"""
    
    async def _call_groq_api(self, prompt: str) -> str:
        """Make API call to Groq for recommendations"""
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a senior technical interviewer providing career guidance. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 3000
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.base_url, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
                elif response.status == 401:
                    error_text = await response.text()
                    raise Exception(f"API authentication failed (401). Please check your Groq API key. Make sure it's valid and has sufficient credits. Error: {error_text}")
                elif response.status == 429:
                    error_text = await response.text()
                    raise Exception(f"API rate limit exceeded (429). Please wait a moment and try again. Error: {error_text}")
                elif response.status == 402:
                    error_text = await response.text()
                    raise Exception(f"API quota exceeded (402). Please check your Groq account credits. Error: {error_text}")
                else:
                    error_text = await response.text()
                    raise Exception(f"API call failed with status {response.status}. Error: {error_text}")
    
    def _parse_recommendation_response(self, response: str) -> Dict[str, Any]:
        """Parse recommendation response from LLM"""
        try:
            # Clean the response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            
            recommendations = json.loads(response)
            
            # Ensure required fields
            return {
                "strengths": recommendations.get("strengths", []),
                "weaknesses": recommendations.get("weaknesses", []),
                "recommendations": recommendations.get("recommendations", []),
                "suggested_resources": recommendations.get("suggested_resources", []),
                "next_level_readiness": recommendations.get("next_level_readiness", False),
                "readiness_explanation": recommendations.get("readiness_explanation", ""),
                "focus_areas": recommendations.get("focus_areas", []),
                "estimated_study_time": recommendations.get("estimated_study_time", "")
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse recommendations JSON: {e}")
            raise Exception("Invalid JSON response from recommendation LLM")


class InterviewOrchestrator:
    """Main orchestrator that coordinates all interview agents"""
    
    def __init__(self, groq_api_key: str = None):
        if not groq_api_key:
            raise ValueError("Groq API key is required for interview system. Please provide a valid API key.")
        
        self.question_generator = QuestionGeneratorAgent(groq_api_key)
        self.answer_evaluator = AnswerEvaluationAgent(groq_api_key)
        self.scoring_agent = ScoringAgent(groq_api_key)
    
    def determine_difficulty_from_experience(self, years_experience: int) -> DifficultyLevel:
        """Map years of experience to difficulty level"""
        if years_experience <= 1:
            return DifficultyLevel.FRESHER
        elif years_experience <= 3:
            return DifficultyLevel.JUNIOR
        elif years_experience <= 5:
            return DifficultyLevel.INTERMEDIATE
        elif years_experience <= 8:
            return DifficultyLevel.SENIOR
        else:
            return DifficultyLevel.EXPERT
    
    async def generate_interview_questions(
        self,
        domain: InterviewDomain,
        years_experience: int,
        config: InterviewConfig = None
    ) -> Tuple[DifficultyLevel, List[Dict[str, Any]]]:
        """Generate questions for an interview session"""
        
        difficulty = self.determine_difficulty_from_experience(years_experience)
        questions = await self.question_generator.generate_questions(
            domain, difficulty, years_experience, config
        )
        
        logger.info(f"Generated {len(questions)} questions for {domain.value} at {difficulty.value} level")
        return difficulty, questions
    
    async def evaluate_interview(
        self,
        questions: List[Dict[str, Any]],
        answers: List[Dict[str, Any]],
        domain: InterviewDomain,
        difficulty: DifficultyLevel,
        years_experience: int
    ) -> InterviewResultResponse:
        """Complete interview evaluation and scoring"""
        
        # Step 1: Evaluate individual answers against ideal answers
        logger.info("Evaluating individual answers...")
        evaluations = await self.answer_evaluator.evaluate_answers(questions, answers)
        
        # Step 2: Calculate overall score
        logger.info("Calculating overall score...")
        score_data = self.scoring_agent.calculate_overall_score(evaluations)
        
        # Step 3: Generate simple recommendations based on score
        logger.info("Generating recommendations...")
        recommendations_data = self._generate_simple_recommendations(
            evaluations, score_data["overall_score"], domain
        )
        
        # Step 4: Build comprehensive result
        result = InterviewResultResponse(
            session_id=0,  # Will be set by the calling function
            domain=domain.value,
            difficulty_level=difficulty.value,
            overall_score=score_data["overall_score"],
            grade=score_data["grade"],
            question_evaluations=evaluations,
            strengths=recommendations_data["strengths"],
            weaknesses=recommendations_data["weaknesses"],
            recommendations=recommendations_data["recommendations"],
            time_taken=0,  # Will be calculated by caller
            accuracy_rate=score_data["accuracy_rate"],
            suggested_resources=recommendations_data.get("suggested_resources", []),
            next_level_readiness=score_data["overall_score"] >= 70
        )
        
        logger.info(f"Interview evaluation complete. Overall score: {score_data['overall_score']}%")
        return result
    
    def _generate_simple_recommendations(
        self, 
        evaluations: List[QuestionEvaluation], 
        overall_score: float,
        domain: InterviewDomain
    ) -> Dict[str, Any]:
        """Generate simple recommendations based on score"""
        
        # Analyze performance
        high_scores = [e for e in evaluations if e.score >= 8]
        medium_scores = [e for e in evaluations if 5 <= e.score < 8]
        low_scores = [e for e in evaluations if e.score < 5]
        
        strengths = []
        weaknesses = []
        recommendations = []
        
        if high_scores:
            strengths.append("Strong understanding of key concepts")
            if len(high_scores) >= len(evaluations) * 0.6:
                strengths.append("Consistent performance across topics")
        
        if medium_scores:
            strengths.append("Good foundation with room for improvement")
        
        if low_scores:
            weaknesses.append("Some knowledge gaps identified")
            weaknesses.append("Need more practice with fundamental concepts")
            recommendations.append(f"Focus on strengthening {domain.value.replace('_', ' ')} fundamentals")
        
        if overall_score >= 80:
            strengths.append("Excellent technical knowledge")
            recommendations.append("Ready for advanced topics and challenges")
        elif overall_score >= 60:
            recommendations.append("Continue practicing and studying key concepts")
            recommendations.append("Focus on areas with lower scores")
        else:
            recommendations.append("Recommend comprehensive study of fundamentals")
            recommendations.append("Practice more problems and examples")
        
        return {
            "strengths": strengths if strengths else ["Shows willingness to learn"],
            "weaknesses": weaknesses if weaknesses else ["Minor areas for improvement"],
            "recommendations": recommendations if recommendations else ["Keep practicing!"],
            "suggested_resources": []
        }
