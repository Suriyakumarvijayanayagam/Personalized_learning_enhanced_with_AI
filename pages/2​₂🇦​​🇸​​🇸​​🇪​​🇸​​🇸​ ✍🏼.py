import streamlit as st
import google.generativeai as genai
import json
import random
import streamlit as st
import random
import google.generativeai as genai  # Ensure you have Gemini AI configured

import streamlit as st
import google.generativeai as genai
from datetime import datetime
import json
import os
import re
import pandas as pd

# Check if the user is logged in
if 'signed_in' not in st.session_state or not st.session_state.signed_in:
    st.warning("🔒You must be logged in to access this page.")
    st.stop()  # Stop rendering the rest of the page



API_KEY = st.secrets["GEMINI_API_KEY"]
# Configure the API key
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-pro")

def set_page_config():
    st.set_page_config(
        page_title="🇦​​🇮​ ​🇶​​🇺​​🇮​​🇿​ ​🇬​​🇪​​🇳​​🇪​​🇷​​🇦​​🇹​​🇴​​🇷​",
        page_icon="📘",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def initialize_session():
    """Initialize session state variables."""
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = []
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
    if 'quiz_completed' not in st.session_state:
        st.session_state.quiz_completed = False
    if 'quiz_history' not in st.session_state:
        st.session_state.quiz_history = []  # Changed to list instead of QuizHistory object
    if 'current_topic' not in st.session_state:
        st.session_state.current_topic = ""



def generate_mcq(topic, difficulty, num_questions=5):
    """Generates multiple-choice questions using AI."""
    prompt = f"""
    Create {num_questions} multiple-choice questions about {topic} at {difficulty} level.
    
    Use exactly this format for each question:

    Q: Write the question here
    (a) First option
    (b) Second option
    (c) Third option
    (d) Fourth option
    Answer: Write only the letter (a/b/c/d)
    Explanation: Write a brief explanation

    Make sure:
    1. Each question follows this exact format
    2. Options are labeled with (a), (b), (c), (d)
    3. Answer is just the letter a, b, c, or d
    4. Include a brief explanation
    5. Separate each question with a blank line
    """
    
    try:
        response = model.generate_content(prompt)
        if response and response.text:
            questions = parse_mcq_text(response.text)
            if questions:
                return questions
            st.error("Error processing questions. Trying again...")
            return []
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return []

def parse_mcq_text(ai_text):
    """Parses AI-generated MCQs into a structured list."""
    questions = []
    current_question = None
    
    # Split text into lines and clean them
    lines = [line.strip() for line in ai_text.split('\n') if line.strip()]
    
    for line in lines:
        if line.startswith('Q:'):
            if current_question:
                questions.append(current_question)
            current_question = {
                'question': line[2:].strip(),
                'options': [],
                'correct': '',
                'explanation': ''
            }
        elif line.startswith(('(a)', '(b)', '(c)', '(d)')) and current_question:
            current_question['options'].append(line)
        elif line.startswith('Answer:') and current_question:
            current_question['correct'] = line[7:].strip().lower()
        elif line.startswith('Explanation:') and current_question:
            current_question['explanation'] = line[12:].strip()
    
    if current_question:
        questions.append(current_question)
    
    return questions

def display_quiz():
    """Displays quiz with improved UI."""
    if not st.session_state.quiz_questions:
        st.warning("No quiz available. Please generate a quiz first.")
        return

    st.markdown("### 📝 Quiz Time!")
    
    # Quiz progress
    total_questions = len(st.session_state.quiz_questions)
    progress = st.progress(0)
    
    for i, question in enumerate(st.session_state.quiz_questions):

       
        # Update progress bar
        progress.progress((i + 1) / total_questions)
        
        with st.container():
            st.markdown(f"**Question {i + 1} of {total_questions}**")
            st.markdown(f"**{question['question']}**")
            
            # Create columns for better layout
            col1, col2 = st.columns([3, 1])
            
            with col1:
                selected = st.radio(
                    "Choose your answer:",
                    question['options'],
                    key=f"q_{i}",
                    index=None
            )
            
            # Store answer - modified to ensure we're storing the correct format
        if selected:
            # Make sure we're storing the letter properly
            selected_letter = selected[1].lower()  # This gets just the letter
            st.session_state.user_answers[i] = {
                'question': question['question'],
                'selected': selected,
                'correct': question['correct'].lower(),  # Ensure correct answer is lowercase
                'explanation': question['explanation']
            }
        st.markdown("---")

    # Submit button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📋 Submit Quiz", type="primary", use_container_width=True):
            if len(st.session_state.user_answers) < total_questions:
                st.warning("Please answer all questions before submitting!")
            else:
                st.session_state.quiz_completed = True
                display_results()

def display_results():
    """Shows quiz results with enhanced visualization."""
    if not st.session_state.quiz_completed:
        return

    score = 0
    total = len(st.session_state.quiz_questions)
    
    for i, answer in st.session_state.user_answers.items():
        user_choice = answer['selected'][1].lower()  # Get the letter (a, b, c, d)
        if user_choice == answer['correct']:
            score += 1

    # Calculate percentage
    percentage = (score / total) * 100

    # Display score with styling
    st.markdown("""
        <style>
        .big-font {
            font-size:30px !important;
            font-weight:bold;
            text-align:center;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown(f"<p class='big-font'>Your Score: {score}/{total} ({percentage:.1f}%)</p>", unsafe_allow_html=True)

    # Performance message
    if percentage >= 80:
        st.success("🎉 Excellent! You've mastered this topic!")
    elif percentage >= 60:
        st.warning("👍 Good effort! Keep practicing!")
    else:
        st.error("💪 Keep learning! You'll improve!")

    # Detailed review
    st.markdown("### Question Review")
    for i, answer in st.session_state.user_answers.items():
        with st.expander(f"Question {i+1}"):
            st.markdown(f"**Q: {answer['question']}**")
            st.markdown(f"**Your answer:** {answer['selected']}")
            st.markdown(f"**Correct answer:** Option ({answer['correct']})")
            
            if answer['selected'][1].lower() == answer['correct']:
                st.success("✅ Correct!")
            else:
                st.error("❌ Incorrect")
            
            st.info(f"**Explanation:** {answer['explanation']}")

    # Save to history
    st.session_state.quiz_history.append({
        'topic': st.session_state.current_topic,
        'score': score,
        'total': total,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Retake Quiz", use_container_width=True):
            st.session_state.user_answers = {}
            st.session_state.quiz_completed = False
            st.experimental_rerun()
    with col2:
        if st.button("📝 New Quiz", use_container_width=True):
            st.session_state.quiz_questions = []
            st.session_state.user_answers = {}
            st.session_state.quiz_completed = False
            st.experimental_rerun()

def main():
    set_page_config()
    initialize_session()

    # Sidebar with history
    with st.sidebar:
        st.markdown("### 📊 Quiz History")
        if st.session_state.quiz_history:
            # Show last 5 quizzes from the list
            for quiz in list(reversed(st.session_state.quiz_history))[:5]:
                st.markdown(f"""
                    **Topic:** {quiz['topic']}  
                    **Score:** {quiz['score']}/{quiz['total']}  
                    **Date:** {quiz['timestamp']}  
                    ---
                """)
        else:
            st.info("No quiz history yet!")

    # Main content
    st.title("🎓 AI-Powered Quiz Generator")
    st.markdown("Generate custom quizzes on any topic!")

    # Quiz configuration
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        topic = st.text_input("📚 Enter your topic:", 
                            value=st.session_state.current_topic,
                            placeholder="e.g., Python Programming, World History, etc.")
    
    with col2:
        difficulty = st.selectbox("🎯 Select Difficulty:", 
                                ["Basic", "Intermediate", "Advanced"])
    
    with col3:
        num_questions = st.number_input("📝 Questions:", 
                                      min_value=1, 
                                      max_value=10, 
                                      value=5)

    # Generate button
    if st.button("🎲 Generate Quiz", type="primary", use_container_width=True):
        if not topic:
            st.warning("Please enter a topic!")
        else:
            st.session_state.current_topic = topic
            with st.spinner("🤖 Generating your quiz..."):
                st.session_state.quiz_questions = generate_mcq(topic, difficulty, num_questions)
                if st.session_state.quiz_questions:
                    st.success("✨ Quiz generated successfully!")

    # Display quiz if available
    if st.session_state.quiz_questions:
        display_quiz()

if __name__ == "__main__":
    main()