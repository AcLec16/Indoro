import streamlit as st
import openai
from openai import OpenAI
import json
import os
from typing import Dict, Any
import uuid
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="South Korea Job Matcher",
    page_icon="🇰🇷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f4e79;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .section-header {
        color: #2c5282;
        font-size: 1.3rem;
        font-weight: bold;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-left: 4px solid #4299e1;
        padding-left: 1rem;
    }
    .question-container {
        background-color: #f7fafc;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .recommendation-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-top: 2rem;
    }
    .recommendation-title {
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .stButton > button {
        background-color: #4299e1;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 2rem;
        font-size: 1.1rem;
    }
    .stButton > button:hover {
        background-color: #3182ce;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

def initialize_openai_client():
    """Initialize OpenAI client with API key from Streamlit secrets."""
    try:
        # Get API key from Streamlit secrets
        api_key = st.secrets["OPENAI_API_KEY"]
        client = OpenAI(api_key=api_key)
        return client
    except Exception as e:
        st.error("⚠️ OpenAI API configuration error. Please check your secrets configuration.")
        st.stop()
        return None

def create_survey_form():
    """Create the 15-question PESTLE survey form with simple answers."""
    st.markdown('<div class="main-header">🇰🇷 South Korea Job Matcher</div>', unsafe_allow_html=True)
    st.markdown("### Discover your ideal career path in South Korea's dynamic job market!")
    st.markdown("---")
    
    # Initialize session state for responses
    if 'survey_responses' not in st.session_state:
        st.session_state.survey_responses = {}
    
    with st.form("pestle_survey"):
        responses = {}
        
        # POLITICAL FACTORS (3 questions)
        st.markdown('<div class="section-header">🏛️ Political & Legal</div>', unsafe_allow_html=True)
        
        responses['visa_status'] = st.radio(
            "1. What is your work authorization status in South Korea?",
            ["Korean citizen", "Have work visa", "Need work visa", "Student visa"],
            key="q1"
        )
        
        responses['sector_preference'] = st.radio(
            "2. Which sector do you prefer?",
            ["Government/Public", "Private companies", "Startups", "No preference"],
            key="q2"
        )
        
        responses['work_regulations'] = st.radio(
            "3. How do you feel about following strict workplace rules?",
            ["I like clear rules", "It's okay", "I prefer flexibility", "I don't like many rules"],
            key="q3"
        )
        
        # ECONOMIC FACTORS (3 questions)
        st.markdown('<div class="section-header">💰 Economic Priorities</div>', unsafe_allow_html=True)
        
        responses['salary_priority'] = st.radio(
            "4. What matters most to you about salary?",
            ["High starting salary", "Steady growth over time", "Just enough to live well", "Money isn't my priority"],
            key="q4"
        )
        
        responses['work_hours'] = st.radio(
            "5. What work schedule do you prefer?",
            ["Standard 9-6", "Flexible hours", "Long hours, high pay", "Part-time work"],
            key="q5"
        )
        
        responses['job_security'] = st.radio(
            "6. What's more important to you?",
            ["Job security", "Career growth", "Both equally", "Work-life balance"],
            key="q6"
        )
        
        # SOCIAL FACTORS (3 questions)
        st.markdown('<div class="section-header">👥 Social & Cultural</div>', unsafe_allow_html=True)
        
        responses['korean_language'] = st.radio(
            "7. How well do you speak Korean?",
            ["Native/Fluent", "Good (can work in Korean)", "Basic (need help)", "Beginner/None"],
            key="q7"
        )
        
        responses['work_style'] = st.radio(
            "8. What work environment do you prefer?",
            ["Traditional Korean office", "International company", "Modern startup", "Remote work"],
            key="q8"
        )
        
        responses['team_work'] = st.radio(
            "9. How do you like to work?",
            ["In a team", "Independently", "Mix of both", "Leading others"],
            key="q9"
        )
        
        # TECHNOLOGICAL FACTORS (3 questions)
        st.markdown('<div class="section-header">💻 Technology Skills</div>', unsafe_allow_html=True)
        
        responses['tech_skills'] = st.radio(
            "10. How would you describe your tech skills?",
            ["Expert (programming, etc.)", "Good (comfortable with software)", "Basic (email, office)", "Need help with technology"],
            key="q10"
        )
        
        responses['ai_interest'] = st.radio(
            "11. How do you feel about AI and automation?",
            ["Very interested", "Somewhat interested", "Neutral", "Prefer traditional work"],
            key="q11"
        )
        
        responses['digital_comfort'] = st.radio(
            "12. How comfortable are you learning new software?",
            ["Love learning new tools", "Comfortable if needed", "Prefer familiar tools", "Avoid new technology"],
            key="q12"
        )
        
        # ENVIRONMENTAL FACTORS (3 questions)
        st.markdown('<div class="section-header">🌱 Environmental & Lifestyle</div>', unsafe_allow_html=True)
        
        responses['sustainability'] = st.radio(
            "13. How important is environmental work to you?",
            ["Very important", "Somewhat important", "Not important", "I don't care"],
            key="q13"
        )
        
        responses['work_location'] = st.radio(
            "14. Where would you prefer to work in Korea?",
            ["Seoul", "Busan", "Other major city", "Smaller city/rural"],
            key="q14"
        )
        
        responses['industry_interest'] = st.radio(
            "15. Which industry interests you most?",
            ["Technology/IT", "Manufacturing", "Healthcare", "Education", "Entertainment/Media", "Finance", "Other"],
            key="q15"
        )
        
        # Submit button
        st.markdown("---")
        submitted = st.form_submit_button("🎯 Get My Job Recommendations", use_container_width=True)
        
        if submitted:
            st.session_state.survey_responses = responses
            return responses
    
    return None

def generate_job_recommendation(client: OpenAI, responses: Dict[str, Any]) -> str:
    """Generate personalized job recommendation using OpenAI GPT-4."""
    
    # Create a comprehensive prompt based on survey responses
    prompt = f"""
    Based on the following PESTLE survey responses from a job seeker interested in working in South Korea, 
    provide a personalized job recommendation. Consider the current South Korean job market trends, 
    major industries, and realistic opportunities.

    Survey Responses:
    - Visa Status: {responses.get('visa_status')}
    - Sector Preference: {responses.get('sector_preference')}
    - Regulatory Comfort: {responses.get('regulatory_comfort')}/5
    - Salary Importance: {responses.get('salary_importance')}
    - Work Hours Preference: {responses.get('work_hours')}
    - Job Stability vs Growth: {responses.get('job_stability')}
    - Korean Language Level: {responses.get('korean_language')}
    - Work Environment Preferences: {responses.get('work_environment')}
    - Cultural Adaptability: {responses.get('cultural_adaptability')}/5
    - Technology Comfort: {responses.get('tech_comfort')}
    - Digital Skills: {responses.get('digital_skills')}
    - AI Interest Level: {responses.get('ai_interest')}/5
    - Compliance Work Attitude: {responses.get('compliance_work')}
    - Sustainability Importance: {responses.get('sustainability_interest')}
    - Green Sector Interests: {responses.get('green_sectors')}

    Please provide:
    1. **Primary Job Recommendation**: Specific job title and industry
    2. **Why This Fits**: Explanation based on their responses
    3. **Alternative Options**: 2-3 other suitable job roles
    4. **Industry Insights**: Brief overview of the recommended sector in South Korea
    5. **Next Steps**: Practical advice for pursuing this career path in South Korea
    6. **Salary Expectations**: Realistic salary ranges in KRW
    7. **Required Skills**: Key skills they should develop

    Focus on realistic opportunities in South Korea's major industries like:
    - Technology (Samsung, LG, Naver, Kakao)
    - Manufacturing (automotive, shipbuilding, steel)
    - Healthcare and eldercare
    - Education (English teaching, international schools)
    - Finance and consulting
    - Entertainment and media (K-pop, gaming)
    - Green energy and sustainability
    - E-commerce and logistics

    Keep the response practical, encouraging, and specific to the South Korean market.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert career counselor specializing in the South Korean job market. Provide detailed, practical, and culturally-aware job recommendations."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error generating recommendation: {str(e)}. Please check your API key and try again."

def display_recommendation(recommendation: str, responses: Dict[str, Any]):
    """Display the job recommendation in a styled format and save to Firebase."""
    st.markdown('<div class="recommendation-box">', unsafe_allow_html=True)
    st.markdown('<div class="recommendation-title">🎯 Your Personalized South Korea Job Recommendation</div>', unsafe_allow_html=True)
    st.markdown(recommendation)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Save to Firebase
    response_id = save_to_firebase(responses, recommendation)
    st.success(f"✅ Your responses have been saved! Reference ID: {response_id[:8]}...")
    
    # Add download option
    st.download_button(
        label="📄 Download Recommendation",
        data=recommendation,
        file_name="korea_job_recommendation.txt",
        mime="text/plain",
        use_container_width=True
    )

def main():
    """Main application logic."""
    # Initialize OpenAI client
    client = initialize_openai_client()
    
    # Sidebar information
    st.sidebar.markdown("### 📋 About This Survey")
    st.sidebar.markdown("""
    This survey uses the **PESTLE framework** to assess:
    - **P**olitical factors (visa, sector preferences)
    - **E**conomic factors (salary, work-life balance)
    - **S**ocial factors (culture, language, environment)
    - **T**echnological factors (digital skills, AI interest)
    - **L**egal factors (compliance comfort)
    - **E**nvironmental factors (sustainability focus)
    """)
    
    st.sidebar.markdown("### 🇰🇷 About South Korea's Job Market")
    st.sidebar.markdown("""
    Key industries include:
    - **Technology**: Samsung, LG, Naver, Kakao
    - **Automotive**: Hyundai, Kia
    - **Entertainment**: K-pop, gaming, media
    - **Healthcare**: Aging society opportunities
    - **Green Energy**: Government sustainability push
    - **Education**: English teaching, international schools
    """)
    
    # Main survey form
    responses = create_survey_form()
    
    # Process responses if survey is submitted
    if responses and client:
        with st.spinner("🤖 Analyzing your responses and generating personalized recommendations..."):
            recommendation = generate_job_recommendation(client, responses)
            display_recommendation(recommendation, responses)
            
        # Option to retake survey
        if st.button("🔄 Take Survey Again", use_container_width=True):
            st.session_state.survey_responses = {}
            st.experimental_rerun()
    
    elif responses and not client:
        st.error("⚠️ Unable to generate recommendations. Please check the configuration.")

if __name__ == "__main__":
    main()