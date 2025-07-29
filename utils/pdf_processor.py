import PyPDF2
import re
from typing import Optional

class PDFProcessor:
    @staticmethod
    def extract_text_from_pdf(pdf_file) -> Optional[str]:
        """Extract text from uploaded PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return PDFProcessor.clean_text(text)
        except Exception as e:
            return None
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and preprocess extracted text"""
        # Remove extra whitespaces and newlines
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s\.\,\-\(\)\@]', '', text)
        
        # Remove common PDF artifacts
        text = re.sub(r'Page \d+', '', text)
        
        return text.strip()
    
    @staticmethod
    def extract_sections(resume_text: str) -> dict:
        """Extract different sections from resume"""
        sections = {
            'experience': '',
            'education': '',
            'skills': '',
            'full_text': resume_text
        }
        
        # Simple regex patterns to identify sections
        experience_patterns = [
            r'(experience|work experience|employment|professional experience)(.*?)(?=education|skills|projects|$)',
            r'(employment history|work history)(.*?)(?=education|skills|projects|$)'
        ]
        
        education_patterns = [
            r'(education|academic background|qualifications)(.*?)(?=experience|skills|projects|$)'
        ]
        
        skills_patterns = [
            r'(skills|technical skills|core competencies|technologies)(.*?)(?=experience|education|projects|$)'
        ]
        
        text_lower = resume_text.lower()
        
        # Extract experience section
        for pattern in experience_patterns:
            match = re.search(pattern, text_lower, re.DOTALL | re.IGNORECASE)
            if match:
                sections['experience'] = match.group(2).strip()
                break
        
        # Extract education section
        for pattern in education_patterns:
            match = re.search(pattern, text_lower, re.DOTALL | re.IGNORECASE)
            if match:
                sections['education'] = match.group(2).strip()
                break
        
        # Extract skills section
        for pattern in skills_patterns:
            match = re.search(pattern, text_lower, re.DOTALL | re.IGNORECASE)
            if match:
                sections['skills'] = match.group(2).strip()
                break
        
        return sections
