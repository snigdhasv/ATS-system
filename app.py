import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
from dotenv import load_dotenv
from utils.pdf_processor import PDFProcessor
from utils.gemini_analyzer import GeminiAnalyzer

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="ATS Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling (replace the existing CSS section)
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #40c9ff 0%, #e81cff 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .success-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: black;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);
    }
    .warning-card {
        background: linear-gradient(135deg, #8CC9FF 0%, #FF9FE1 100%);
        color: black;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(250, 112, 154, 0.3);
    }
    .error-card {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        color: black;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(255, 154, 158, 0.3);
    }
</style>
""", unsafe_allow_html=True)



def initialize_session_state():
    """Initialize session state variables"""
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'resume_text' not in st.session_state:
        st.session_state.resume_text = None
    if 'job_description' not in st.session_state:
        st.session_state.job_description = None

def display_score_gauge(score, title):
    """Display a gauge chart for scores"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title},
        delta = {'reference': 70, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "red"},
                {'range': [50, 80], 'color': "yellow"},
                {'range': [80, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    fig.update_layout(height=300)
    return fig

def display_section_scores(section_scores):
    """Display section scores as bar chart"""
    sections = list(section_scores.keys())
    scores = list(section_scores.values())
    
    fig = px.bar(
        x=sections,
        y=scores,
        title="Section-wise Analysis",
        labels={'x': 'Resume Sections', 'y': 'Match Score'},
        color=scores,
        color_continuous_scale='RdYlGn'
    )
    fig.update_layout(height=400)
    return fig

def main():
    initialize_session_state()
    
    # Header
    st.title("🎯 ATS Resume Analyzer")
    st.markdown("Upload your resume and job description to get detailed matching analysis")
    
    # Sidebar for API key
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input(
            "Google Gemini API Key",
            type="password",
            help="Enter your Google Gemini API key"
        )
        
        if not api_key:
            st.warning("Please enter your Gemini API key to continue")
            st.markdown("[Get your API key here](https://makersuite.google.com/app/apikey)")
        
        st.markdown("---")
        st.header("📋 How to use")
        st.markdown("""
        1. Enter your Gemini API key
        2. Paste or upload job description
        3. Upload your resume PDF
        4. Click 'Analyze Resume'
        5. Review detailed results
        """)
    
    if not api_key:
        st.stop()
    
    # Initialize analyzer
    try:
        analyzer = GeminiAnalyzer(api_key)
    except Exception as e:
        st.error(f"Failed to initialize Gemini API: {str(e)}")
        st.stop()
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["📝 Input", "📊 Analysis", "💡 Suggestions"])
    
    with tab1:
        st.header("Input Your Data")
        
        # Job Description Input
        st.subheader("Job Description")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            job_desc_method = st.radio(
                "How would you like to input the job description?",
                ["Paste Text", "Upload File"],
                horizontal=True
            )
        
        if job_desc_method == "Paste Text":
            job_description = st.text_area(
                "Paste the job description here:",
                height=200,
                placeholder="Paste the complete job description..."
            )
        else:
            uploaded_jd = st.file_uploader(
                "Upload job description file",
                type=['txt', 'pdf'],
                help="Upload a text or PDF file containing the job description"
            )
            job_description = ""
            
            if uploaded_jd:
                if uploaded_jd.type == "application/pdf":
                    job_description = PDFProcessor.extract_text_from_pdf(uploaded_jd)
                else:
                    job_description = str(uploaded_jd.read(), "utf-8")
        
        st.markdown("---")
        
        # Resume Upload
        st.subheader("Resume Upload")
        uploaded_resume = st.file_uploader(
            "Upload your resume (PDF only)",
            type=['pdf'],
            help="Upload your resume in PDF format"
        )
        
        resume_text = ""
        if uploaded_resume:
            with st.spinner("Processing resume..."):
                resume_text = PDFProcessor.extract_text_from_pdf(uploaded_resume)
                
            if resume_text:
                st.success("✅ Resume processed successfully!")
                with st.expander("Preview extracted text"):
                    st.text_area("Extracted text:", resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text, height=200)
            else:
                st.error("❌ Failed to extract text from PDF. Please try a different file.")
        
        # Analysis button
        st.markdown("---")
        if st.button("🔍 Analyze Resume", type="primary", use_container_width=True):
            if not job_description or not resume_text:
                st.error("Please provide both job description and resume before analyzing.")
            else:
                with st.spinner("Analyzing resume match... This may take a few moments."):
                    st.session_state.analysis_results = analyzer.analyze_resume_match(resume_text, job_description)
                    st.session_state.resume_text = resume_text
                    st.session_state.job_description = job_description
                
                if st.session_state.analysis_results:
                    st.success("✅ Analysis completed! Check the Analysis tab for results.")
                    st.balloons()
    
    with tab2:
        if st.session_state.analysis_results:
            results = st.session_state.analysis_results
            
            st.header("Resume Analysis Results")
            
            # Overall Score Display with custom colors
            col1, col2 = st.columns([2, 1])
            with col1:
                # Enhanced gauge with custom colors
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = results['overall_match_score'],
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Overall Match Score", 'font': {'size': 20, 'color': '#EEFAFF'}},
                    delta = {'reference': 70, 'increasing': {'color': "#28a745"}, 'decreasing': {'color': "#dc3545"}},
                    gauge = {
                        'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#EEFAFF"},
                        'bar': {'color': "#262626"},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "#230C0F",
                        'steps': [
                            {'range': [0, 30], 'color': "#FF8684"},
                            {'range': [30, 60], 'color': "#FFFF7B"},
                            {'range': [60, 80], 'color': "#96EB96"},
                            {'range': [80, 100], 'color': "#4ECD65"}
                        ],
                        'threshold': {
                            'line': {'color': "#230C0F", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                fig.update_layout(
                    height=300,
                    font={'color': "#EEFAFF", 'family': "Arial"},
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>📈 Match Score</h3>
                    <h1 style="font-size: 3rem; margin: 0;">{results['overall_match_score']}%</h1>
                </div>
                """, unsafe_allow_html=True)
            
            # Display the score message and summary below the columns
            score = results['overall_match_score']
            if score >= 80:
                color_class = "success-card"
                message = "Excellent Match! 🎉"
            elif score >= 60:
                color_class = "warning-card"
                message = "Good Match 👍"
            else:
                color_class = "error-card"
                message = "Needs Improvement 📈"
            
            st.markdown(f"""
            <div class="{color_class}">
                <h3 style="margin-top: 0;">{message}</h3>
                <p style="margin-bottom: 0;">{results['summary']}</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
            
            # Section Scores
            st.subheader("📋 Section-wise Analysis")
            if results['section_scores']:
                sections = list(results['section_scores'].keys())
                scores = list(results['section_scores'].values())
                
                # Create colorful bar chart
                colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=sections,
                        y=scores,
                        marker_color=colors[:len(sections)],
                        text=scores,
                        textposition='auto',
                        textfont=dict(color='white', size=14, family='Arial Black')
                    )
                ])
                
                fig.update_layout(
                    title={
                        'text': 'Section Performance Analysis',
                        'x': 0.5,
                        'font': {'size': 20, 'color': '#2E86AB'}
                    },
                    xaxis_title="Resume Sections",
                    yaxis_title="Match Score (%)",
                    height=400,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font={'color': '#2E86AB'},
                    yaxis=dict(range=[0, 100])
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Skills Analysis
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("✅ Matched Skills")
                if results['matched_skills']:
                    for skill in results['matched_skills'][:10]:  # Show top 10
                        st.success(f"• {skill}")
                else:
                    st.info("No specific skill matches found")
            
            with col2:
                st.subheader("❌ Missing Skills")
                if results['missing_skills']:
                    for skill in results['missing_skills'][:10]:  # Show top 10
                        st.error(f"• {skill}")
                else:
                    st.info("No critical missing skills identified")
            
            # Keyword Matches
            if results['keyword_matches']:
                st.subheader("🔍 Keyword Analysis")
                keywords_df = pd.DataFrame({
                    'Keywords': results['keyword_matches'][:20],  # Top 20 keywords
                    'Status': ['Matched'] * len(results['keyword_matches'][:20])
                })
                st.dataframe(keywords_df, use_container_width=True)
            
            # Strengths and Weaknesses
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("💪 Strengths")
                if results['strengths']:
                    for strength in results['strengths']:
                        st.markdown(f"• **{strength}**")
                else:
                    st.info("No specific strengths identified")
            
            with col2:
                st.subheader("⚠️ Areas for Improvement")
                if results['weaknesses']:
                    for weakness in results['weaknesses']:
                        st.markdown(f"• {weakness}")
                else:
                    st.info("No major weaknesses identified")
        
        else:
            st.info("👆 Please analyze a resume first using the Input tab")


    
    with tab3:
        if st.session_state.analysis_results and st.session_state.resume_text and st.session_state.job_description:
            st.header("Improvement Suggestions")
            
            # General Recommendations
            st.subheader("🎯 General Recommendations")
            if st.session_state.analysis_results['recommendations']:
                for i, rec in enumerate(st.session_state.analysis_results['recommendations'], 1):
                    st.markdown(f"**{i}.** {rec}")
            
            st.markdown("---")
            
            # Section-specific suggestions
            st.subheader("📝 Section-specific Suggestions")
            
            sections = ['experience', 'skills', 'education']
            
            for section in sections:
                with st.expander(f"Improve {section.title()} Section"):
                    if st.button(f"Generate {section.title()} Suggestions", key=f"btn_{section}"):
                        with st.spinner(f"Generating {section} suggestions..."):
                            suggestions = analyzer.generate_resume_suggestions(
                                st.session_state.resume_text,
                                st.session_state.job_description,
                                section
                            )
                            st.markdown(suggestions)
            
            # Export Options
            st.markdown("---")
            st.subheader("📤 Export Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📋 Copy Analysis Summary", use_container_width=True):
                    summary_text = f"""
                    ATS Resume Analysis Summary
                    ===========================
                    Overall Match Score: {st.session_state.analysis_results['overall_match_score']}%
                    
                    Summary: {st.session_state.analysis_results['summary']}
                    
                    Matched Skills: {', '.join(st.session_state.analysis_results['matched_skills'][:5])}
                    Missing Skills: {', '.join(st.session_state.analysis_results['missing_skills'][:5])}
                    
                    Top Recommendations:
                    {chr(10).join([f"• {rec}" for rec in st.session_state.analysis_results['recommendations'][:3]])}
                    """
                    st.code(summary_text)
            
            with col2:
                # Create downloadable report
                analysis_data = {
                    'Analysis Date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Overall Score': st.session_state.analysis_results['overall_match_score'],
                    'Summary': st.session_state.analysis_results['summary'],
                    'Matched Skills': ', '.join(st.session_state.analysis_results['matched_skills']),
                    'Missing Skills': ', '.join(st.session_state.analysis_results['missing_skills']),
                    'Recommendations': '\n'.join(st.session_state.analysis_results['recommendations'])
                }
                
                df_report = pd.DataFrame([analysis_data])
                csv_data = df_report.to_csv(index=False)
                
                st.download_button(
                    label="📥 Download Report (CSV)",
                    data=csv_data,
                    file_name=f"ats_analysis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        else:
            st.info("👆 Please complete the analysis first to see suggestions")

if __name__ == "__main__":
    main()
