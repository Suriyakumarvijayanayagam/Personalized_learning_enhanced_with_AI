import streamlit as st
import google.generativeai as genai
import logging
import json
import requests
import time
from datetime import datetime
import pandas as pd
import plotly.express as px
from pathlib import Path
import sqlite3
import hashlib


# # Check if the user is logged in
# if 'signed_in' not in st.session_state or not st.session_state.signed_in:
#     st.warning("🔒You must be logged in to access this page.")
#     st.stop()  # Stop rendering the rest of the page

# Load API keys
def load_config():
    try:
        with open('api.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("API configuration file not found. Please create api.json")
        return None

# Initialize folders
def init_folders():
    Path("logs").mkdir(exist_ok=True)
    Path("downloads").mkdir(exist_ok=True)

class LearningSession:
    def __init__(self, user_id):
        self.user_id = user_id
        self.session_id = hashlib.md5(f"{user_id}{time.time()}".encode()).hexdigest()
        self.start_time = datetime.now()
        self.topics = []
        self.ratings = []
    
    def end_session(self):
        avg_rating = sum(self.ratings) / len(self.ratings) if self.ratings else 0
        conn = sqlite3.connect('learning_history.db')
        c = conn.cursor()
        c.execute('''INSERT INTO learning_sessions VALUES (?, ?, ?, ?, ?, ?)''',
                 (self.session_id, self.user_id, self.start_time.isoformat(),
                  datetime.now().isoformat(), len(self.topics), avg_rating))
        conn.commit()
        conn.close()

def main():
    init_folders()
    # init_db()
    config = load_config()
    
    if not config:
        return

    # # Configure APIs
    # genai.configure(api_key=config['api'])
    # CUSTOM_SEARCH_API_KEY = config['custom_search_api']
    # SEARCH_ENGINE_ID = config['search_engine_id']
    # YOUTUBE_API_KEY = config['youtube_api']
    # model = genai.GenerativeModel('gemini-pro')
    # Load API keys from Streamlit secrets
    API = st.secrets["API"]
    CUSTOM_SEARCH_API_KEY = st.secrets["CUSTOM_SEARCH_API_KEY"]
    SEARCH_ENGINE_ID = st.secrets["SEARCH_ENGINE_ID"]
    YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]

    # Configure Gemini API
    genai.configure(api_key=API)
    model = genai.GenerativeModel("gemini-pro")
    # Setup session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'learning_styles' not in st.session_state:
        st.session_state.learning_styles = {
            'visual': False,
            'auditory': False,
            'kinesthetic': False
        }
    if 'user_id' not in st.session_state:
        st.session_state.user_id = hashlib.md5(str(time.time()).encode()).hexdigest()
    if 'session' not in st.session_state:
        st.session_state.session = LearningSession(st.session_state.user_id)
    if 'topic_history' not in st.session_state:
        st.session_state.topic_history = []

    # Page Configuration
    st.set_page_config(page_title="ᴀᴅᴀᴘᴛɪᴠᴇ ʟᴇᴀʀɴɪɴɢ ɢᴇɴᴇʀᴀᴛᴏʀ ", page_icon="🌎",layout="wide")
    
    # Sidebar Configuration
    with st.sidebar:
        st.title("​🇱​​🇪​​🇦​​🇷​​🇳​​🇮​​🇳​​🇬​ ​🇨​​🇴​​🇳​​🇹​​🇷​​🇴​​🇱​​🇸​ ֎ ")
        
        # Learning Style Selection
        st.subheader("​🇨​​🇭​​🇴​​🇴​​🇸​​🇪​ ​🇱​​🇪​​🇦​​🇷​​🇳​​🇮​​🇳​​🇬​ ​🇸​​🇹​​🇾​​🇱​​🇪​ 🔝")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Visual 🖼️", use_container_width=True):
                st.session_state.learning_styles = {k: k == 'visual' for k in st.session_state.learning_styles}
        with col2:
            if st.button("Auditory 🎧", use_container_width=True):
                st.session_state.learning_styles = {k: k == 'auditory' for k in st.session_state.learning_styles}
        with col3:
            if st.button("Kinesthetic 🤹", use_container_width=True):
                st.session_state.learning_styles = {k: k == 'kinesthetic' for k in st.session_state.learning_styles}

        # Topic Input
        st.subheader("​🇪​​🇳​​🇹​​🇪​​🇷​ ​🇹​​🇴​​🇵​​🇮​​🇨​ 🧑‍💻")
        user_prompt = st.text_area(
            "​🇼​​🇭​​🇦​​🇹​ ​🇼​​🇴​​🇺​​🇱​​🇩​ ​🇾​​🇴​​🇺​ ​🇱​​🇮​​🇰​​🇪​ ​🇹​​🇴​ ​🇱​​🇪​​🇦​​🇷​​🇳​ ​🇦​​🇧​​🇴​​🇺​​🇹​? 📜",
            value="", height=100,
            placeholder="​🇹​​🇾​​🇵​​🇪​ ​🇾​​🇴​​🇺​​🇷​ ​🇶​​🇺​​🇪​​🇷​​🇾​ ​🇭​​🇪​​🇷​​🇪​... 🌐"
        )

        # Difficulty Level
        difficulty = st.select_slider(
            "Select Difficulty Level",
            options=["Beginner", "Intermediate", "Advanced"],
            value="Intermediate"
        )

        # Submit Button
        if st.button("​🇬​​🇪​​🇳​​🇪​​🇷​​🇦​​🇹​​🇪​ ​🇱​​🇪​​🇦​​🇷​​🇳​​🇮​​🇳​​🇬​ ​🇨​​🇴​​🇳​​🇹​​🇪​​🇳​​🇹​ 🌍", use_container_width=True):
            if user_prompt and any(st.session_state.learning_styles.values()):
                process_learning_request(user_prompt, difficulty, model)
            else:
                st.warning("P​​​🇱​​🇪​​🇦​​🇸​​🇪​ ​🇸​​🇪​​🇱​​🇪​​🇨​​🇹​ ​🇦​ ​🇱​​🇪​​🇦​​🇷​​🇳​​🇮​​🇳​​🇬​ ​🇸​​🇹​​🇾​​🇱​​🇪​ ​🇦​​🇳​​🇩​ ​🇪​​🇳​​🇹​​🇪​​🇷​ ​🇦​ ​🇹​​🇴​​🇵​​🇮​​🇨​.")

    # Main Content Area
    st.title("ᴀᴅᴀᴘᴛɪᴠᴇ ʟᴇᴀʀɴɪɴɢ ɢᴇɴᴇʀᴀᴛᴏʀ 💡")
    
    # Display current learning session info
    st.sidebar.markdown("---")
    st.sidebar.subheader("Session Statistics")
    display_session_stats()

    # Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Analytics Dashboard
    if st.session_state.topic_history:
        st.markdown("---")
        st.subheader("Learning Analytics")
        display_analytics()

