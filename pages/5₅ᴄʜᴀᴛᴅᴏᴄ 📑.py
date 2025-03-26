import os
import streamlit as st
import google.generativeai as genai
import numpy as np
import faiss
from typing import List
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer


# Check if the user is logged in
if 'signed_in' not in st.session_state or not st.session_state.signed_in:
    st.warning("🔒You must be logged in to access this page.")
    st.stop()  # Stop rendering the rest of the page



def set_page_config():
    st.set_page_config(
        page_title="ᴄʜᴀᴛ ᴡɪᴛʜ ᴅᴏᴄ​",
        page_icon="📑",
        layout="wide",
        initial_sidebar_state="expanded"
    )

class GeminiPDFInsights:
    def __init__(self, api_key: str):
        """Initialize Gemini PDF Chatbot with professional configurations."""
        self.api_key = api_key
        self._setup_page_config()
        self._initialize_session_state()
        self._validate_api_key()

    def _validate_api_key(self):
        """Configure Gemini API with the provided key."""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            st.error(f"API Configuration Error: {e}")
            st.stop()

    def _setup_page_config(self):
        """Configure Streamlit page with minimal, professional styling."""
        st.set_page_config(
            page_title="PDF Intelligence",
            page_icon="📄",
            layout="wide"
        )
        st.markdown("""
            <style>
                .stApp { background-color: #f4f4f4; }
                .stTextInput > div > div > input { 
                    background-color: #e6e6e6;
                    color: black;
                }
            </style>
        """, unsafe_allow_html=True)

    def _initialize_session_state(self):
        """Initialize Streamlit session variables."""
        session_vars = [
            'pdf_processed', 'document_chunks', 
            'document_embeddings', 'faiss_index'
        ]
        for var in session_vars:
            if var not in st.session_state:
                st.session_state[var] = None

    def extract_pdf_text(self, pdf_file) -> str:
        """Extract text from PDF."""
        try:
            reader = PdfReader(pdf_file)
            return " ".join(page.extract_text() for page in reader.pages)
        except Exception as e:
            st.error(f"PDF Text Extraction Error: {e}")
            return ""

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """Advanced text chunking."""
        words = text.split()
        chunks, current_chunk = [], []
        
        for word in words:
            current_chunk.append(word)
            if len(current_chunk) >= chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = current_chunk[-overlap:]
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks

    def create_vector_index(self, chunks: List[str]) -> np.ndarray:
        """Create FAISS vector index for semantic search."""
        try:
            embeddings = np.array([self.embedding_model.encode(chunk) for chunk in chunks])
            index = faiss.IndexFlatL2(embeddings.shape[1])
            index.add(embeddings)
            return index
        except Exception as e:
            st.error(f"Vector Index Creation Error: {e}")
            return None

    def semantic_search(self, query: str, top_k: int = 3) -> List[str]:
        """Perform semantic search across document chunks."""
        if st.session_state.faiss_index is None:
            return []

        try:
            query_embedding = self.embedding_model.encode(query).reshape(1, -1)
            D, I = st.session_state.faiss_index.search(query_embedding, top_k)
            return [st.session_state.document_chunks[i] for i in I[0]]
        except Exception as e:
            st.error(f"Semantic Search Error: {e}")
            return []

    def generate_response(self, query: str, context: List[str]) -> str:
        """Generate intelligent response using Gemini."""
        try:
            context_str = "\n".join(context)
            full_prompt = f"""Context from PDF:
            {context_str}

            Query: {query}

            Provide a concise, accurate response based on the context."""

            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            st.error(f"Response Generation Error: {e}")
            return "Unable to generate response."

    def run(self):
        """Main application runner."""
        st.title("PDF Intelligence")

        # PDF Upload
        uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])
        
        if uploaded_file is not None:
            with st.spinner('Processing PDF...'):
                text = self.extract_pdf_text(uploaded_file)
                
                if not text:
                    st.error("Could not extract text from PDF")
                    return

                chunks = self.chunk_text(text)
                
                st.session_state.document_chunks = chunks
                st.session_state.faiss_index = self.create_vector_index(chunks)
                
                if st.session_state.faiss_index is not None:
                    st.session_state.pdf_processed = True
                    st.success("PDF processed successfully!")

        # Chat Interface
        if st.session_state.pdf_processed:
            query = st.text_input("Ask a question about your document")
            
            if query:
                with st.spinner('Generating response...'):
                    context = self.semantic_search(query)
                    response = self.generate_response(query, context)
                    
                    st.subheader("Response")
                    st.write(response)

def main():
    # Load API key from Streamlit secrets
    api_key = st.secrets["GEMINI_API_KEY"]

    # Initialize the chatbot using the secure API key
    chatbot = GeminiPDFInsights(api_key=api_key)
    chatbot.run()

if __name__ == '__main__':
    main()