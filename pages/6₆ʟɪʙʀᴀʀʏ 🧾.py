import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import random
from datetime import datetime
import json

# # Initial authentication check
# if 'signed_in' not in st.session_state or not st.session_state.signed_in:
#     st.warning("🔒 Please log in to access this page.")
#     st.stop()

class EnhancedAdaptiveLearning:
    def __init__(self):
        # Advanced page configuration
        st.set_page_config(
            page_title="AI-Powered Adaptive Learning",
            page_icon="🧠",
            layout="wide",
            initial_sidebar_state="auto",
            menu_items={
                'Get Help': 'https://www.xai.com/help',
                'Report a bug': None,
                'About': "AI-Powered Learning Platform by xAI"
            }
        )
        
        # Initialize session state
        if 'user_profile' not in st.session_state:
            st.session_state.user_profile = {'preferences': [], 'history': []}
        
        # Base data URL
        self.EXCEL_URL = "https://raw.githubusercontent.com/Suriyakumarvijayanayagam/Personalized_learning_enhanced_with_AI/main/chennal.xlsx"
        self.load_initial_data()

    def load_initial_data(self):
        """Load base data and initialize dynamic content"""
        try:
            self.df = pd.read_excel(self.EXCEL_URL)
            self.categorized_content = self.process_content(self.df)
        except Exception as e:
            st.error(f"Data loading error: {e}")
            self.categorized_content = {}

    def process_content(self, df):
        """Process and categorize content with additional metadata"""
        categorized = {}
        for _, row in df.iterrows():
            subject = str(row['subject ']).strip()
            content = {
                'videos': [{'name': str(row['channel name ']).strip(), 
                          'link': str(row['channel link']).strip(), 
                          'last_updated': datetime.now().isoformat()}],
                'websites': [{'name': str(row[' website name ']).strip(), 
                            'link': str(row['website link']).strip(),
                            'last_updated': datetime.now().isoformat()}]
            }
            if subject not in categorized:
                categorized[subject] = {'videos': [], 'websites': []}
            categorized[subject]['videos'].extend([v for v in content['videos'] if v['name']])
            categorized[subject]['websites'].extend([w for w in content['websites'] if w['name']])
        return categorized

    def fetch_dynamic_content(self, subject, content_type):
        """Dynamically fetch additional content using web scraping"""
        try:
            search_query = f"{subject} educational {content_type}"
            response = requests.get(f"https://www.google.com/search?q={search_query}")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            new_resources = []
            for link in soup.find_all('a', href=True)[:5]:  # Top 5 results
                href = link['href']
                if 'http' in href and 'google' not in href:
                    new_resources.append({
                        'name': link.text[:50] or f"{content_type.capitalize()} Resource",
                        'link': href,
                        'last_updated': datetime.now().isoformat(),
                        'source': 'dynamic'
                    })
            return new_resources
        except Exception as e:
            st.warning(f"Dynamic fetch failed: {e}")
            return []

    def get_personalized_recommendations(self, subject, content_type):
        """AI-driven content recommendations based on user profile"""
        base_content = self.categorized_content.get(subject, {}).get(content_type, [])
        
        # Add dynamic content if less than 5 resources
        if len(base_content) < 5:
            dynamic_content = self.fetch_dynamic_content(subject, content_type)
            base_content.extend(dynamic_content)
        
        # Sort by relevance based on user preferences
        if st.session_state.user_profile['preferences']:
            base_content.sort(key=lambda x: random.random())  # Simple randomization for now
        return base_content[:10]  # Return top 10 recommendations

    def render_ui(self):
        """Render enhanced UI with advanced features"""
        # Custom CSS
        st.markdown("""
        <style>
        .main-title { font-size: 3.5em; color: #1a5f7a; text-align: center; margin-bottom: 40px; }
        .subject-container { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 30px; border-radius: 15px; }
        .resource-card { background: white; padding: 20px; border-radius: 10px; margin: 10px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1); transition: all 0.3s; }
        .resource-card:hover { transform: translateY(-5px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        .preference-chip { background: #e8f1f2; padding: 5px 15px; border-radius: 20px; margin: 5px; }
        </style>
        """, unsafe_allow_html=True)

        # Header
        st.markdown('<h1 class="main-title">🧠 AI-Powered Learning Hub</h1>', unsafe_allow_html=True)
        
        # Sidebar for user preferences
        with st.sidebar:
            st.subheader("Personalization Settings")
            learning_prefs = st.multiselect(
                "Learning Preferences",
                ["Quick Videos", "In-depth Articles", "Interactive Content", "Beginner", "Advanced"],
                default=st.session_state.user_profile['preferences']
            )
            st.session_state.user_profile['preferences'] = learning_prefs
            
            if st.button("Save Preferences"):
                st.success("Preferences saved!")

        # Main content
        st.markdown('<div class="subject-container">', unsafe_allow_html=True)
        
        # Subject selection with autocomplete
        subjects = sorted(self.categorized_content.keys())
        subject = st.selectbox("Choose Your Subject", subjects, 
                             help="Start typing to filter subjects")
        
        # Content type selection with modern buttons
        col1, col2 = st.columns(2)
        with col1:
            show_videos = st.button("🎥 Video Content", use_container_width=True)
        with col2:
            show_websites = st.button("🌐 Web Resources", use_container_width=True)

        # Display personalized content
        if show_videos or show_websites:
            content_type = 'videos' if show_videos else 'websites'
            resources = self.get_personalized_recommendations(subject, content_type)
            
            st.markdown(f"### Recommended {content_type.capitalize()} for {subject}")
            for resource in resources:
                st.markdown(f"""
                <div class="resource-card">
                    <h4>{resource['name']}</h4>
                    <p>Last Updated: {resource['last_updated'].split('T')[0]}</p>
                    <a href="{resource['link']}" target="_blank">
                        <button style="background: #1a5f7a; color: white; border: none; padding: 10px 20px; border-radius: 5px;">
                            Explore Now
                        </button>
                    </a>
                </div>
                """, unsafe_allow_html=True)
                # Track user interaction
                st.session_state.user_profile['history'].append({
                    'subject': subject,
                    'resource': resource['name'],
                    'type': content_type,
                    'timestamp': datetime.now().isoformat()
                })

        st.markdown('</div>', unsafe_allow_html=True)

    def run(self):
        """Run the application"""
        st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True)
        self.render_ui()

if __name__ == "__main__":
    app = EnhancedAdaptiveLearning()
    app.run()
