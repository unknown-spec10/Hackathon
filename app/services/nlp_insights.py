"""
Advanced NLP Insights Module
Provides AI-powered resume analysis with dynamic keyword generation and career insights.
"""

import re
import json
import os
import requests
from typing import Dict, List, Tuple, Optional, Any, Union
from collections import Counter, defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dataclasses import dataclass, field
import pandas as pd
from pathlib import Path
import asyncio
import aiohttp
from datetime import datetime, timedelta


@dataclass
class InsightScore:
    """Insight with confidence score"""
    insight: str
    score: float
    category: str
    evidence: List[str]


@dataclass
class CareerInsights:
    """Career insights from resume analysis"""
    career_trajectory: Dict[str, Any]
    skill_analysis: Dict[str, Any]
    experience_insights: Dict[str, Any]
    education_insights: Dict[str, Any]
    personality_traits: Dict[str, Any]
    career_recommendations: List[str]
    strengths: List[str]
    areas_for_improvement: List[str]
    overall_score: float


@dataclass
class AnalysisConfig:
    """Dynamic analysis configuration"""
    skill_categories: Dict[str, List[str]] = field(default_factory=dict)
    seniority_indicators: Dict[str, List[str]] = field(default_factory=dict)
    industry_keywords: Dict[str, List[str]] = field(default_factory=dict)
    personality_traits: Dict[str, List[str]] = field(default_factory=dict)
    achievement_keywords: List[str] = field(default_factory=list)
    leadership_keywords: List[str] = field(default_factory=list)
    education_levels: Dict[str, List[str]] = field(default_factory=dict)
    relevant_fields: List[str] = field(default_factory=list)
    weights: Dict[str, float] = field(default_factory=dict)
    thresholds: Dict[str, float] = field(default_factory=dict)
    last_updated: Optional[str] = None
    dynamic_sources: List[str] = field(default_factory=list)


