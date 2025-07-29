import google.generativeai as genai
import json
from typing import Dict, Any
import os

class GeminiAnalyzer:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def analyze_resume_match(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """Analyze how well resume matches job description"""
        
        prompt = f"""
        You are an expert ATS (Applicant Tracking System) analyzer. Compare the following resume against the job description and provide a detailed analysis.

        JOB DESCRIPTION:
        {job_description}

        RESUME:
        {resume_text}

        Please provide your analysis in the following JSON format:
        {{
            "overall_match_score": <number between 0-100>,
            "matched_skills": [<list of skills from resume that match job requirements>],
            "missing_skills": [<list of important skills from job description not found in resume>],
            "strengths": [<list of candidate's key strengths for this role>],
            "weaknesses": [<list of areas where candidate falls short>],
            "recommendations": [<list of specific suggestions to improve resume for this role>],
            "keyword_matches": [<list of important keywords that matched>],
            "section_scores": {{
                "experience": <score 0-100>,
                "education": <score 0-100>,
                "skills": <score 0-100>
            }},
            "summary": "<brief overall assessment>"
        }}

        Be specific and actionable in your analysis. Focus on relevant skills, experience level, and qualifications mentioned in the job description.
        """

        try:
            response = self.model.generate_content(prompt)
            # Clean the response to extract JSON
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text[7:-3]  # Remove ```json and ```
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]  # Remove ``````
            
            return json.loads(response_text)
        
        except Exception as e:
            # Return default structure if API fails
            return {
                "overall_match_score": 0,
                "matched_skills": [],
                "missing_skills": [],
                "strengths": [],
                "weaknesses": ["Unable to analyze due to API error"],
                "recommendations": ["Please try again"],
                "keyword_matches": [],
                "section_scores": {"experience": 0, "education": 0, "skills": 0},
                "summary": f"Analysis failed: {str(e)}"
            }
    
    def generate_resume_suggestions(self, resume_text: str, job_description: str, section: str) -> str:
        """Generate specific suggestions for improving a resume section"""
        
        prompt = f"""
        Based on this job description and resume, provide 3-5 specific, actionable suggestions for improving the {section} section of the resume.

        JOB DESCRIPTION:
        {job_description}

        CURRENT RESUME:
        {resume_text}

        Focus on the {section} section and provide suggestions that would help the candidate better align with the job requirements. Be specific and practical.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Unable to generate suggestions: {str(e)}"
