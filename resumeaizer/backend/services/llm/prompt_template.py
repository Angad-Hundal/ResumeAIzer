from typing import Dict, Any
import json

class PromptTemplates:
    @staticmethod
    def get_analysis_template(job_description: str) -> str:
        """
        Generates a structured prompt for comprehensive resume analysis
        """
        return f"""
        **Resume Analysis Task**

        === INPUT DATA ===
        Job Description:
        {job_description}

        === INSTRUCTIONS ===
        Analyze the provided resume against the job description and return a detailed analysis, including:

        1. **Compatibility Score (0-100)**: Provide a score based on how well the resume matches the job description. The score should be calculated with a breakdown of the following components:
           - **Skills Match**: How well the skills listed in the resume match those required in the job description.
           - **Experience Match**: How relevant the candidate's experience is to the job description.
           - **Education Match**: How well the candidate's education aligns with the requirements in the job description.

        2. **Missing Skills**: Identify missing skills, divided into:
           - **Hard Skills**: Technical skills (programming languages, tools, frameworks, etc.).
           - **Soft Skills**: Interpersonal skills (leadership, communication, etc.).
           Provide specific skills that the resume lacks but are explicitly mentioned in the job description or are commonly required for the role.

        3. **Suggested Improvements**: Offer detailed suggestions for improving the resume. Do not restrict suggestions to specific sections like “Experience” or “Skills.” Provide open-ended suggestions that could improve the overall resume, such as:
           - Suggestions for improving clarity, formatting, or tone.
           - Recommendations for highlighting key accomplishments.
           - Tips for better alignment with job requirements.

        4. **Updated Resume**: Based on the analysis and suggested improvements, provide an updated version of the resume as a PDF. Include the necessary changes and improvements directly in the file.

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
                    "hard_skills": ["skill1", "skill2", "skill3"],
                    "soft_skills": ["skillA", "skillB"]
                }},
                "suggested_improvements": [
                    {{
                        "section": "header|experience|education|skills|overall",
                        "suggestion": "specific improvement",
                        "priority": "high|medium|low",
                        "reason": "how it helps match JD"
                    }}
                ],
                "updated_resume": "base64_pdf_string_here"
            }}
        }}

        === ANALYSIS GUIDELINES ===
        1. **Score Breakdown** should consider:
           - Skill overlap percentage between resume and job description.
           - Years of relevant experience listed in the resume.
           - Education/certification requirements based on job description.

        2. **Missing Skills**:
           - Identify skills mentioned in the job description but absent from the resume.
           - Consider skills that are typically required for the role, even if not mentioned explicitly in the JD.

        3. **Suggested Improvements**:
           - Focus on improvements that will help the candidate better match the JD.
           - Prioritize suggestions that are practical and easy to implement.
           - Ensure suggestions cover both technical and soft skills as needed.

        4. **Updated Resume**:
           - Output the updated resume in PDF format encoded in base64.
           - The PDF should reflect all changes and suggested improvements made to the resume content.
        """
