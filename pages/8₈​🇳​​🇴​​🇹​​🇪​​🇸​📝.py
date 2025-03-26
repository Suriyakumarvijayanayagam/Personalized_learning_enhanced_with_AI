import streamlit as st
import base64
from datetime import datetime
import json
import uuid
import pandas as pd
import re
import random
from streamlit_ace import st_ace
import time


# Check if the user is logged in
if 'signed_in' not in st.session_state or not st.session_state.signed_in:
    st.warning("🔒You must be logged in to access this page.")
    st.stop()  # Stop rendering the rest of the page

# Set page configuration
st.set_page_config(
    page_title="NoteStream Pro",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced UI
def apply_custom_css():
    st.markdown("""
    <style>
    .main-header {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 5px;
    }
    .sub-header {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 500;
        color: #424242;
        margin-bottom: 20px;
    }
    .card {
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 15px;
        background-color: var(--card-bg-color);
        border: 1px solid var(--card-border-color);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
    }
    .card-title {
        font-weight: 600;
        margin-bottom: 8px;
        color: var(--text-color);
    }
    .card-meta {
        font-size: 0.8em;
        color: var(--secondary-text-color);
        margin-bottom: 10px;
    }
    .tag {
        display: inline-block;
        padding: 2px 8px;
        margin-right: 5px;
        border-radius: 4px;
        font-size: 0.7em;
        font-weight: 500;
    }
    .search-box {
        border-radius: 30px;
        border: 1px solid #E0E0E0;
        padding: 10px 15px;
        width: 100%;
        margin-bottom: 20px;
    }
    .status-message {
        padding: 10px;
        border-radius: 4px;
        margin: 10px 0;
    }
    .success-message {
        background-color: rgba(76, 175, 80, 0.1);
        border-left: 4px solid #4CAF50;
        color: #2E7D32;
    }
    .error-message {
        background-color: rgba(244, 67, 54, 0.1);
        border-left: 4px solid #F44336;
        color: #C62828;
    }
    .info-message {
        background-color: rgba(33, 150, 243, 0.1);
        border-left: 4px solid #2196F3;
        color: #1565C0;
    }
    .stButton button {
        border-radius: 20px;
        font-weight: 500;
        padding: 8px 16px;
        transition: all 0.3s ease;
    }
    .primary-button button {
        background-color: #1E88E5;
        color: white;
        border: none;
    }
    .primary-button button:hover {
        background-color: #1565C0;
        box-shadow: 0 5px 15px rgba(30, 136, 229, 0.3);
    }
    .secondary-button button {
        background-color: transparent;
        border: 1px solid #1E88E5;
        color: #1E88E5;
    }
    .secondary-button button:hover {
        background-color: rgba(30, 136, 229, 0.1);
    }
    .danger-button button {
        background-color: #F44336;
        color: white;
        border: none;
    }
    .danger-button button:hover {
        background-color: #D32F2F;
        box-shadow: 0 5px 15px rgba(244, 67, 54, 0.3);
    }
    .st-emotion-cache-18ni7ap {
        background-color: var(--background-color);
    }
    .st-emotion-cache-6qob1r {
        background-color: var(--sidebar-bg-color);
    }
    .st-emotion-cache-1cypcdb {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    .st-emotion-cache-1v0mbdj {
        width: 100%;
    }
    .stTextArea textarea {
        border-radius: 8px;
        border: 1px solid #E0E0E0;
        padding: 10px;
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 16px;
        height: 300px;
        background-color: var(--textarea-bg-color);
        color: var(--text-color);
    }
    .color-picker {
        display: inline-block;
        width: 25px;
        height: 25px;
        border-radius: 50%;
        margin-right: 5px;
        cursor: pointer;
        border: 2px solid transparent;
    }
    .color-picker.selected {
        border: 2px solid #1E88E5;
    }
    .notebook-tab {
        padding: 10px 15px;
        background-color: var(--tab-bg-color);
        border-radius: 8px 8px 0 0;
        margin-right: 2px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    .notebook-tab:hover {
        background-color: var(--tab-hover-bg-color);
    }
    .notebook-tab.active {
        background-color: var(--tab-active-bg-color);
        border-bottom: 3px solid #1E88E5;
    }
    .footer {
        margin-top: 30px;
        padding-top: 10px;
        border-top: 1px solid #E0E0E0;
        text-align: center;
        font-size: 0.8em;
        color: var(--secondary-text-color);
    }
    .export-options {
        margin-top: 10px;
        padding: 10px;
        border-radius: 8px;
        background-color: var(--card-bg-color);
        border: 1px solid var(--card-border-color);
    }
    .note-preview {
        overflow-y: auto;
        max-height: 300px;
        padding: 10px;
        border-radius: 8px;
        background-color: var(--preview-bg-color);
        border: 1px solid var(--card-border-color);
        margin-bottom: 10px;
    }
    .chart-container {
        margin-top: 20px;
        padding: 15px;
        border-radius: 8px;
        background-color: var(--card-bg-color);
        border: 1px solid var(--card-border-color);
    }
    </style>
    """, unsafe_allow_html=True)

# Theme variables
def set_theme_variables():
    # Dark mode
    if st.session_state.get('dark_mode', False):
        st.markdown("""
        <style>
        :root {
            --background-color: #121212;
            --sidebar-bg-color: #1E1E1E;
            --card-bg-color: #1E1E1E;
            --card-border-color: #333333;
            --text-color: #E0E0E0;
            --secondary-text-color: #AAAAAA;
            --textarea-bg-color: #2D2D2D;
            --tab-bg-color: #2D2D2D;
            --tab-hover-bg-color: #3D3D3D;
            --tab-active-bg-color: #1E1E1E;
            --preview-bg-color: #2D2D2D;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        :root {
            --background-color: #FFFFFF;
            --sidebar-bg-color: #F5F5F5;
            --card-bg-color: #FFFFFF;
            --card-border-color: #E0E0E0;
            --text-color: #333333;
            --secondary-text-color: #757575;
            --textarea-bg-color: #FFFFFF;
            --tab-bg-color: #F5F5F5;
            --tab-hover-bg-color: #EEEEEE;
            --tab-active-bg-color: #FFFFFF;
            --preview-bg-color: #F9F9F9;
        }
        </style>
        """, unsafe_allow_html=True)

# Note class
class Note:
    def __init__(self, title="", content="", notebook="Default", tags=None, color="#1E88E5"):
        self.id = str(uuid.uuid4())
        self.title = title
        self.content = content
        self.notebook = notebook
        self.tags = tags or []
        self.color = color
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.pinned = False
        
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "notebook": self.notebook,
            "tags": self.tags,
            "color": self.color,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "pinned": self.pinned
        }
    
    @classmethod
    def from_dict(cls, data):
        note = cls()
        note.id = data.get("id", str(uuid.uuid4()))
        note.title = data.get("title", "")
        note.content = data.get("content", "")
        note.notebook = data.get("notebook", "Default")
        note.tags = data.get("tags", [])
        note.color = data.get("color", "#1E88E5")
        note.created_at = data.get("created_at", datetime.now().isoformat())
        note.updated_at = data.get("updated_at", note.created_at)
        note.pinned = data.get("pinned", False)
        return note

