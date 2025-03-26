import streamlit as st
import boto3
import re  # For password validation
from botocore.exceptions import ClientError
import hashlib
from datetime import datetime
import io
import logging
import docx
from PyPDF2 import PdfReader
from typing import Dict

import streamlit as st
import boto3

# Load AWS configuration from Streamlit secrets
AWS_REGION = st.secrets["AWS_REGION"]
USER_POOL_ID = st.secrets["USER_POOL_ID"]
CLIENT_ID = st.secrets["CLIENT_ID"]
S3_BUCKET = st.secrets["S3_BUCKET"]

# Load AWS credentials
AWS_ACCESS_KEY = st.secrets["AWS_ACCESS_KEY"]
AWS_SECRET_KEY = st.secrets["AWS_SECRET_KEY"]

# Initialize Boto3 client for S3
s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
)

# # List S3 buckets (for testing)
# buckets = s3_client.list_buckets()
# st.write("S3 Buckets:", [bucket["Name"] for bucket in buckets["Buckets"]])

# Page Configuration
st.set_page_config(page_title="ᴀᴅᴀᴘᴛɪᴠᴇ ʟᴇᴀʀɴɪɴɢ ɢᴇɴᴇʀᴀᴛᴏʀ ", page_icon="🌎",layout="wide")
# Initialize the Cognito client
client = boto3.client(
    'cognito-idp',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_valid_password(password):
    return {
        "min_length": len(password) >= 8,
        "uppercase": bool(re.search(r"[A-Z]", password)),
        "lowercase": bool(re.search(r"[a-z]", password)),
        "digit": bool(re.search(r"\d", password)),
        "special_char": bool(re.search(r"[!@#$%^&*]", password))
    }

# Function to sign up a new user with role
def sign_up(email, password, role):
    try:
        response = client.sign_up(
            ClientId=CLIENT_ID,
            Username=email,
            Password=password,
            UserAttributes=[
                {"Name": "email", "Value": email},
                {"Name": "custom:role", "Value": role},  # 'instructor' or 'student'
            ],
        )
        st.success("Sign up successful! Please check your email for the verification code.")
        st.session_state['email'] = email  # Save email for verification
        st.session_state['signup_completed'] = True
        return response
    except ClientError as e:
        st.error(f"Error signing up: {e.response['Error']['Message']}")
        return None

# Function to verify user's email
def verify_email(email, verification_code):
    try:
        response = client.confirm_sign_up(
            ClientId=CLIENT_ID,
            Username=email,
            ConfirmationCode=verification_code,
        )
        st.success("Email verified successfully!")
        st.session_state['signup_completed'] = False
        return response
    except ClientError as e:
        st.error(f"Error verifying email: {e.response['Error']['Message']}")
        return None

# Initialize session state for authentication
if 'signed_in' not in st.session_state:
    st.session_state.signed_in = False


    

def sign_in(email, password):
    try:
        # Authenticate user
        response = client.initiate_auth(
            ClientId=CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={'USERNAME': email, 'PASSWORD': password},
        )
        
        # Store authentication tokens in session state
        st.session_state['tokens'] = response['AuthenticationResult']
        st.session_state['signed_in'] = True
        st.session_state['username'] = email
        
        # Retrieve user role
        user_info = client.get_user(AccessToken=st.session_state['tokens']['AccessToken'])
        for attribute in user_info['UserAttributes']:
            if attribute['Name'] == 'custom:role':
                st.session_state['role'] = attribute['Value']
        
        st.success("Sign in successful! Redirecting...")

        # 🔹 Ensure page switch happens at the end
        st.switch_page("pages/🇭​​🇴​​🇲​​🇪​ 🌎.py")  

    except ClientError as e:
        st.error(f"Error signing in: {e.response['Error']['Message']}")

# Streamlit UI setup
class StreamlitUI:
    """Handle Streamlit UI components"""
    

    def setup_page(self):
        st.set_page_config(page_title="Document Upload", layout="wide")
        
        # Custom CSS
        st.markdown("""
            <style>
                .stButton>button {
                    width: 100%;
                    border-radius: 5px;
                    height: 3em;
                    background-color: #FF4B4B;
                    color: white;
                }
                .success-message {
                    padding: 1em;
                    border-radius: 5px;
                    background-color: #28a745;
                    color: white;
                }
                .error-message {
                    padding: 1em;
                    border-radius: 5px;
                    background-color: #dc3545;
                    color: white;
                }
            </style>
        """, unsafe_allow_html=True)


    def main(self):

        choice = st.sidebar.selectbox("Choose Option", ["Sign Up", "Sign In"])
        if choice == "Sign Up":
            sign_up_page()
        elif choice == "Sign In":
                sign_in_page()
   
# Main function to manage Streamlit app flow
def sign_up_page():
    st.subheader("🇸​​🇮​​🇬​​🇳​ ​🇺​​🇵​")
    if not st.session_state.get('signup_completed'):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Select Role", ["student", "instructor"])

        if password:
            checks = is_valid_password(password)
            st.write("Password Requirements:")
            st.write("- Minimum 8 characters: " + ("✅" if checks["min_length"] else "❌"))
            st.write("- At least 1 uppercase letter: " + ("✅" if checks["uppercase"] else "❌"))
            st.write("- At least 1 lowercase letter: " + ("✅" if checks["lowercase"] else "❌"))
            st.write("- At least 1 digit: " + ("✅" if checks["digit"] else "❌"))
            st.write("- At least 1 special character (!@#$%^&*): " + ("✅" if checks["special_char"] else "❌"))

        if st.button("Sign Up"):
            if email and password:
                if all(is_valid_password(password).values()):
                    sign_up(email, password, role)
                else:
                    st.warning("Please make sure your password meets all requirements.")
            else:
                st.warning("Please provide both email and password.")
    
    if st.session_state.get('signup_completed'):
        st.subheader("Verify Email")
        verification_code = st.text_input("Enter Verification Code")
        if st.button("Verify Email"):
            if verification_code:
                verify_email(st.session_state['email'], verification_code)
            else:
                st.warning("Please enter the verification code sent to your email.")

def sign_in_page():
    st.subheader("​🇸​​🇮​​🇬​​🇳​ ​🇮​​🇳​")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Sign In"):
        if email and password:
            sign_in(email, password)
        else:
            st.warning("Please provide both email and password.")


disable_sidebar_nav_css = """
<style>
    /* Target the sidebar navigation links */
    section[data-testid="stSidebarNav"] a {
        pointer-events: none; /* Disable clicking */
        cursor: default; /* Change cursor to default (non-clickable) */
        opacity: 0.5; /* Optional: Make the links look faded */
    }
</style>
"""
st.markdown(disable_sidebar_nav_css, unsafe_allow_html=True)


# Run the app
if __name__ == "__main__":
    ui = StreamlitUI()
    ui.main()