class DynamicKeywordGenerator:
    """AI-powered dynamic keyword generator using multiple sources"""
    
    def __init__(self, groq_api_key: Optional[str] = None):
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.cache_duration = timedelta(days=7)  # Cache for 7 days
        self.cache_file = "config/dynamic_keywords_cache.json"
        
    async def generate_skill_keywords(self, category: str, context: str = "") -> List[str]:
        """Generate skill keywords for a category using Groq AI"""
        try:
            if not self.groq_api_key:
                print(f"⚠️ Groq API key not available, using fallback for {category}")
                return self._get_fallback_skills(category)
            
            from groq import Groq
            client = Groq(api_key=self.groq_api_key)
            
            prompt = f"""
            Generate a comprehensive list of relevant skills, technologies, and keywords for the "{category}" category in the current tech job market (2024-2025).
            
            Context: {context}
            
            Requirements:
            1. Include both established and emerging technologies
            2. Focus on skills that are in demand in the job market
            3. Include variations and synonyms
            4. Return exactly 20-30 relevant keywords
            5. Format as a comma-separated list
            6. Use lowercase for consistency
            
            Category: {category}
            
            Examples for reference:
            - programming: python, java, javascript, typescript, go, rust, etc.
            - data_science: machine learning, deep learning, pandas, tensorflow, etc.
            - cloud: aws, azure, gcp, kubernetes, docker, etc.
            
            Generate keywords for "{category}":
            """
            
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            keywords = [kw.strip().lower() for kw in content.split(',') if kw.strip()]
            
            print(f"✅ Generated {len(keywords)} keywords for {category} using Groq AI")
            return keywords[:30]  # Limit to 30 keywords
            
        except Exception as e:
            print(f"❌ Error generating keywords for {category}: {e}")
            return self._get_fallback_skills(category)
    
    async def generate_industry_keywords(self, industry: str) -> List[str]:
        """Generate industry-specific keywords using Groq AI"""
        try:
            if not self.groq_api_key:
                return self._get_fallback_industry(industry)
            
            from groq import Groq
            client = Groq(api_key=self.groq_api_key)
            
            prompt = f"""
            Generate comprehensive keywords and terms that are commonly found in job descriptions, company descriptions, and resumes for the "{industry}" industry.
            
            Requirements:
            1. Include company types, job roles, technologies, and domain-specific terms
            2. Focus on terms that would help identify if someone works in this industry
            3. Include both formal and informal terms
            4. Return 15-25 relevant keywords
            5. Format as comma-separated list in lowercase
            
            Industry: {industry}
            
            Generate industry keywords:
            """
            
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=400
            )
            
            content = response.choices[0].message.content.strip()
            keywords = [kw.strip().lower() for kw in content.split(',') if kw.strip()]
            
            print(f"✅ Generated {len(keywords)} industry keywords for {industry}")
            return keywords[:25]
            
        except Exception as e:
            print(f"❌ Error generating industry keywords for {industry}: {e}")
            return self._get_fallback_industry(industry)
    
    async def generate_trending_skills(self) -> List[str]:
        """Generate trending skills based on current market demand"""
        try:
            if not self.groq_api_key:
                return self._get_fallback_trending()
            
            from groq import Groq
            client = Groq(api_key=self.groq_api_key)
            
            prompt = """
            Generate a list of the most trending and in-demand technical skills in 2024-2025 job market.
            Focus on:
            1. Emerging technologies and frameworks
            2. AI/ML related skills that are hot in the market
            3. Cloud and DevOps trends
            4. New programming languages and tools
            5. Skills that companies are actively seeking
            
            Return 20-30 trending skills as comma-separated lowercase list.
            Include skills like: generative ai, llm, chatgpt, kubernetes, rust, etc.
            """
            
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=400
            )
            
            content = response.choices[0].message.content.strip()
            keywords = [kw.strip().lower() for kw in content.split(',') if kw.strip()]
            
            print(f"✅ Generated {len(keywords)} trending skills")
            return keywords[:30]
            
        except Exception as e:
            print(f"❌ Error generating trending skills: {e}")
            return self._get_fallback_trending()
    
    def _get_fallback_skills(self, category: str) -> List[str]:
        """Fallback skills when AI is not available"""
        fallback_map = {
            'programming': ['python', 'java', 'javascript', 'typescript', 'go', 'rust', 'c++', 'c#'],
            'data_science': ['machine learning', 'deep learning', 'pandas', 'numpy', 'tensorflow', 'pytorch'],
            'cloud_devops': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform'],
            'web_development': ['react', 'angular', 'vue', 'node.js', 'express', 'django'],
            'mobile_development': ['android', 'ios', 'react native', 'flutter', 'swift', 'kotlin'],
            'blockchain': ['blockchain', 'ethereum', 'smart contracts', 'web3', 'solidity'],
            'cybersecurity': ['cybersecurity', 'penetration testing', 'ethical hacking', 'encryption']
        }
        return fallback_map.get(category, ['general', 'technology', 'software'])
    
    def _get_fallback_industry(self, industry: str) -> List[str]:
        """Fallback industry keywords when AI is not available"""
        fallback_map = {
            'fintech': ['banking', 'finance', 'payment', 'cryptocurrency', 'trading'],
            'healthcare': ['medical', 'healthcare', 'hospital', 'pharmaceutical', 'clinical'],
            'ecommerce': ['retail', 'ecommerce', 'marketplace', 'shopping', 'commerce'],
            'ai_ml': ['artificial intelligence', 'machine learning', 'ai', 'ml', 'nlp']
        }
        return fallback_map.get(industry, ['business', 'technology', 'services'])
    
    def _get_fallback_trending(self) -> List[str]:
        """Fallback trending skills when AI is not available"""
        return [
            'chatgpt', 'llm', 'generative ai', 'stable diffusion', 'kubernetes', 
            'rust', 'webassembly', 'edge computing', 'quantum computing', 'blockchain'
        ]
    
    async def fetch_github_trending_topics(self) -> List[str]:
        """Fetch trending topics from GitHub to identify emerging technologies"""
        try:
            url = "https://api.github.com/search/repositories"
            params = {
                'q': 'created:>2024-01-01 stars:>100',
                'sort': 'stars',
                'order': 'desc',
                'per_page': 50
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        languages = []
                        topics = []
                        
                        for repo in data.get('items', []):
                            if repo.get('language'):
                                languages.append(repo['language'].lower())
                            if repo.get('topics'):
                                topics.extend([topic.lower() for topic in repo['topics']])
                        
                        # Get most common languages and topics
                        trending = []
                        trending.extend([lang for lang, _ in Counter(languages).most_common(10)])
                        trending.extend([topic for topic, _ in Counter(topics).most_common(15)])
                        
                        print(f"✅ Fetched {len(trending)} trending technologies from GitHub")
                        return list(set(trending))
        
        except Exception as e:
            print(f"⚠️ Could not fetch GitHub trends: {e}")
        
        return []
    
    async def save_cache(self, data: Dict[str, Any]) -> None:
        """Save generated keywords to cache"""
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved dynamic keywords cache to {self.cache_file}")
        except Exception as e:
            print(f"⚠️ Could not save cache: {e}")
    
    async def load_cache(self) -> Optional[Dict[str, Any]]:
        """Load cached keywords if they're recent enough"""
        try:
            if not os.path.exists(self.cache_file):
                return None
            
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            timestamp = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - timestamp < self.cache_duration:
                print(f"✅ Loaded keywords from cache (age: {datetime.now() - timestamp})")
                return cache_data['data']
            else:
                print(f"⚠️ Cache expired (age: {datetime.now() - timestamp})")
                return None
        
        except Exception as e:
            print(f"⚠️ Could not load cache: {e}")
            return None


class ConfigLoader:
    """Manages loading and saving of dynamic configuration"""
    
    def __init__(self, config_path: str = "config/nlp_insights_config.json"):
        self.config_path = config_path
        self.keyword_generator = DynamicKeywordGenerator()
        
    async def load_default_config(self, use_ai: bool = True) -> AnalysisConfig:
        """Load default configuration with AI-powered dynamic keywords"""
        
        # Check if we have cached dynamic keywords
        if use_ai:
            cached_data = await self.keyword_generator.load_cache()
            if cached_data:
                print("📦 Using cached AI-generated keywords")
                return self._build_config_from_data(cached_data)
        
        print("🚀 Generating fresh configuration with AI-powered keywords...")
        
        # Generate dynamic skill categories
        skill_categories = {}
        categories_to_generate = [
            'programming', 'data_science', 'cloud_devops', 'web_development',
            'mobile_development', 'blockchain', 'cybersecurity', 'ai_ml'
        ]
        
        if use_ai:
            print("🤖 Generating skill categories using AI...")
            for category in categories_to_generate:
                keywords = await self.keyword_generator.generate_skill_keywords(
                    category, 
                    f"Technical skills and technologies for {category} professionals"
                )
                skill_categories[category] = keywords
                
            # Generate trending skills and add as a category
            trending_skills = await self.keyword_generator.generate_trending_skills()
            skill_categories['trending'] = trending_skills
            
            # Fetch GitHub trending topics
            github_trends = await self.keyword_generator.fetch_github_trending_topics()
            if github_trends:
                skill_categories['emerging'] = github_trends
        else:
            # Use fallback if AI is disabled
            skill_categories = self._get_fallback_skill_categories()
        
        # Generate dynamic industry keywords
        industry_keywords = {}
        industries_to_generate = ['fintech', 'healthcare', 'ecommerce', 'ai_ml', 'gaming', 'education']

        if use_ai:
            print("🏢 Generating industry keywords using AI...")
            for industry in industries_to_generate:
                keywords = await self.keyword_generator.generate_industry_keywords(industry)
                industry_keywords[industry] = keywords
        else:
            industry_keywords = self._get_fallback_industry_keywords()
        
        # Build comprehensive configuration
        config_data = {
            'skill_categories': skill_categories,
            'seniority_indicators': self._get_seniority_indicators(),
            'industry_keywords': industry_keywords,
            'personality_traits': self._get_personality_traits(),
            'achievement_keywords': await self._get_achievement_keywords(use_ai),
            'leadership_keywords': await self._get_leadership_keywords(use_ai),
            'education_levels': self._get_education_levels(),
            'relevant_fields': await self._get_relevant_fields(use_ai),
            'weights': self._get_default_weights(),
            'thresholds': self._get_default_thresholds(),
            'last_updated': datetime.now().isoformat(),
            'dynamic_sources': ['groq_ai', 'github_api'] if use_ai else ['fallback']
        }
        
        # Save to cache if using AI
        if use_ai:
            await self.keyword_generator.save_cache(config_data)
        
        print(f"✅ Generated configuration with {len(skill_categories)} skill categories and {len(industry_keywords)} industries")
        return self._build_config_from_data(config_data)
    
    def _build_config_from_data(self, data: Dict[str, Any]) -> AnalysisConfig:
        """Build AnalysisConfig from dictionary data"""
        return AnalysisConfig(
            skill_categories=data.get('skill_categories', {}),
            seniority_indicators=data.get('seniority_indicators', {}),
            industry_keywords=data.get('industry_keywords', {}),
            personality_traits=data.get('personality_traits', {}),
            achievement_keywords=data.get('achievement_keywords', []),
            leadership_keywords=data.get('leadership_keywords', []),
            education_levels=data.get('education_levels', {}),
            relevant_fields=data.get('relevant_fields', []),
            weights=data.get('weights', {}),
            thresholds=data.get('thresholds', {}),
            last_updated=data.get('last_updated'),
            dynamic_sources=data.get('dynamic_sources', [])
        )
    
    async def _get_achievement_keywords(self, use_ai: bool) -> List[str]:
        """Get achievement keywords with optional AI enhancement"""
        base_keywords = [
            'achieved', 'accomplished', 'delivered', 'implemented', 'developed',
            'created', 'built', 'designed', 'launched', 'improved', 'increased',
            'decreased', 'optimized', 'streamlined', 'automated', 'led', 'managed',
            'supervised', 'coordinated', 'executed', 'completed', 'successful'
        ]
        
        if use_ai and self.keyword_generator.groq_api_key:
            try:
                from groq import Groq
                client = Groq(api_key=self.keyword_generator.groq_api_key)
                
                prompt = """
                Generate 20-25 action words and phrases that indicate achievements, accomplishments, 
                and positive outcomes in professional contexts. Focus on words that show impact and results.
                Format as comma-separated lowercase list.
                Examples: achieved, delivered, increased, optimized, etc.
                """
                
                response = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=300
                )
                
                ai_keywords = [kw.strip().lower() for kw in response.choices[0].message.content.split(',') if kw.strip()]
                return list(set(base_keywords + ai_keywords))
            except:
                pass
        
        return base_keywords
    
    async def _get_leadership_keywords(self, use_ai: bool) -> List[str]:
        """Get leadership keywords with optional AI enhancement"""
        base_keywords = [
            'led', 'managed', 'supervised', 'directed', 'coordinated', 'mentored',
            'guided', 'trained', 'developed team', 'built team', 'leadership',
            'team lead', 'project manager', 'scrum master', 'tech lead'
        ]
        
        if use_ai and self.keyword_generator.groq_api_key:
            try:
                from groq import Groq
                client = Groq(api_key=self.keyword_generator.groq_api_key)
                
                prompt = """
                Generate 15-20 words and phrases that indicate leadership, management, and team guidance 
                in professional contexts. Include both formal titles and action words.
                Format as comma-separated lowercase list.
                Examples: led, managed, mentored, team lead, etc.
                """
                
                response = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=250
                )
                
                ai_keywords = [kw.strip().lower() for kw in response.choices[0].message.content.split(',') if kw.strip()]
                return list(set(base_keywords + ai_keywords))
            except:
                pass
        
        return base_keywords
    
    async def _get_relevant_fields(self, use_ai: bool) -> List[str]:
        """Get relevant academic/professional fields with optional AI enhancement"""
        base_fields = [
            'computer science', 'software engineering', 'data science', 'information technology',
            'electrical engineering', 'mathematics', 'statistics', 'physics', 'business',
            'management', 'marketing', 'finance', 'economics'
        ]
        
        if use_ai and self.keyword_generator.groq_api_key:
            try:
                from groq import Groq
                client = Groq(api_key=self.keyword_generator.groq_api_key)
                
                prompt = """
                Generate 20-25 academic fields, majors, and professional domains that are relevant 
                for technology and business careers in 2024-2025.
                Format as comma-separated lowercase list.
                Examples: computer science, data science, business administration, etc.
                """
                
                response = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=300
                )
                
                ai_fields = [field.strip().lower() for field in response.choices[0].message.content.split(',') if field.strip()]
                return list(set(base_fields + ai_fields))
            except:
                pass
        
        return base_fields
    
    def _get_fallback_skill_categories(self) -> Dict[str, List[str]]:
        """Fallback skill categories when AI is not available"""
        return {
            'programming': ['python', 'java', 'javascript', 'typescript', 'go', 'rust'],
            'data_science': ['machine learning', 'deep learning', 'pandas', 'tensorflow'],
            'cloud_devops': ['aws', 'azure', 'docker', 'kubernetes'],
            'web_development': ['react', 'angular', 'vue', 'node.js']
        }
    
    def _get_fallback_industry_keywords(self) -> Dict[str, List[str]]:
        """Fallback industry keywords when AI is not available"""
        return {
            'fintech': ['banking', 'finance', 'payment', 'trading'],
            'healthcare': ['medical', 'hospital', 'pharmaceutical'],
            'ecommerce': ['retail', 'marketplace', 'shopping']
        }
    
    def _get_seniority_indicators(self) -> Dict[str, List[str]]:
        """Get seniority level indicators"""
        return {
            'junior': ['junior', 'entry level', 'graduate', 'intern', 'trainee', 'associate', '0-2 years'],
            'mid': ['mid level', 'intermediate', 'experienced', 'regular', '2-5 years', '3-7 years'],
            'senior': ['senior', 'lead', 'principal', 'expert', 'specialist', '5+ years', '7+ years'],
            'executive': ['director', 'vp', 'cto', 'ceo', 'head of', 'chief', 'executive', '10+ years']
        }
    
    def _get_personality_traits(self) -> Dict[str, List[str]]:
        """Get personality trait indicators"""
        return {
            'analytical': ['analytical', 'logical', 'systematic', 'methodical', 'detail-oriented'],
            'creative': ['creative', 'innovative', 'artistic', 'imaginative', 'original'],
            'leadership': ['leadership', 'decisive', 'confident', 'inspiring', 'motivational'],
            'collaborative': ['collaborative', 'team player', 'cooperative', 'supportive', 'diplomatic'],
            'adaptive': ['adaptable', 'flexible', 'agile', 'versatile', 'quick learner']
        }
    
    def _get_education_levels(self) -> Dict[str, List[str]]:
        """Get education level indicators"""
        return {
            'high_school': ['high school', 'secondary', 'diploma'],
            'bachelor': ['bachelor', "bachelor's", 'bs', 'ba', 'undergraduate'],
            'master': ['master', "master's", 'ms', 'ma', 'mba', 'graduate'],
            'phd': ['phd', 'doctorate', 'doctoral', 'ph.d']
        }
    
    def _get_default_weights(self) -> Dict[str, float]:
        """Get default weights for different analysis components"""
        return {
            'skills_weight': 0.3,
            'experience_weight': 0.25,
            'education_weight': 0.2,
            'achievements_weight': 0.15,
            'leadership_weight': 0.1
        }
    
    def _get_default_thresholds(self) -> Dict[str, float]:
        """Get default thresholds for analysis scoring"""
        return {
            'skill_match_threshold': 0.3,
            'experience_threshold': 0.4,
            'education_threshold': 0.5,
            'achievement_threshold': 0.2,
            'confidence_threshold': 0.6
        }
    
    @staticmethod
    def load_from_file(config_path: str) -> Optional[AnalysisConfig]:
        """Load configuration from JSON file"""
        try:
            if not os.path.exists(config_path):
                return None
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            return AnalysisConfig(**config_data)
        except Exception as e:
            print(f"Error loading config from {config_path}: {e}")
            return None
    
    @staticmethod
    def save_config(config: AnalysisConfig, config_path: str) -> bool:
        """Save configuration to JSON file"""
        try:
            # Convert dataclass to dict
            config_dict = {
                'skill_categories': config.skill_categories,
                'seniority_indicators': config.seniority_indicators,
                'industry_keywords': config.industry_keywords,
                'personality_traits': config.personality_traits,
                'achievement_keywords': config.achievement_keywords,
                'leadership_keywords': config.leadership_keywords,
                'education_levels': config.education_levels,
                'relevant_fields': config.relevant_fields,
                'weights': config.weights,
                'thresholds': config.thresholds,
                'last_updated': config.last_updated,
                'dynamic_sources': config.dynamic_sources
            }
            
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving config to {config_path}: {e}")
            return False
    
    @staticmethod
    def merge_configs(base_config: AnalysisConfig, override_config: AnalysisConfig) -> AnalysisConfig:
        """Merge two configurations, with override taking precedence"""
        merged = AnalysisConfig()
        
        # Merge each field
        for field_name in ['skill_categories', 'seniority_indicators', 'industry_keywords', 'personality_traits']:
            base_dict = getattr(base_config, field_name)
            override_dict = getattr(override_config, field_name)
            merged_dict = {**base_dict, **override_dict}
            setattr(merged, field_name, merged_dict)
        
        # Merge lists
        for field_name in ['achievement_keywords', 'leadership_keywords', 'relevant_fields']:
            base_list = getattr(base_config, field_name)
            override_list = getattr(override_config, field_name)
            merged_list = list(set(base_list + override_list))
            setattr(merged, field_name, merged_list)
        
        # Merge education levels and weights
        merged.education_levels = {**base_config.education_levels, **override_config.education_levels}
        merged.weights = {**base_config.weights, **override_config.weights}
        merged.thresholds = {**base_config.thresholds, **override_config.thresholds}
        merged.last_updated = override_config.last_updated or base_config.last_updated
        merged.dynamic_sources = list(set((base_config.dynamic_sources or []) + (override_config.dynamic_sources or [])))
        
        return merged