# Initialize session state
def initialize_session_state():
    if 'notes' not in st.session_state:
        st.session_state.notes = []
    if 'notebooks' not in st.session_state:
        st.session_state.notebooks = ["Default", "Work", "Personal"]
    if 'current_notebook' not in st.session_state:
        st.session_state.current_notebook = "Default"
    if 'current_note_id' not in st.session_state:
        st.session_state.current_note_id = None
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    if 'editor_mode' not in st.session_state:
        st.session_state.editor_mode = "rich"  # "rich" or "code"
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
    if 'analytics_data' not in st.session_state:
        st.session_state.analytics_data = {
            "word_count": 0,
            "notes_per_notebook": {},
            "tags_frequency": {},
            "activity_over_time": []
        }

# Update analytics data
def update_analytics():
    notebooks = {}
    tags = {}
    word_count = 0
    activity = {}
    
    for note in st.session_state.notes:
        # Update notebooks count
        if note.notebook in notebooks:
            notebooks[note.notebook] += 1
        else:
            notebooks[note.notebook] = 1
        
        # Update tags frequency
        for tag in note.tags:
            if tag in tags:
                tags[tag] += 1
            else:
                tags[tag] = 1
        
        # Update word count
        word_count += len(re.findall(r'\w+', note.content))
        
        # Update activity over time
        date = datetime.fromisoformat(note.created_at).strftime("%Y-%m-%d")
        if date in activity:
            activity[date] += 1
        else:
            activity[date] = 1
    
    st.session_state.analytics_data = {
        "word_count": word_count,
        "notes_per_notebook": notebooks,
        "tags_frequency": tags,
        "activity_over_time": [{"date": k, "count": v} for k, v in activity.items()]
    }

