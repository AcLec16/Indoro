import streamlit as st
import openai
from openai import OpenAI
import json
import random
import os
from typing import Dict, Any
import uuid
from datetime import datetime
from google.cloud import firestore
from google.oauth2 import service_account

# Page configuration
st.set_page_config(
    page_title="Indoro",
    page_icon="🇰🇷🇮🇳",
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
        st.error("OpenAI API configuration error. Please check your secrets configuration.")
        st.stop()
        return None

def create_survey_form():
    """Create a fully multiple-choice career survey for Indian college students exploring the Korean job market."""
    st.markdown('<div class="main-header"> 🇰🇷 Indoro - Labour Market Survey 🇮🇳 </div>', unsafe_allow_html=True)
    st.markdown("### Discover which career paths in Korea align with your skills and interests!")
    st.markdown("---")
    
    if 'survey_responses' not in st.session_state:
        st.session_state.survey_responses = {}
    
    with st.form("korea_career_survey"):
        responses = {}
        
        # Personal Information
        st.markdown('<div class="section-header">👤 Personal Information</div>', unsafe_allow_html=True)
        responses['name'] = st.text_input("1. Full Name")
        responses['college'] = st.text_input("2. College/University")
        responses['email'] = st.text_input("3. Email Address")
        
        # Academic and Career Interests
        st.markdown('<div class="section-header">🎓 Academic & Career Interests</div>', unsafe_allow_html=True)
        responses['sector_preference'] = st.radio(
            "4. Which sector are you most interested in exploring in Korea?",
            ["Technology/IT", "Finance/Consulting", "Education", "Healthcare", "Startups/Entrepreneurship", "Green/Energy", "Entertainment/Media", "Other"],
            key="sector_preference"
        )
        responses['job_stability'] = st.radio(
            "5. Which type of career path appeals to you most?",
            ["Stable and structured", "Dynamic and high-growth", "A balance of both", "Flexible/freelance options"],
            key="job_stability"
        )
        responses['work_hours'] = st.radio(
            "6. Preferred work-life balance?",
            ["Regular 9-6 schedule", "Flexible hours", "Project-based/workload varies", "Part-time/freelance"],
            key="work_hours"
        )
        
        # Skills and Technical Competence
        st.markdown('<div class="section-header">💻 Skills & Technology</div>', unsafe_allow_html=True)
        responses['tech_comfort'] = st.radio(
            "7. Comfort with technology in academics or projects?",
            ["Expert (coding, data, design tools)", "Comfortable with software tools", "Basic (Word, Excel, presentations)", "Need more practice with tech"],
            key="tech_comfort"
        )
        responses['digital_skills'] = st.radio(
            "8. What best describes your technical skills?",
            ["Programming/Data Analysis", "Software/Office tools", "Basic computer skills", "No particular skills"],
            key="digital_skills"
        )
        responses['ai_interest'] = st.radio(
            "9. Interest in AI or automation in your career?",
            ["Very interested", "Somewhat interested", "Neutral", "Not interested"],
            key="ai_interest"
        )
        
        # Language and Adaptability
        st.markdown('<div class="section-header">🗣️ Language & Adaptability</div>', unsafe_allow_html=True)
        responses['korean_language'] = st.radio(
            "10. Korean language proficiency?",
            ["Fluent", "Conversational", "Beginner/Just started", "No experience"],
            key="korean_language"
        )
        responses['cultural_adaptability'] = st.radio(
            "11. Confidence in adapting to Korean work culture?",
            ["Very confident", "Somewhat confident", "Neutral", "Not confident"],
            key="cultural_adaptability"
        )
        responses['work_environment'] = st.radio(
            "14. Preferred work environment?",
            ["Structured corporate", "Startup/innovative", "Research/academic", "Flexible/remote"],
            key="work_environment"
        )
        responses['team_work'] = st.radio(
            "15. How do you prefer to work on projects?",
            ["In a team", "Independently", "Combination of both", "Leading others"],
            key="team_work"
        )
        # Career Exploration
        st.markdown('<div class="section-header">📍 Career Exploration</div>', unsafe_allow_html=True)
        responses['industry_interest'] = st.radio(
            "16. Which industries would you like to explore first in Korea?",
            ["Technology/IT", "Finance/Consulting", "Healthcare", "Education", "Startups", "Entertainment/Media", "Green/Energy", "Other"],
            key="industry_interest"
        )
        responses['location_preference'] = st.radio(
            "17. Preferred city or region for work in Korea?",
            ["Seoul", "Busan", "Other major city", "Smaller city/rural area"],
            key="work_hours_preference"
        )
        responses['career_orientation'] = st.radio(
            "18. Which best describes your career orientation?",
            ["Innovation-focused", "Stability-focused", "Balanced", "Exploration/Flexible"],
            key="career_orientation"
        )
        st.markdown("---")
        submitted = st.form_submit_button("🎯 Get My Job Recommendations", use_container_width=True)
        
        if submitted:
            st.session_state.survey_responses = responses
            return responses
    
    return None

def generate_job_recommendation(client: OpenAI, responses: Dict[str, Any]) -> str:
    """Generate personalized job recommendation using OpenAI GPT-4o-mini (cheaper & faster)."""
    
    prompt = f"""
    You are a career counselor specializing in the South Korean job market for Indian Students.
    Based on the following survey responses, provide a concise but tailored job recommendation for an Indian Student. 
    Keep it practical, realistic, and specific to South Korea.

    Survey Responses:
    Sector Preference: {responses.get('sector_preference')}
    Job Stability vs Growth: {responses.get('job_stability')}
    Work Hours Preference: {responses.get('work_hours')}
    Korean Language Level: {responses.get('korean_language')}
    Cultural Adaptability: {responses.get('cultural_adaptability')}
    Tech Comfort: {responses.get('tech_comfort')}
    Digital Skills: {responses.get('digital_skills')}
    AI Interest: {responses.get('ai_interest')}
    Work Environment Preference: {responses.get('work_environment')}
    Team Work Preference: {responses.get('team_work')}
    Industry Interest: {responses.get('industry_interest')}
    Location Preference: {responses.get('location_preference')}
    Career Orientation: {responses.get('career_orientation')}

    Please provide:
    1. Primary Job Recommendation (specific role + Potential Companies + industry)
    2. Why This Fits (link to responses)
    3. 2–3 Alternative Options
    4. Industry Outlook (brief, 2 sentences max)
    5. Next Steps (practical advice for pursuing this career in Korea)
    6. Required Skills (short bullet list)
    7. Salary Range (Inr, realistic and atleast 30lakh per year)
    8. Mention How Indians In Korea (IIK), ISRK (Indian Student Researchers In Korea) and SkalePlus are Helpfull with several processes, as well as the Indian Embassy In Seoul

    Focus on sectors like technology, manufacturing, healthcare, education, finance, entertainment, green energy, e-commerce, and logistics.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # cheaper, optimized for scale
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,  # reduced for cost efficiency
            temperature=0.6   # slightly lower for consistency
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"Error generating recommendation: {str(e)}. Please check your API key and try again."

def display_recommendation(recommendation: str, responses: Dict[str, Any]):
    """Display the job recommendation in a styled format and save to Firebase."""
    st.markdown('<div class="recommendation-box">', unsafe_allow_html=True)
    st.markdown('<div class="recommendation-title">🎯 Your Personalized South Korea Job Recommendation</div>', unsafe_allow_html=True)
    st.markdown(recommendation)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Save to Firebase
    response_id = store_indoro_responses(responses)
    
    # Add download option


def main():
    """Main application logic."""
    # Initialize OpenAI client
    client = initialize_openai_client()
    
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
        st.error("Unable to generate recommendations. Please check the configuration.")


# Functions to interact with Firebase
def store_indoro_responses(responses):
    # Generate a Version 4 (random) UUID
    my_uuid = str(uuid.uuid4())
    print(f"Random UUID: {my_uuid}")
    key_dict = json.loads(st.secrets["FIREBASE_KEY"])
    creds = service_account.Credentials.from_service_account_info(key_dict)
    db = firestore.Client(credentials=creds, project="indoro-fe1e2")
    db.collection("responses").document(my_uuid).set(responses)
if __name__ == "__main__":
    main()