class NLPInsightsAnalyzer:
    """Advanced NLP analyzer for extracting deeper insights from resume data"""
    
    def __init__(self, config: AnalysisConfig):
        """
        Initialize with a pre-loaded configuration
        
        Args:
            config: Pre-loaded AnalysisConfig object
        """
        self.config = config
        self.config_loader = ConfigLoader()
        
        # Initialize additional derived data
        self._initialize_derived_data()
    
    @classmethod
    async def create(cls, 
                     config_path: Optional[str] = None, 
                     custom_config: Optional[AnalysisConfig] = None,
                     use_ai: bool = True) -> "NLPInsightsAnalyzer":
        """
        Factory method to create NLPInsightsAnalyzer with async configuration loading
        
        Args:
            config_path: Path to JSON configuration file
            custom_config: Custom AnalysisConfig object
            use_ai: Whether to use AI-powered keyword generation
        """
        config_loader = ConfigLoader(config_path)
        
        # Load default configuration with AI enhancement
        base_config = await config_loader.load_default_config(use_ai=use_ai)
        
        # Override with file config if provided
        if config_path and os.path.exists(config_path):
            file_config = ConfigLoader.load_from_file(config_path)
            if file_config:
                base_config = ConfigLoader.merge_configs(base_config, file_config)
                print(f"✅ Loaded configuration from: {config_path}")
        
        # Override with custom config if provided
        if custom_config:
            base_config = ConfigLoader.merge_configs(base_config, custom_config)
            print("✅ Applied custom configuration")
        
        return cls(base_config)
    
    @classmethod
    def create_with_fallback(cls, 
                            config_path: Optional[str] = None, 
                            custom_config: Optional[AnalysisConfig] = None) -> "NLPInsightsAnalyzer":
        """
        Synchronous factory method with fallback configuration (no AI)
        
        Args:
            config_path: Path to JSON configuration file
            custom_config: Custom AnalysisConfig object
        """
        config_loader = ConfigLoader(config_path)
        
        # Use fallback configuration (no async needed)
        base_config = AnalysisConfig(
            skill_categories=config_loader._get_fallback_skill_categories(),
            seniority_indicators=config_loader._get_seniority_indicators(),
            industry_keywords=config_loader._get_fallback_industry_keywords(),
            personality_traits=config_loader._get_personality_traits(),
            achievement_keywords=[
                'achieved', 'accomplished', 'delivered', 'implemented', 'developed',
                'created', 'built', 'designed', 'launched', 'improved'
            ],
            leadership_keywords=[
                'led', 'managed', 'supervised', 'directed', 'coordinated', 'mentored'
            ],
            education_levels=config_loader._get_education_levels(),
            relevant_fields=[
                'computer science', 'software engineering', 'data science', 'information technology'
            ],
            weights=config_loader._get_default_weights(),
            thresholds=config_loader._get_default_thresholds(),
            last_updated=datetime.now().isoformat(),
            dynamic_sources=['fallback']
        )
        
        # Override with file config if provided
        if config_path and os.path.exists(config_path):
            file_config = ConfigLoader.load_from_file(config_path)
            if file_config:
                base_config = ConfigLoader.merge_configs(base_config, file_config)
                print(f"✅ Loaded configuration from: {config_path}")
        
        # Override with custom config if provided
        if custom_config:
            base_config = ConfigLoader.merge_configs(base_config, custom_config)
            print("✅ Applied custom configuration")
        
        return cls(base_config)
    
    async def refresh_dynamic_config(self, use_ai: bool = True) -> None:
        """Refresh configuration with latest AI-generated keywords"""
        fresh_config = await self.config_loader.load_default_config(use_ai=use_ai)
        self.config = ConfigLoader.merge_configs(fresh_config, self.config)
        self._initialize_derived_data()
        print("✅ Configuration refreshed with latest dynamic keywords")
    
    def _initialize_derived_data(self):
        """Initialize derived data from configuration"""
        # Create reverse mapping for education levels - must match config.education_levels keys
        self.education_level_order = ['high_school', 'bachelor', 'master', 'phd']
        
        # Create emerging skills list from latest trends
        emerging_base = ['ai', 'machine learning', 'blockchain', 'kubernetes', 'react', 'vue', 'docker']
        self.emerging_skills = emerging_base + [
            skill for category_skills in self.config.skill_categories.values()
            for skill in category_skills if any(emerging in skill.lower() for emerging in emerging_base)
        ]

    async def analyze_resume(self, resume_data: Dict[str, Any]) -> CareerInsights:
        """
        Perform comprehensive NLP analysis on resume data
        """
        try:
            # Extract text content for analysis
            all_text = self._extract_all_text(resume_data)
            
            # Perform various analyses
            career_trajectory = self._analyze_career_trajectory(resume_data)
            skill_analysis = self._analyze_skills(resume_data, all_text)
            experience_insights = self._analyze_experience(resume_data, all_text)
            education_insights = self._analyze_education(resume_data)
            personality_traits = self._infer_personality_traits(all_text)
            
            # Generate AI-powered recommendations and insights
            career_recommendations = await self._generate_career_recommendations(
                skill_analysis, experience_insights, education_insights
            )
            strengths = self._identify_strengths(skill_analysis, experience_insights)
            improvements = self._identify_improvement_areas(skill_analysis, career_trajectory)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(
                skill_analysis, experience_insights, education_insights
            )
            
            return CareerInsights(
                career_trajectory=career_trajectory,
                skill_analysis=skill_analysis,
                experience_insights=experience_insights,
                education_insights=education_insights,
                personality_traits=personality_traits,
                career_recommendations=career_recommendations,
                strengths=strengths,
                areas_for_improvement=improvements,
                overall_score=overall_score
            )
            
        except Exception as e:
            print(f"Error in NLP analysis: {e}")
            return self._create_default_insights()
    
    def analyze_resume_sync(self, resume_data: Dict[str, Any]) -> CareerInsights:
        """
        Synchronous wrapper for analyze_resume for backward compatibility
        Uses fallback recommendations if async is not available
        """
        try:
            # Extract text content for analysis
            all_text = self._extract_all_text(resume_data)
            
            # Perform various analyses
            career_trajectory = self._analyze_career_trajectory(resume_data)
            skill_analysis = self._analyze_skills(resume_data, all_text)
            experience_insights = self._analyze_experience(resume_data, all_text)
            education_insights = self._analyze_education(resume_data)
            personality_traits = self._infer_personality_traits(all_text)
            
            # Generate fallback recommendations (synchronous)
            career_recommendations = self._generate_fallback_career_recommendations(
                skill_analysis, experience_insights, education_insights
            )
            strengths = self._identify_strengths(skill_analysis, experience_insights)
            improvements = self._identify_improvement_areas(skill_analysis, career_trajectory)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(
                skill_analysis, experience_insights, education_insights
            )
            
            return CareerInsights(
                career_trajectory=career_trajectory,
                skill_analysis=skill_analysis,
                experience_insights=experience_insights,
                education_insights=education_insights,
                personality_traits=personality_traits,
                career_recommendations=career_recommendations,
                strengths=strengths,
                areas_for_improvement=improvements,
                overall_score=overall_score
            )
            
        except Exception as e:
            print(f"Error in NLP analysis: {e}")
            return self._create_default_insights()

    def _extract_all_text(self, resume_data: Dict[str, Any]) -> str:
        """Extract all text content from resume data"""
        text_parts = []
        
        # Add skills
        if 'skills' in resume_data and resume_data['skills']:
            text_parts.append(' '.join(resume_data['skills']))
        
        # Add experience descriptions
        if 'experience' in resume_data:
            for exp in resume_data['experience']:
                if exp.get('description'):
                    text_parts.append(exp['description'])
                if exp.get('responsibilities'):
                    if isinstance(exp['responsibilities'], list):
                        text_parts.extend(exp['responsibilities'])
                    else:
                        text_parts.append(exp['responsibilities'])
        
        # Add project descriptions
        if 'projects' in resume_data:
            for project in resume_data['projects']:
                if project.get('description'):
                    text_parts.append(project['description'])
        
        # Add education details
        if 'education' in resume_data:
            for edu in resume_data['education']:
                if edu.get('field'):
                    text_parts.append(edu['field'])
                if edu.get('institution'):
                    text_parts.append(edu['institution'])
        
        return ' '.join(text_parts).lower()

    def _analyze_career_trajectory(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze career progression and trajectory using dynamic configuration"""
        trajectory = {
            'seniority_level': 'entry',
            'career_progression': 'stable',
            'industry_focus': 'generalist',
            'years_experience': 0,
            'role_diversity': 'low',
            'trajectory_score': 0.5
        }
        
        try:
            if 'experience' in resume_data and resume_data['experience']:
                experiences = resume_data['experience']
                
                # Analyze seniority progression using dynamic indicators
                seniority_levels = []
                for exp in experiences:
                    title = exp.get('title', '').lower()
                    level = self._determine_seniority_level(title)
                    seniority_levels.append(level)
                
                if seniority_levels:
                    level_order = ['entry', 'junior', 'mid', 'senior', 'executive']
                    trajectory['seniority_level'] = max(seniority_levels, key=lambda x: 
                        level_order.index(x) if x in level_order else 0)
                
                # Analyze progression
                if len(set(seniority_levels)) > 1:
                    trajectory['career_progression'] = 'ascending'
                    trajectory['trajectory_score'] += 0.2
                
                # Role diversity analysis
                unique_roles = len(set(exp.get('title', '').lower() for exp in experiences))
                if unique_roles > 2:
                    trajectory['role_diversity'] = 'high'
                    trajectory['trajectory_score'] += 0.1
                elif unique_roles > 1:
                    trajectory['role_diversity'] = 'medium'
                
                # Dynamic industry analysis using configurable keywords
                industry_matches = []
                for exp in experiences:
                    company = exp.get('company', '').lower()
                    title = exp.get('title', '').lower()
                    desc = exp.get('description', '').lower()
                    
                    exp_text = f"{company} {title} {desc}"
                    
                    # Check against all configured industry keywords
                    for industry, keywords in self.config.industry_keywords.items():
                        match_count = sum(1 for keyword in keywords if keyword in exp_text)
                        if match_count > 0:
                            industry_matches.extend([industry] * match_count)
                
                if industry_matches:
                    most_common = Counter(industry_matches).most_common(1)[0][0]
                    trajectory['industry_focus'] = most_common
                
                # Calculate years of experience (estimate)
                trajectory['years_experience'] = len(experiences) * 1.5  # Rough estimate
        
        except Exception as e:
            print(f"Error analyzing career trajectory: {e}")
        
        return trajectory

    def _analyze_skills(self, resume_data: Dict[str, Any], all_text: str) -> Dict[str, Any]:
        """Deep analysis of skills and competencies using dynamic configuration"""
        analysis = {
            'total_skills': 0,
            'skill_categories': {},
            'skill_density': 0.0,
            'emerging_skills': [],
            'core_competencies': [],
            'skill_gaps': [],
            'marketability_score': 0.5
        }
        
        try:
            skills = resume_data.get('skills', [])
            if not skills:
                return analysis
            
            analysis['total_skills'] = len(skills)
            
            # Dynamic skill categorization using configuration
            skill_categories = defaultdict(list)
            skills_lower = [skill.lower() for skill in skills]
            
            for category, category_skills in self.config.skill_categories.items():
                for skill in skills_lower:
                    if any(cat_skill in skill for cat_skill in category_skills):
                        skill_categories[category].append(skill)
            
            analysis['skill_categories'] = dict(skill_categories)
            
            # Calculate skill density (skills per word in resume)
            word_count = len(all_text.split())
            if word_count > 0:
                analysis['skill_density'] = len(skills) / word_count
            
            # Identify core competencies (most frequent skill categories)
            if skill_categories:
                sorted_categories = sorted(skill_categories.items(), 
                                         key=lambda x: len(x[1]), reverse=True)
                analysis['core_competencies'] = [cat for cat, skills in sorted_categories[:3]]
            
            # Dynamic emerging skills identification
            analysis['emerging_skills'] = [skill for skill in skills_lower 
                                         if any(emerging_skill in skill for emerging_skill in self.emerging_skills)]
            
            # Dynamic marketability score calculation using configurable weights
            marketability = 0.5
            threshold_diverse = self.config.thresholds.get('min_skills_diverse', 10)
            threshold_technical = self.config.thresholds.get('min_technical_skills', 3)
            
            if len(skill_categories) >= 3:
                marketability += self.config.weights.get('diversity_bonus', 0.2)
            
            if analysis['emerging_skills']:
                marketability += self.config.weights.get('emerging_bonus', 0.2)
            
            if 'programming' in skill_categories and len(skill_categories['programming']) >= threshold_technical:
                marketability += self.config.weights.get('technical_bonus', 0.1)
            
            analysis['marketability_score'] = min(marketability, 1.0)
            
        except Exception as e:
            print(f"Error analyzing skills: {e}")
        
        return analysis

    def _analyze_experience(self, resume_data: Dict[str, Any], all_text: str) -> Dict[str, Any]:
        """Analyze work experience patterns and insights using dynamic configuration"""
        analysis = {
            'total_positions': 0,
            'experience_diversity': 'low',
            'leadership_indicators': 0,
            'achievement_density': 0.0,
            'responsibility_growth': False,
            'domain_expertise': [],
            'experience_quality_score': 0.5
        }
        
        try:
            experiences = resume_data.get('experience', [])
            if not experiences:
                return analysis
            
            analysis['total_positions'] = len(experiences)
            
            # Dynamic diversity analysis
            if len(experiences) > 3:
                analysis['experience_diversity'] = 'high'
            elif len(experiences) > 1:
                analysis['experience_diversity'] = 'medium'
            
            # Dynamic leadership analysis using configurable keywords
            leadership_count = 0
            
            for exp in experiences:
                desc = exp.get('description', '').lower()
                responsibilities = exp.get('responsibilities', [])
                if isinstance(responsibilities, list):
                    desc += ' ' + ' '.join(responsibilities).lower()
                
                # Use dynamic leadership keywords from config
                leadership_count += sum(1 for word in self.config.leadership_keywords 
                                      if word in desc)
            
            analysis['leadership_indicators'] = leadership_count
            
            # Dynamic achievement analysis using configurable keywords
            achievement_count = 0
            total_words = 0
            
            for exp in experiences:
                desc = exp.get('description', '').lower()
                words = desc.split()
                total_words += len(words)
                
                # Use dynamic achievement keywords from config
                achievement_count += sum(1 for word in self.config.achievement_keywords 
                                       if word in words)
            
            if total_words > 0:
                analysis['achievement_density'] = achievement_count / total_words
            
            # Dynamic responsibility growth analysis
            if len(experiences) >= 2:
                first_exp = experiences[0].get('description', '').lower()
                last_exp = experiences[-1].get('description', '').lower()
                
                first_leadership = sum(1 for word in self.config.leadership_keywords 
                                     if word in first_exp)
                last_leadership = sum(1 for word in self.config.leadership_keywords 
                                    if word in last_exp)
                
                analysis['responsibility_growth'] = last_leadership > first_leadership
            
            # Dynamic experience quality score using configurable thresholds
            quality_score = 0.5
            min_achievement_density = self.config.thresholds.get('min_achievement_density', 0.05)
            
            if analysis['leadership_indicators'] > 0:
                quality_score += 0.2
            if analysis['achievement_density'] > min_achievement_density:
                quality_score += 0.2
            if analysis['responsibility_growth']:
                quality_score += 0.1
            
            analysis['experience_quality_score'] = min(quality_score, 1.0)
            
        except Exception as e:
            print(f"Error analyzing experience: {e}")
        
        return analysis

    def _analyze_education(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze educational background and its relevance using dynamic configuration"""
        analysis = {
            'education_level': 'none',
            'field_relevance': 'low',
            'institution_quality': 'unknown',
            'continuous_learning': False,
            'education_score': 0.3
        }
        
        try:
            education = resume_data.get('education', [])
            if not education:
                return analysis
            
            # Dynamic education level determination using configuration
            levels = []
            for edu in education:
                degree = edu.get('degree', '').lower()
                
                # Check against all configured education levels
                for level, level_keywords in self.config.education_levels.items():
                    if any(keyword in degree for keyword in level_keywords):
                        levels.append(level)
                        break
            
            if levels:
                try:
                    analysis['education_level'] = max(levels, key=lambda x: self.education_level_order.index(x))
                except ValueError as e:
                    print(f"Error analyzing education: {e}")
                    # Fallback: use the first detected level
                    analysis['education_level'] = levels[0] if levels else 'unknown'
            
            # Dynamic field relevance assessment using configurable relevant fields
            for edu in education:
                field = edu.get('field', '').lower()
                if any(keyword in field for keyword in self.config.relevant_fields):
                    analysis['field_relevance'] = 'high'
                    break
            
            # Check for continuous learning (multiple degrees, recent graduation)
            if len(education) > 1:
                analysis['continuous_learning'] = True
            
            # Dynamic education score calculation
            score = 0.3
            if analysis['education_level'] == 'bachelors':
                score += 0.2
            elif analysis['education_level'] == 'masters':
                score += 0.3
            elif analysis['education_level'] == 'doctorate':
                score += 0.4
            
            if analysis['field_relevance'] == 'high':
                score += 0.2
            
            if analysis['continuous_learning']:
                score += 0.1
            
            analysis['education_score'] = min(score, 1.0)
            
        except Exception as e:
            print(f"Error analyzing education: {e}")
        
        return analysis

    def _infer_personality_traits(self, all_text: str) -> Dict[str, Any]:
        """Infer personality traits from resume text using dynamic NLP configuration"""
        traits = {
            'analytical': 0.0,
            'creative': 0.0,
            'leadership': 0.0,
            'collaborative': 0.0,
            'detail_oriented': 0.0,
            'innovative': 0.0,
            'dominant_traits': []
        }
        
        try:
            words = all_text.split()
            total_words = len(words)
            
            if total_words == 0:
                return traits
            
            # Dynamic trait calculation using configurable indicators
            for trait, indicators in self.config.personality_traits.items():
                count = sum(1 for word in words if any(indicator in word for indicator in indicators))
                traits[trait] = count / total_words if total_words > 0 else 0.0
            
            # Identify dominant traits
            trait_scores = [(trait, score) for trait, score in traits.items() 
                           if trait != 'dominant_traits' and score > 0]
            trait_scores.sort(key=lambda x: x[1], reverse=True)
            traits['dominant_traits'] = [trait for trait, score in trait_scores[:3]]
            
        except Exception as e:
            print(f"Error inferring personality traits: {e}")
        
        return traits

    def _determine_seniority_level(self, title: str) -> str:
        """Determine seniority level from job title using dynamic configuration"""
        title = title.lower()
        
        for level, indicators in self.config.seniority_indicators.items():
            if any(indicator in title for indicator in indicators):
                return level
        
        return 'entry'

    async def _generate_career_recommendations(self, skill_analysis: Dict, 
                                         experience_insights: Dict, 
                                         education_insights: Dict) -> List[str]:
        """Generate AI-powered personalized career recommendations"""
        
        # Try AI-generated recommendations first
        ai_recommendations = await self._generate_ai_career_recommendations(
            skill_analysis, experience_insights, education_insights
        )
        
        if ai_recommendations:
            return ai_recommendations
        
        # Fallback to rule-based recommendations if AI fails
        return self._generate_fallback_career_recommendations(
            skill_analysis, experience_insights, education_insights
        )
    
    async def _generate_ai_career_recommendations(self, skill_analysis: Dict, 
                                                experience_insights: Dict, 
                                                education_insights: Dict) -> List[str]:
        """Generate career recommendations using Groq AI"""
        try:
            # Check if we have access to AI
            if not self.config_loader.keyword_generator.groq_api_key:
                return []
            
            from groq import Groq
            client = Groq(api_key=self.config_loader.keyword_generator.groq_api_key)
            
            # Build comprehensive profile summary for AI
            profile_summary = self._build_profile_summary_for_ai(
                skill_analysis, experience_insights, education_insights
            )
            
            prompt = f"""
            As an expert career counselor and tech industry advisor, analyze this professional profile and provide 5-7 specific, actionable career recommendations.

            PROFESSIONAL PROFILE:
            {profile_summary}

            INSTRUCTIONS:
            1. Provide specific job roles and career paths based on the candidate's strengths
            2. Consider current market trends and demand (2024-2025)
            3. Suggest both immediate next steps and longer-term career progression
            4. Include skill development recommendations where relevant
            5. Be specific about industries or companies that would be a good fit
            6. Consider salary growth potential and career advancement opportunities
            7. Each recommendation should be 1-2 sentences and actionable

            OUTPUT FORMAT:
            Provide exactly 5-7 recommendations, each on a new line, without numbering or bullet points.
            Focus on career advancement, role transitions, skill development, and market opportunities.

            CAREER RECOMMENDATIONS:
            """
            
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,  # Slightly creative but focused
                max_tokens=600
            )
            
            content = response.choices[0].message.content.strip()
            recommendations = [
                rec.strip() for rec in content.split('\n') 
                if rec.strip() and not rec.strip().lower().startswith(('career recommendations:', 'recommendations:'))
            ]
            
            # Filter and clean recommendations
            filtered_recommendations = []
            for rec in recommendations:
                if len(rec) > 20 and not rec.startswith(('1.', '2.', '3.', '4.', '5.', '-', '•')):
                    filtered_recommendations.append(rec)
            
            if len(filtered_recommendations) >= 3:
                print(f"✅ Generated {len(filtered_recommendations)} AI-powered career recommendations")
                return filtered_recommendations[:7]  # Limit to 7 recommendations
            else:
                print("⚠️ AI recommendations insufficient, using fallback")
                return []
                
        except Exception as e:
            print(f"⚠️ Error generating AI career recommendations: {e}")
            return []
    
    def _build_profile_summary_for_ai(self, skill_analysis: Dict, 
                                    experience_insights: Dict, 
                                    education_insights: Dict) -> str:
        """Build a comprehensive profile summary for AI analysis"""
        
        summary_parts = []
        
        # Skills Summary
        total_skills = skill_analysis.get('total_skills', 0)
        core_competencies = skill_analysis.get('core_competencies', [])
        emerging_skills = skill_analysis.get('emerging_skills', [])
        marketability_score = skill_analysis.get('marketability_score', 0)
        skill_categories = skill_analysis.get('skill_categories', {})
        
        summary_parts.append(f"SKILLS PROFILE:")
        summary_parts.append(f"• Total Skills: {total_skills}")
        summary_parts.append(f"• Core Competencies: {', '.join(core_competencies)}")
        if emerging_skills:
            summary_parts.append(f"• Emerging Technologies: {', '.join(emerging_skills)}")
        summary_parts.append(f"• Market Relevance Score: {marketability_score:.1%}")
        
        # Detailed skill categories
        for category, skills in skill_categories.items():
            if skills:
                summary_parts.append(f"• {category.replace('_', ' ').title()}: {', '.join(skills[:5])}{'...' if len(skills) > 5 else ''}")
        
        # Experience Summary
        total_positions = experience_insights.get('total_positions', 0)
        leadership_indicators = experience_insights.get('leadership_indicators', 0)
        experience_diversity = experience_insights.get('experience_diversity', 'unknown')
        experience_quality = experience_insights.get('experience_quality_score', 0)
        responsibility_growth = experience_insights.get('responsibility_growth', False)
        
        summary_parts.append(f"\nEXPERIENCE PROFILE:")
        summary_parts.append(f"• Total Positions: {total_positions}")
        summary_parts.append(f"• Leadership Experience: {'Strong' if leadership_indicators > 2 else 'Moderate' if leadership_indicators > 0 else 'Limited'}")
        summary_parts.append(f"• Experience Diversity: {experience_diversity}")
        summary_parts.append(f"• Experience Quality Score: {experience_quality:.1%}")
        summary_parts.append(f"• Career Progression: {'Demonstrated growth' if responsibility_growth else 'Stable trajectory'}")
        
        # Education Summary
        education_level = education_insights.get('education_level', 'unknown')
        field_relevance = education_insights.get('field_relevance', 'unknown')
        continuous_learning = education_insights.get('continuous_learning', False)
        education_score = education_insights.get('education_score', 0)
        
        summary_parts.append(f"\nEDUCATION PROFILE:")
        summary_parts.append(f"• Education Level: {education_level.title()}")
        summary_parts.append(f"• Field Relevance: {field_relevance.title()}")
        summary_parts.append(f"• Continuous Learning: {'Yes' if continuous_learning else 'No'}")
        summary_parts.append(f"• Education Score: {education_score:.1%}")
        
        # Career trajectory context
        summary_parts.append(f"\nCAREER CONTEXT:")
        summary_parts.append(f"• Looking for career advancement opportunities")
        summary_parts.append(f"• Current market: High demand for AI/ML, Cloud, and Full-stack skills")
        summary_parts.append(f"• Salary growth potential and leadership track important")
        
        return '\n'.join(summary_parts)
    
    def _generate_fallback_career_recommendations(self, skill_analysis: Dict, 
                                                experience_insights: Dict, 
                                                education_insights: Dict) -> List[str]:
        """Generate rule-based career recommendations as fallback"""
        recommendations = []
        
        try:
            # Skill-based recommendations
            core_competencies = skill_analysis.get('core_competencies', [])
            emerging_skills = skill_analysis.get('emerging_skills', [])
            marketability = skill_analysis.get('marketability_score', 0)
            
            # AI/ML career path
            if 'data_science' in core_competencies or 'ai_ml' in core_competencies:
                if 'programming' in core_competencies:
                    recommendations.append("Consider Machine Learning Engineer or AI Engineer roles with your combined programming and data science skills")
                else:
                    recommendations.append("Explore Data Scientist or ML Research positions, consider strengthening programming skills")
            
            # Full-stack development path
            if 'programming' in core_competencies and 'web_development' in core_competencies:
                recommendations.append("Target Senior Full-Stack Developer or Solution Architect roles in growing tech companies")
            
            # Cloud/DevOps career path
            if 'cloud_devops' in core_competencies:
                if experience_insights.get('leadership_indicators', 0) > 1:
                    recommendations.append("Pursue Cloud Solutions Architect or DevOps Team Lead positions")
                else:
                    recommendations.append("Focus on Cloud Engineer or Site Reliability Engineer roles")
            
            # Emerging tech opportunities
            if emerging_skills:
                recommendations.append(f"Leverage your knowledge of emerging technologies ({', '.join(emerging_skills[:3])}) for roles in innovative startups or R&D divisions")
            
            # Leadership track recommendations
            leadership_indicators = experience_insights.get('leadership_indicators', 0)
            experience_quality = experience_insights.get('experience_quality_score', 0)
            
            if leadership_indicators > 2 and experience_quality > 0.6:
                recommendations.append("Consider transitioning to Engineering Manager or Technical Lead roles to leverage your proven leadership experience")
            elif leadership_indicators > 0:
                recommendations.append("Develop your leadership skills further to qualify for senior technical or management positions")
            
            # Education-based recommendations
            education_level = education_insights.get('education_level', '')
            if education_level == 'masters':
                recommendations.append("Your advanced degree positions you well for specialized roles in research, consulting, or senior technical positions at top-tier companies")
            elif education_level == 'phd':
                recommendations.append("Consider research scientist, principal engineer, or CTO track positions that leverage your doctoral expertise")
            
            # Market-driven recommendations
            if marketability > 0.7:
                recommendations.append("Your skill set is highly marketable - consider opportunities at FAANG companies or high-growth startups for maximum career acceleration")
            elif marketability > 0.5:
                recommendations.append("Focus on building expertise in 1-2 core areas to increase your competitive advantage in the job market")
            else:
                recommendations.append("Invest in developing in-demand skills like cloud technologies, AI/ML, or modern web frameworks to improve marketability")
            
            # Default recommendations
            if not recommendations:
                recommendations.extend([
                    "Focus on building a stronger technical portfolio with real-world projects",
                    "Consider contributing to open-source projects to demonstrate your skills",
                    "Network within your industry and consider mentorship opportunities"
                ])
            
            # Limit to reasonable number of recommendations
            return recommendations[:6]
            
        except Exception as e:
            print(f"Error generating fallback recommendations: {e}")
            return [
                "Continue developing your technical skills and gaining experience",
                "Focus on building a strong portfolio of projects",
                "Consider certification in your areas of interest"
            ]

    def _identify_strengths(self, skill_analysis: Dict, experience_insights: Dict) -> List[str]:
        """Identify candidate's key strengths"""
        strengths = []
        
        try:
            # Skill-based strengths
            if skill_analysis.get('total_skills', 0) > 10:
                strengths.append("Diverse technical skill set")
            
            if skill_analysis.get('marketability_score', 0) > 0.7:
                strengths.append("High market demand skills")
            
            emerging_skills = skill_analysis.get('emerging_skills', [])
            if emerging_skills:
                strengths.append("Up-to-date with emerging technologies")
            
            # Experience-based strengths
            if experience_insights.get('leadership_indicators', 0) > 0:
                strengths.append("Demonstrated leadership capabilities")
            
            if experience_insights.get('achievement_density', 0) > 0.05:
                strengths.append("Strong track record of achievements")
            
            if experience_insights.get('responsibility_growth'):
                strengths.append("Clear career progression")
            
            # Default strength
            if not strengths:
                strengths.append("Solid foundation for career growth")
            
        except Exception as e:
            print(f"Error identifying strengths: {e}")
            strengths.append("Potential for growth and development")
        
        return strengths

    def _identify_improvement_areas(self, skill_analysis: Dict, career_trajectory: Dict) -> List[str]:
        """Identify areas for improvement"""
        improvements = []
        
        try:
            # Skill gaps
            skill_categories = skill_analysis.get('skill_categories', {})
            if 'soft_skills' not in skill_categories or len(skill_categories.get('soft_skills', [])) < 2:
                improvements.append("Develop and highlight soft skills")
            
            if skill_analysis.get('total_skills', 0) < 8:
                improvements.append("Expand technical skill set")
            
            # Career trajectory improvements
            if career_trajectory.get('role_diversity') == 'low':
                improvements.append("Gain experience in diverse roles or projects")
            
            if career_trajectory.get('trajectory_score', 0) < 0.6:
                improvements.append("Focus on career progression and skill advancement")
            
            # Default improvement
            if not improvements:
                improvements.append("Continue learning and staying updated with industry trends")
            
        except Exception as e:
            print(f"Error identifying improvements: {e}")
            improvements.append("Focus on continuous learning and skill development")
        
        return improvements

    def _calculate_overall_score(self, skill_analysis: Dict, 
                               experience_insights: Dict, 
                               education_insights: Dict) -> float:
        """Calculate overall candidate score using dynamic weights"""
        try:
            skill_score = skill_analysis.get('marketability_score', 0.5)
            experience_score = experience_insights.get('experience_quality_score', 0.5)
            education_score = education_insights.get('education_score', 0.3)
            
            # Use dynamic weights from configuration
            skill_weight = self.config.weights.get('skill_weight', 0.4)
            experience_weight = self.config.weights.get('experience_weight', 0.4)
            education_weight = self.config.weights.get('education_weight', 0.2)
            
            # Weighted average
            overall_score = (skill_score * skill_weight + 
                           experience_score * experience_weight + 
                           education_score * education_weight)
            return round(overall_score, 2)
            
        except Exception as e:
            print(f"Error calculating overall score: {e}")
            return 0.5

    def _create_default_insights(self) -> CareerInsights:
        """Create default insights when analysis fails"""
        return CareerInsights(
            career_trajectory={'seniority_level': 'entry', 'trajectory_score': 0.5},
            skill_analysis={'total_skills': 0, 'marketability_score': 0.5},
            experience_insights={'total_positions': 0, 'experience_quality_score': 0.5},
            education_insights={'education_level': 'none', 'education_score': 0.3},
            personality_traits={'dominant_traits': []},
            career_recommendations=['Focus on skill development and gaining experience'],
            strengths=['Potential for growth'],
            areas_for_improvement=['Develop core competencies'],
            overall_score=0.5
        )

    def generate_insights_report(self, insights: CareerInsights) -> str:
        """Generate a comprehensive insights report"""
        report = []
        report.append("🎯 COMPREHENSIVE CAREER INSIGHTS REPORT")
        report.append("=" * 50)
        
        # Overall Score
        report.append(f"\n📊 Overall Profile Score: {insights.overall_score:.1%}")
        
        # Career Trajectory
        trajectory = insights.career_trajectory
        report.append(f"\n🚀 Career Trajectory:")
        report.append(f"   • Seniority Level: {trajectory.get('seniority_level', 'Unknown').title()}")
        report.append(f"   • Career Progression: {trajectory.get('career_progression', 'Unknown').title()}")
        report.append(f"   • Industry Focus: {trajectory.get('industry_focus', 'Unknown').title()}")
        
        # Skills Analysis
        skills = insights.skill_analysis
        report.append(f"\n💻 Skills Analysis:")
        report.append(f"   • Total Skills: {skills.get('total_skills', 0)}")
        report.append(f"   • Marketability Score: {skills.get('marketability_score', 0):.1%}")
        report.append(f"   • Core Competencies: {', '.join(skills.get('core_competencies', []))}")
        if skills.get('emerging_skills'):
            report.append(f"   • Emerging Skills: {', '.join(skills.get('emerging_skills', []))}")
        
        # Experience Insights
        exp = insights.experience_insights
        report.append(f"\n💼 Experience Analysis:")
        report.append(f"   • Total Positions: {exp.get('total_positions', 0)}")
        report.append(f"   • Leadership Indicators: {exp.get('leadership_indicators', 0)}")
        report.append(f"   • Quality Score: {exp.get('experience_quality_score', 0):.1%}")
        
        # Education
        edu = insights.education_insights
        report.append(f"\n🎓 Education Analysis:")
        report.append(f"   • Education Level: {edu.get('education_level', 'Unknown').title()}")
        report.append(f"   • Field Relevance: {edu.get('field_relevance', 'Unknown').title()}")
        
        # Personality Traits
        traits = insights.personality_traits.get('dominant_traits', [])
        if traits:
            report.append(f"\n🧠 Dominant Personality Traits:")
            for trait in traits:
                report.append(f"   • {trait.replace('_', ' ').title()}")
        
        # Strengths
        report.append(f"\n✅ Key Strengths:")
        for strength in insights.strengths:
            report.append(f"   • {strength}")
        
        # Areas for Improvement
        report.append(f"\n🎯 Areas for Improvement:")
        for improvement in insights.areas_for_improvement:
            report.append(f"   • {improvement}")
        
        # Career Recommendations
        report.append(f"\n🚀 Career Recommendations:")
        for recommendation in insights.career_recommendations:
            report.append(f"   • {recommendation}")
        
        return '\n'.join(report)
    
    def add_skill_category(self, category_name: str, skills: List[str]) -> None:
        """Dynamically add a new skill category"""
        self.config.skill_categories[category_name] = skills
        print(f"✅ Added skill category '{category_name}' with {len(skills)} skills")
    
    def add_industry_keywords(self, industry_name: str, keywords: List[str]) -> None:
        """Dynamically add industry keywords"""
        self.config.industry_keywords[industry_name] = keywords
        print(f"✅ Added industry '{industry_name}' with {len(keywords)} keywords")
    
    def update_thresholds(self, threshold_updates: Dict[str, float]) -> None:
        """Dynamically update analysis thresholds"""
        self.config.thresholds.update(threshold_updates)
        print(f"✅ Updated {len(threshold_updates)} thresholds")
    
    def update_weights(self, weight_updates: Dict[str, float]) -> None:
        """Dynamically update scoring weights"""
        self.config.weights.update(weight_updates)
        print(f"✅ Updated {len(weight_updates)} weights")
    
    def add_emerging_skills(self, skills: List[str]) -> None:
        """Dynamically add emerging skills to track"""
        self.emerging_skills.extend(skills)
        self.emerging_skills = list(set(self.emerging_skills))  # Remove duplicates
        print(f"✅ Added {len(skills)} emerging skills")
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration"""
        return {
            'skill_categories': {cat: len(skills) for cat, skills in self.config.skill_categories.items()},
            'industry_keywords': {ind: len(keywords) for ind, keywords in self.config.industry_keywords.items()},
            'seniority_levels': list(self.config.seniority_indicators.keys()),
            'personality_traits': list(self.config.personality_traits.keys()),
            'total_achievement_keywords': len(self.config.achievement_keywords),
            'total_leadership_keywords': len(self.config.leadership_keywords),
            'education_levels': list(self.config.education_levels.keys()),
            'total_relevant_fields': len(self.config.relevant_fields),
            'weights': self.config.weights,
            'thresholds': self.config.thresholds,
            'total_emerging_skills': len(self.emerging_skills)
        }
    
    def save_current_config(self, config_path: str) -> bool:
        """Save current configuration to file"""
        return ConfigLoader.save_config(self.config, config_path)


# Example usage and testing
if __name__ == "__main__":
    # Test the analyzer
    analyzer = NLPInsightsAnalyzer()
    
    # Sample resume data
    sample_resume = {
        'skills': ['Python', 'Machine Learning', 'SQL', 'JavaScript', 'React', 'AWS', 'Docker'],
        'experience': [
            {
                'title': 'Software Developer',
                'company': 'TechCorp',
                'description': 'Developed web applications using Python and React. Led a team of 3 developers.',
                'responsibilities': ['Code development', 'Team leadership', 'Project coordination']
            }
        ],
        'education': [
            {
                'degree': 'Bachelor of Computer Science',
                'field': 'Computer Science',
                'institution': 'Tech University'
            }
        ]
    }
    
    insights = analyzer.analyze_resume_sync(sample_resume)
    print(analyzer.generate_insights_report(insights))
