# Configuration Files

## nlp_insights_config.json

Main configuration file for the NLP Insights Analyzer. Contains:

### Skill Categories
- **programming**: Programming languages and frameworks
- **data_science**: ML, data analysis, and visualization tools
- **cloud_devops**: Cloud platforms, containerization, CI/CD
- **web_development**: Frontend and backend web technologies
- **mobile_development**: Mobile app development platforms
- **ai_ml**: AI/ML specific technologies and frameworks
- **blockchain**: Blockchain and cryptocurrency technologies
- **cybersecurity**: Security tools and methodologies
- **soft_skills**: Leadership, communication, and interpersonal skills

### Seniority Indicators
Maps experience levels to common job title keywords:
- **junior**: Entry-level positions
- **mid**: Mid-level positions
- **senior**: Senior-level positions
- **executive**: Leadership and C-level positions

### Industry Keywords
Industry-specific terminology for job classification.

### Personality Traits
Keywords that indicate different personality characteristics.

### Achievement & Leadership Keywords
Words that indicate accomplishments and leadership experience.

### Education Levels
Mapping of education keywords to standardized levels:
- **high_school**: Secondary education
- **bachelor**: Undergraduate degree
- **master**: Graduate degree
- **phd**: Doctoral degree

### Weights & Thresholds
Scoring parameters for the analysis algorithm.

## Usage

This configuration is automatically loaded by the `NLPInsightsAnalyzer` class. You can modify categories and keywords to adapt the analysis to your specific needs.

The AI-powered dynamic keyword generation system supplements this static configuration with real-time keyword discovery.