def process_learning_request(prompt, difficulty, model):
    # Log the interaction
    log_user_interaction(prompt)
    
    # Update session data
    st.session_state.session.topics.append(prompt)
    st.session_state.topic_history.append({
        'timestamp': datetime.now(),
        'topic': prompt,
        'difficulty': difficulty
    })

    # Generate learning content based on style
    style = next(k for k, v in st.session_state.learning_styles.items() if v)
    
    # Construct enhanced prompt
    enhanced_prompt = f"""
    Create a {difficulty}-level explanation of '{prompt}' for a {style} learner.
    
    Include:
    1. Main concepts and definitions
    2. Real-world applications
    3. Practice exercises or activities
    4. Summary and key takeaways
    5. fetch the resources form the web based on the type of learner
    6. provide real time example and easy ways to understand
    7. provide the clear explanantion and examples 
    Format the response in a structured, easy-to-follow manner.
    """

    # Generate and display content
    try:
        response = model.generate_content(enhanced_prompt)
        if response and hasattr(response, 'text'):
            display_learning_content(response.text, style, prompt)
            
            # Add feedback mechanism
            feedback_container = st.container()
            with feedback_container:
                st.markdown("---")
                st.subheader("Was this helpful?")
                col1, col2, col3 = st.columns([1,1,3])
                with col1:
                    if st.button("👍 Yes"):
                        save_feedback(5, prompt, style)
                with col2:
                    if st.button("👎 No"):
                        save_feedback(1, prompt, style)
                with col3:
                    feedback_text = st.text_input("Additional feedback (optional)")
                    if feedback_text:
                        save_detailed_feedback(feedback_text, prompt, style)
        else:
            st.error("Failed to generate content. Please try again.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        logging.error(f"Error generating content: {str(e)}")


        
def search_images(query, max_images=3):
    """
    Search for images using Google Custom Search API
    """
    api=st.secrets["GEMINI_API_KEY"]
    try:
        key=st.secrets["GEMINI_API_KEY"]
        search_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "q": query,
            "cx": "9745cbd96dd164562",
            "key": "api",
            "searchType": "image",
            "num": max_images,
            "safe": "active"
        }
        
        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        results = response.json().get("items", [])
        if results:
            st.subheader("📸 Related Visual References")
            cols = st.columns(min(max_images, len(results)))
            
            for idx, (item, col) in enumerate(zip(results, cols)):
                with col:
                    st.image(
                        item['link'],
                        caption=f"Image {idx + 1}",
                        use_column_width=True
                    )
                    with st.expander("Image Details"):
                        st.write(f"Title: {item.get('title', 'N/A')}")
                        st.write(f"Source: {item.get('displayLink', 'N/A')}")
        else:
            st.info("No relevant images found for this topic.")
            
    except requests.RequestException as e:
        st.warning(f"Failed to fetch images: {str(e)}")
        logging.error(f"Image search error: {str(e)}")
    except Exception as e:
        st.error(f"An unexpected error occurred while fetching images: {str(e)}")
        logging.error(f"Unexpected image search error: {str(e)}")