# Save and load notes
def save_notes():
    notes_data = [note.to_dict() for note in st.session_state.notes]
    return json.dumps(notes_data)

def get_note_by_id(note_id):
    for note in st.session_state.notes:
        if note.id == note_id:
            return note
    return None

def update_note(note_id, updates):
    for i, note in enumerate(st.session_state.notes):
        if note.id == note_id:
            for key, value in updates.items():
                setattr(note, key, value)
            note.updated_at = datetime.now().isoformat()
            st.session_state.notes[i] = note
            update_analytics()
            return True
    return False

def delete_note(note_id):
    for i, note in enumerate(st.session_state.notes):
        if note.id == note_id:
            st.session_state.notes.pop(i)
            update_analytics()
            return True
    return False

def create_new_note(title, content, notebook, tags, color):
    new_note = Note(title, content, notebook, tags, color)
    st.session_state.notes.append(new_note)
    st.session_state.current_note_id = new_note.id
    update_analytics()
    return new_note.id

# UI Components
def render_header():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<h1 class="main-header">NoteStream Pro</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Your professional note-taking workspace</p>', unsafe_allow_html=True)
    with col2:
        st.session_state.dark_mode = st.toggle("Dark Mode", st.session_state.dark_mode)
        set_theme_variables()

def render_sidebar():
    with st.sidebar:
        st.markdown("### Notebooks")
        
        # Add new notebook
        new_notebook = st.text_input("Create New Notebook", key="new_notebook")
        if st.button("Add Notebook", key="add_notebook"):
            if new_notebook and new_notebook not in st.session_state.notebooks:
                st.session_state.notebooks.append(new_notebook)
                st.session_state.current_notebook = new_notebook
                st.success(f"Notebook '{new_notebook}' created!")
                st.rerun()
        
        # List notebooks
        for notebook in st.session_state.notebooks:
            if st.button(f"📓 {notebook}", key=f"notebook_{notebook}"):
                st.session_state.current_notebook = notebook
                st.session_state.current_note_id = None
                st.rerun()
        
        st.divider()
        
        # Search
        st.markdown("### Search")
        search_query = st.text_input("Search notes", key="search_input", value=st.session_state.search_query)
        if search_query != st.session_state.search_query:
            st.session_state.search_query = search_query
            st.rerun()
        
        st.divider()
        
        # All Tags
        st.markdown("### Tags")
        all_tags = set()
        for note in st.session_state.notes:
            all_tags.update(note.tags)
        
        for tag in sorted(all_tags):
            if st.button(f"🏷️ {tag}", key=f"tag_{tag}"):
                st.session_state.search_query = f"tag:{tag}"
                st.rerun()
        
        st.divider()
        
        # Export options
        st.markdown("### Export")
        export_format = st.selectbox("Format", ["Text (.txt)", "Markdown (.md)", "JSON (.json)"], key="export_format")
        export_scope = st.radio("Scope", ["All Notes", "Current Notebook", "Selected Note"], key="export_scope")
        
        if st.button("Export Notes", key="export_notes"):
            if export_scope == "All Notes":
                notes_to_export = st.session_state.notes
            elif export_scope == "Current Notebook":
                notes_to_export = [note for note in st.session_state.notes if note.notebook == st.session_state.current_notebook]
            else:  # Selected Note
                if st.session_state.current_note_id:
                    notes_to_export = [get_note_by_id(st.session_state.current_note_id)]
                else:
                    st.error("No note selected!")
                    notes_to_export = []
            
            if notes_to_export:
                export_notes(notes_to_export, export_format)
            else:
                st.error("No notes to export!")

