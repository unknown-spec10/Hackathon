#!/usr/bin/env python3
"""
Streamlit Cloud Configuration Handler
Manages environment variables and secrets for cloud deployment
"""
import os
import streamlit as st

def get_config():
    """Get configuration from Streamlit secrets or environment variables"""
    config = {}
    
    # Try to get from Streamlit secrets first (cloud deployment)
    if hasattr(st, 'secrets'):
        try:
            config['GROQ_API_KEY'] = st.secrets.get('GROQ_API_KEY', '')
            config['GROQ_API_URL'] = st.secrets.get('GROQ_API_URL', 'https://api.groq.com/v1')
            config['PROJECT_NAME'] = st.secrets.get('PROJECT_NAME', 'AI Interview & Resume Analyzer')
            config['SECRET_KEY'] = st.secrets.get('SECRET_KEY', 'dev-secret-key')
            config['DATABASE_URL'] = st.secrets.get('DATABASE_URL', 'sqlite:///./hackathon.db')
            config['MAX_UPLOAD_SIZE_MB'] = int(st.secrets.get('MAX_UPLOAD_SIZE_MB', 10))
            config['ALLOWED_FILE_TYPES'] = st.secrets.get('ALLOWED_FILE_TYPES', 'pdf')
        except Exception:
            pass
    
    # Fallback to environment variables (local development)
    if not config.get('GROQ_API_KEY'):
        config['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY', '')
        config['GROQ_API_URL'] = os.getenv('GROQ_API_URL', 'https://api.groq.com/v1')
        config['PROJECT_NAME'] = os.getenv('PROJECT_NAME', 'AI Interview & Resume Analyzer')
        config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
        config['DATABASE_URL'] = os.getenv('DATABASE_URL', 'sqlite:///./hackathon.db')
        config['MAX_UPLOAD_SIZE_MB'] = int(os.getenv('MAX_UPLOAD_SIZE_MB', 10))
        config['ALLOWED_FILE_TYPES'] = os.getenv('ALLOWED_FILE_TYPES', 'pdf')
    
    return config

def is_streamlit_cloud():
    """Check if running on Streamlit Cloud"""
    return hasattr(st, 'secrets') and len(st.secrets.keys()) > 0

def setup_environment():
    """Setup environment variables for the application"""
    config = get_config()
    
    # Set environment variables for the app to use
    for key, value in config.items():
        os.environ[key] = str(value)
    
    return config