def search_youtube_videos(query, max_videos=2):
    """
    Search for YouTube videos using YouTube Data API
    """
    try:
        search_url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": query,
            "key": st.secrets["YOUTUBE_API_KEY"],
            "type": "video",
            "maxResults": max_videos,
            "videoEmbeddable": "true",
            "relevanceLanguage": "en",
            "safeSearch": "moderate"
        }
        
        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()
        
        results = response.json().get("items", [])
        if results:
            st.subheader("🎥 Related Educational Videos")
            for item in results:
                video_id = item['id']['videoId']
                video_title = item['snippet']['title']
                
                # Create an expander for each video
                with st.expander(f"📺 {video_title}"):
                    st.video(f"https://www.youtube.com/watch?v={video_id}")
                    st.write(f"Description: {item['snippet']['description'][:200]}...")
                    st.write(f"Channel: {item['snippet']['channelTitle']}")
        else:
            st.info("No relevant videos found for this topic.")
            
    except requests.RequestException as e:
        st.warning(f"Failed to fetch videos: {str(e)}")
        logging.error(f"YouTube search error: {str(e)}")
    except Exception as e:
        st.error(f"An unexpected error occurred while fetching videos: {str(e)}")
        logging.error(f"Unexpected YouTube search error: {str(e)}")

def display_media_content(topic):
    """
    Display both images and videos for a given topic with error handling
    """
    try:
        with st.spinner("Fetching visual content..."):
            search_images(topic)
        with st.spinner("Fetching video content..."):
            search_youtube_videos(topic)
    except Exception as e:
        st.error("Failed to load media content. Please try again later.")
        logging.error(f"Media content error: {str(e)}")