def render_note_list():
    st.markdown("### Your Notes")
    
    # Filter notes
    filtered_notes = st.session_state.notes
    
    if st.session_state.search_query:
        search_term = st.session_state.search_query.lower()
        if search_term.startswith("tag:"):
            tag = search_term[4:].strip()
            filtered_notes = [note for note in filtered_notes if tag in [t.lower() for t in note.tags]]
        else:
            filtered_notes = [note for note in filtered_notes if 
                            search_term in note.title.lower() or 
                            search_term in note.content.lower()]
    else:
        filtered_notes = [note for note in filtered_notes if note.notebook == st.session_state.current_notebook]
    
    # Sort notes (pinned first, then by updated date)
    filtered_notes.sort(key=lambda x: (not x.pinned, x.updated_at), reverse=True)
    
    if not filtered_notes:
        st.markdown('<div class="info-message">No notes found. Create a new note to get started!</div>', unsafe_allow_html=True)
    
    # Display notes
    for note in filtered_notes:
        created_date = datetime.fromisoformat(note.created_at).strftime("%b %d, %Y")
        updated_date = datetime.fromisoformat(note.updated_at).strftime("%b %d, %Y at %H:%M")
        
        st.markdown(f"""
        <div class="card" style="border-left: 5px solid {note.color};">
            <div class="card-title">{'📌 ' if note.pinned else ''}{note.title or 'Untitled'}</div>
            <div class="card-meta">Created: {created_date} | Updated: {updated_date}</div>
            <div>
                {''.join([f'<span class="tag" style="background-color: {get_tag_color(tag)}; color: white;">{tag}</span>' for tag in note.tags])}
            </div>
            <div style="margin-top: 10px;">
                {note.content[:100] + '...' if len(note.content) > 100 else note.content}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("Open", key=f"open_{note.id}"):
                st.session_state.current_note_id = note.id
                st.rerun()
        with col2:
            if st.button("Pin" if not note.pinned else "Unpin", key=f"pin_{note.id}"):
                update_note(note.id, {"pinned": not note.pinned})
                st.rerun()
        with col3:
            if st.button("Delete", key=f"delete_{note.id}"):
                delete_note(note.id)
                if st.session_state.current_note_id == note.id:
                    st.session_state.current_note_id = None
                st.rerun()

def render_note_editor():
    # Handle new note creation
    if st.button("➕ New Note", key="new_note_button"):
        st.session_state.current_note_id = None
        st.rerun()
    
    # Get current note if exists
    current_note = None
    if st.session_state.current_note_id:
        current_note = get_note_by_id(st.session_state.current_note_id)
    
    # Note editor
    st.markdown("### 📝 Note Editor")
    
    # Title
    note_title = st.text_input("Title", value=current_note.title if current_note else "", key="note_title")
    
    # Note content
    editor_tabs = ["Rich Text", "Code Editor"]
    selected_tab = st.radio("Editor Type", editor_tabs, horizontal=True, key="editor_type")
    
    if selected_tab == "Rich Text":
        note_content = st.text_area("Content", value=current_note.content if current_note else "", height=400, key="note_content")
    else:
        editor_language = st.selectbox("Language", ["markdown", "python", "javascript", "html", "css", "json", "sql"], key="editor_language")
        note_content = st_ace(
            value=current_note.content if current_note else "",
            language=editor_language,
            theme="monokai" if st.session_state.dark_mode else "github",
            key="ace_editor",
            height=400
        )
    
    # Notebook selection
    note_notebook = st.selectbox("Notebook", st.session_state.notebooks, index=st.session_state.notebooks.index(current_note.notebook if current_note else st.session_state.current_notebook), key="note_notebook")
    
    # Tags
    note_tags = st.text_input("Tags (comma separated)", value=", ".join(current_note.tags) if current_note and current_note.tags else "", key="note_tags")
    tags_list = [tag.strip() for tag in note_tags.split(",") if tag.strip()]
    
    # Color picker
    st.markdown("Note Color")
    colors = ["#1E88E5", "#43A047", "#E53935", "#FB8C00", "#8E24AA", "#3949AB", "#00ACC1", "#FFB300", "#5E35B1", "#546E7A"]
    selected_color = current_note.color if current_note else colors[0]
    
    color_cols = st.columns(len(colors))
    for i, color in enumerate(colors):
        with color_cols[i]:
            if st.button("", key=f"color_{i}", 
                       help=color,
                       on_click=lambda c=color: set_selected_color(c),
                       args=(color,)):
                selected_color = color
    
    # Save and cancel buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Note", key="save_note"):
            if note_title.strip() or note_content.strip():
                if current_note:
                    update_note(current_note.id, {
                        "title": note_title,
                        "content": note_content,
                        "notebook": note_notebook,
                        "tags": tags_list,
                        "color": selected_color
                    })
                    st.success("Note updated successfully!")
                else:
                    new_note_id = create_new_note(note_title, note_content, note_notebook, tags_list, selected_color)
                    st.session_state.current_note_id = new_note_id
                    st.success("Note created successfully!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Title or content cannot be empty!")
    
    with col2:
        if st.button("Cancel", key="cancel_note"):
            st.session_state.current_note_id = None
            st.rerun()

    # Preview
    if note_content:
        st.markdown("### Preview")
        st.markdown('<div class="note-preview">' + note_content + '</div>', unsafe_allow_html=True)

def render_dashboard():
    st.markdown("### 📊 Dashboard")
    
    # Update analytics
    update_analytics()
    
    # KPI Cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Notes", len(st.session_state.notes))
    with col2:
        st.metric("Total Words", st.session_state.analytics_data["word_count"])
    with col3:
        st.metric("Notebooks", len(st.session_state.notebooks))
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Notes per Notebook")
        if st.session_state.analytics_data["notes_per_notebook"]:
            notebooks_df = pd.DataFrame({
                "Notebook": list(st.session_state.analytics_data["notes_per_notebook"].keys()),
                "Count": list(st.session_state.analytics_data["notes_per_notebook"].values())
            })
            st.bar_chart(notebooks_df.set_index("Notebook"))
        else:
            st.info("No data available")
    
    with col2:
        st.markdown("#### Popular Tags")
        if st.session_state.analytics_data["tags_frequency"]:
            tags_df = pd.DataFrame({
                "Tag": list(st.session_state.analytics_data["tags_frequency"].keys()),
                "Count": list(st.session_state.analytics_data["tags_frequency"].values())
            }).sort_values("Count", ascending=False).head(10)
            st.bar_chart(tags_df.set_index("Tag"))
        else:
            st.info("No tags available")

# Helper functions
def export_notes(notes, format_type):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format_type == "Text (.txt)":
        content = ""
        for note in notes:
            content += f"Title: {note.title}\n"
            content += f"Date: {datetime.fromisoformat(note.created_at).strftime('%Y-%m-%d %H:%M:%S')}\n"
            content += f"Notebook: {note.notebook}\n"
            content += f"Tags: {', '.join(note.tags)}\n"
            content += f"\n{note.content}\n"
            content += f"\n{'=' * 50}\n\n"
        
        file_name = f"notes_export_{timestamp}.txt"
        mime_type = "text/plain"
    
    elif format_type == "Markdown (.md)":
        content = ""
        for note in notes:
            content += f"# {note.title}\n\n"
            content += f"*Date: {datetime.fromisoformat(note.created_at).strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
            content += f"**Notebook:** {note.notebook}\n\n"
            content += f"**Tags:** {', '.join(note.tags)}\n\n"
            content += f"{note.content}\n\n"
            content += f"---\n\n"
        
        file_name = f"notes_export_{timestamp}.md"
        mime_type = "text/markdown"
    
    else:  # JSON
        content = json.dumps([note.to_dict() for note in notes], indent=2)
        file_name = f"notes_export_{timestamp}.json"
        mime_type = "application/json"
    
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:{mime_type};base64,{b64}" download="{file_name}">📥 Download {file_name}</a>'
    st.markdown(href, unsafe_allow_html=True)

def get_tag_color(tag):
    # Generate a consistent color for each tag
    colors = ["#1E88E5", "#43A047", "#E53935", "#FB8C00", "#8E24AA", "#3949AB", "#00ACC1", "#FFB300", "#5E35B1", "#546E7A"]
    hash_value = hash(tag) % len(colors)
    return colors[hash_value]

def set_selected_color(color):
    st.session_state.selected_color = color

# Sample data generator
def generate_sample_data():
    if not st.session_state.notes:
        sample_notes = [
            Note(
                title="Welcome to NoteStream Pro!",
                content="This is your professional note-taking application. Here are some features:\n\n- Rich text editing\n- Code syntax highlighting\n- Notebook organization\n- Tag filtering\n- Dark mode\n- Analytics dashboard\n\nGet started by creating your first note!",
                notebook="Default",
                tags=["welcome", "tutorial"],
                color="#1E88E5"
            ),
            Note(
                title="Meeting Notes - Project Kickoff",
                content="# Project Kickoff Meeting\n\n**Date:** 2023-03-15\n**Attendees:** John, Sarah, Mike\n\n## Agenda\n1. Project overview\n2. Timeline discussion\n3. Resource allocation\n\n## Action Items\n- [ ] Create project plan\n- [ ] Schedule follow-up meeting\n- [ ] Share documentation",
                notebook="Work",
                tags=["meeting", "project"],
                color="#43A047"
            ),
            Note(
                title="Python Code Snippet",
                content="```python\ndef fibonacci(n):\n    \"\"\"Generate fibonacci sequence up to n\"\"\"\n    a, b = 0, 1\n    result = []\n    while a < n:\n        result.append(a)\n        a, b = b, a + b\n    return result\n\n# Example usage\nprint(fibonacci(100))\n```",
                notebook="Personal",
                tags=["code", "python"],
                color="#FB8C00"
            )
        ]
        
        for note in sample_notes:
            st.session_state.notes.append(note)
        
        update_analytics()

def main():
    # Initialize
    initialize_session_state()
    apply_custom_css()
    set_theme_variables()
    generate_sample_data()
    
    # Render header
    render_header()
    
    # Main layout
    if st.session_state.current_note_id is None and not st.session_state.search_query:
        # Dashboard and note list view
        tab1, tab2 = st.tabs(["Notes", "Dashboard"])
        
        with tab1:
            # Sidebar for navigation
            render_sidebar()
            
            # Main content area
            col1, col2 = st.columns([2, 3])
            
            with col1:
                render_note_list()
            
            with col2:
                render_note_editor()
        
        with tab2:
            render_dashboard()
    
    else:
        # Note edit view or search results
        render_sidebar()
        
        if st.session_state.search_query:
            st.markdown(f"### Search Results for: '{st.session_state.search_query}'")
            if st.button("Clear Search", key="clear_search"):
                st.session_state.search_query = ""
                st.rerun()
            
            render_note_list()
        else:
            render_note_editor()
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>NoteStream Pro v1.0.0 | Made with ❤️ using Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

