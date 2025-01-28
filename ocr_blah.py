import pytesseract
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
import time
import streamlit as st
from googletrans import Translator
from summarizer import Summarizer
from nltk.tokenize import sent_tokenize

# Set up Tesseract OCR and Translator
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
translator = Translator()

# Streamlit App Configuration
st.set_page_config(page_title="OCR & Text Processing App", layout="wide")
st.title("OCR & Text Processing Application")
st.sidebar.header("Workflow Settings")

# Initialize session state for text, screenshot filename, login status, and user credentials
if "text" not in st.session_state:
    st.session_state.text = None
if "screenshot_filename" not in st.session_state:
    st.session_state.screenshot_filename = None
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

# Sign In / Sign Up Page
def sign_in_signup():
    st.header("Sign In / Sign Up")
    
    if st.session_state.logged_in:
        st.success(f"Welcome {st.session_state.username}!")
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.experimental_rerun()
    else:
        choice = st.radio("Choose action", ("Sign In", "Sign Up"))
        
        if choice == "Sign In":
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.button("Sign In"):
                if username == "admin" and password == "admin":  # For demonstration, you can change this part
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.experimental_rerun()
                else:
                    st.error("Invalid credentials")
        
        elif choice == "Sign Up":
            new_username = st.text_input("Create Username")
            new_password = st.text_input("Create Password", type="password")
            
            if st.button("Sign Up"):
                # In a real app, store credentials securely
                if new_username and new_password:
                    st.success("Sign up successful! Now sign in.")
                else:
                    st.error("Please fill in both fields.")

# Main OCR and Text Processing Page
def main_app():
    st.header("Step 1: Webpage Screenshot Capture")
    url = st.text_input("Enter the webpage URL:", placeholder="https://example.com")
    headless = st.sidebar.checkbox("Run in headless mode", value=True)

    if st.button("Capture Screenshots"):
        # Initialize Selenium WebDriver
        @st.cache_resource
        def initialize_driver(headless):
            options = Options()
            if headless:
                options.add_argument("--headless")  # Always headless
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            service = Service("C:\\Users\\User\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe")
            return webdriver.Chrome(service=service, options=options)

        driver = initialize_driver(headless)
        try:
            # Scroll and capture
            driver.get(url)
            time.sleep(3)
            folder_name = "screenshots"
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)
            
            # Capture a single screenshot
            st.session_state.screenshot_filename = os.path.join(folder_name, "screenshot.png")
            driver.save_screenshot(st.session_state.screenshot_filename)
            st.image(st.session_state.screenshot_filename, caption="Captured Screenshot")
        finally:
            driver.quit()

    # Step 2: OCR Processing
    st.header("Step 2: Extract Text with OCR")
    if st.button("Run OCR on Screenshot"):
        if st.session_state.screenshot_filename and os.path.exists(st.session_state.screenshot_filename):
            st.session_state.text = pytesseract.image_to_string(Image.open(st.session_state.screenshot_filename), lang="kan")
            st.text_area("Extracted Text:", st.session_state.text, height=300)
        else:
            st.error("No screenshot found. Please capture a webpage first.")

    # Step 3: Translation
    st.header("Step 3: Translate Text")
    if st.button("Translate Extracted Text to English"):
        if st.session_state.text:  # Check if text exists
            translated_text = translator.translate(st.session_state.text, src='kn', dest='en').text
            st.text_area("Translated Text:", translated_text, height=300)
        else:
            st.error("No text found. Please run OCR first.")

    # Step 4: Summarization
    st.header("Step 4: Summarize Text")
    if st.button("Summarize Text"):
        @st.cache_resource
        def load_bert_model():
            return Summarizer()

        bert_model = load_bert_model()
        if st.session_state.text:
            summary = bert_model(st.session_state.text, ratio=0.5)
            summary = ' '.join(set(sent_tokenize(summary)))  # Post-process for unique sentences
            st.text_area("Summary:", summary, height=300)
        else:
            st.error("No text found. Please run OCR first.")

# Main logic to decide whether to show sign-in or main app
if not st.session_state.logged_in:
    sign_in_signup()  # Show sign-in page if not logged in
else:
    main_app()  # Show the OCR & Text Processing page if logged in