# Update the display_learning_content function to use the new display_media_content
def display_learning_content(content, style, topic):
    """
    Display the learning content with appropriate media based on learning style
    """
    # Add to message history
    assistant_message = {
        "role": "assistant",
        "content": content,
        "timestamp": time.time()
    }
    st.session_state.messages.append(assistant_message)
    
    # Display content
    with st.chat_message("assistant"):
        st.write(content)
        
        # Additional style-specific features
        if style == 'visual':
            display_media_content(topic)
        elif style == 'auditory':
            # Placeholder for audio feature
            st.info("🎧 Audio features coming soon!")
        elif style == 'kinesthetic':
            display_interactive_elements(topic)

def display_learning_content(content, style, topic):
    # Add to message history
    assistant_message = {
        "role": "assistant",
        "content": content,
        "timestamp": time.time()
    }
    st.session_state.messages.append(assistant_message)
    
    # Display content
    with st.chat_message("assistant"):
        st.write(content)
        
        # Additional style-specific features
        if style == 'visual':
            search_images(topic)
            search_youtube_videos(topic)
        elif style == 'auditory':
            st.audio("downloads/audio.mp3")
             # Placeholder for audio feature
        elif style == 'kinesthetic':
            display_interactive_elements(topic)

def display_interactive_elements(topic):
    st.subheader("Interactive Practice")
    # Add interactive elements like quizzes, exercises, etc.
    with st.expander("Practice Exercise"):
        st.write("Complete the following exercise to reinforce your learning:")
        # Add interactive components here

def display_session_stats():
    topics_count = len(st.session_state.session.topics)
    time_spent = datetime.now() - st.session_state.session.start_time
    
    st.sidebar.metric("Topics Covered", topics_count)
    st.sidebar.metric("Time Spent", f"{time_spent.seconds // 60} minutes")

def display_analytics():
    # Convert topic history to DataFrame
    df = pd.DataFrame(st.session_state.topic_history)
    
    # Create visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Topics over time
        fig1 = px.line(df, x='timestamp', y='topic', title='Learning Progress')
        st.plotly_chart(fig1)
    
    with col2:
        # Difficulty distribution
        fig2 = px.pie(df, names='difficulty', title='Difficulty Distribution')
        st.plotly_chart(fig2)

def save_feedback(rating, topic, style):
    conn = sqlite3.connect('learning_history.db')
    c = conn.cursor()
    c.execute('''INSERT INTO user_interactions (timestamp, user_id, topic, 
                 learning_style, rating) VALUES (?, ?, ?, ?, ?)''',
             (datetime.now().isoformat(), st.session_state.user_id, 
              topic, style, rating))
    conn.commit()
    conn.close()
    st.session_state.session.ratings.append(rating)
    st.success("Thank you for your feedback!")

def save_detailed_feedback(feedback, topic, style):
    conn = sqlite3.connect('learning_history.db')
    c = conn.cursor()
    c.execute('''UPDATE user_interactions 
                 SET feedback = ? 
                 WHERE user_id = ? AND topic = ? AND learning_style = ?
                 ORDER BY timestamp DESC LIMIT 1''',
             (feedback, st.session_state.user_id, topic, style))
    conn.commit()
    conn.close()
    st.success("Thank you for your detailed feedback!")

def log_user_interaction(prompt):
    logging.info(f"User {st.session_state.user_id}: {prompt}")

if __name__ == "__main__":
    main()

# Custom CSS to hide Streamlit elements and improve UI
st.markdown("""
<style>
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
    }
    .stTextArea textarea {
        border-radius: 5px;
        border-color: #4CAF50;
    }
    .reportview-container {
        background: #fafafa;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    [data-testid="stSidebar"][aria-expanded="true"] {
        min-width: 550px;
        max-width: 550px;
    }
    
</style>
""", unsafe_allow_html=True)
