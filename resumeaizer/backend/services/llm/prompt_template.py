from typing import Dict, Any
import json

class PromptTemplates:
    @staticmethod
    def get_analysis_template(resume_data: Dict[str, Any], job_description: str) -> str:
        """
        Generates a structured prompt for comprehensive resume analysis
        """
        return f"""
        **Resume Analysis Task**
        
        === INPUT DATA ===
        Resume Metadata:
        - Pages: {len(resume_data['pages'])}
        - Candidate: {resume_data['metadata'].get('author', 'N/A')}
        
        Job Description:
        {job_description}
        
        === INSTRUCTIONS ===
        Analyze this resume against the job description and provide:
        1. Compatibility Score (0-100) with detailed breakdown
        2. Missing hard skills (technical)
        3. Missing soft skills
        4. Suggested improvements with priority levels
        
        Use this exact JSON response format:
        {{
            "analysis": {{
                "compatibility": {{
                    "score": 0-100,
                    "breakdown": {{
                        "skills_match": 0-100,
                        "experience_match": 0-100,
                        "education_match": 0-100
                    }}
                }},
                "missing_skills": {{
                    "hard_skills": [],
                    "soft_skills": []
                }},
                "suggested_improvements": [
                    {{
                        "section": "header|experience|education|skills",
                        "suggestion": "specific improvement",
                        "priority": "high|medium|low",
                        "reason": "how it helps match JD"
                    }}
                ],
                "strengths": []
            }}
        }}
        
        === ANALYSIS GUIDELINES ===
        1. Score breakdown should consider:
           - Skill overlap percentage
           - Years of relevant experience
           - Education/certification requirements
        2. Missing skills should be:
           - Explicitly mentioned in JD but absent in resume
           - Industry-standard for the role
        3. Prioritize suggestions that:
           - Address critical JD requirements
           - Are easiest to implement
        """