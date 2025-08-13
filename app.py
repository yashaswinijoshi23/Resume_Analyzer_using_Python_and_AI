import os
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai
from pdf2image import convert_from_path
import pytesseract
import pdfplumber
from pathlib import Path

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text

        if text.strip():
            return text.strip()
    except Exception as e:
        print(f"Direct text extraction failed: {e}")

    print("Falling back to OCR for image-based PDF.")
    try:
        images = convert_from_path(pdf_path)
        for image in images:
            page_text = pytesseract.image_to_string(image)
            text += page_text + "\n"
    except Exception as e:
        print(f"OCR failed: {e}")

    return text.strip()

# Function to get response from Gemini AI
def analyze_resume(resume_text, job_description=None):
    if not resume_text:
        return {"error": "Resume text is required for analysis."}
    
    model = genai.GenerativeModel("gemini-2.5-flash")

    basic_prompt = f"""
    You are an expert resume analyser. Given the following resume text and job description, provide a detailed analysis of how well the resume matches the job requirements.
    Resume:
    {resume_text}
    """

    if job_description:
        basic_prompt += f"""
        Additionally, consider the following job description:
        Job Description:
        {job_description}
        Highlight the key skills, experiences, and qualifications that make the candidate a good fit for the job.
        """
    response = model.generate_content(basic_prompt)

    analysis = response.text.strip()
    return analysis


# Streamlit app

st.set_page_config(page_title="Resume Analyzer", layout="wide")

st.markdown("""
    <style>
        .main {
            background-color: #0e1117;
            color: white;
        }
        h1 {
            text-align: center;
            color: #00ffcc;
        }
        .stButton>button {
            background-color: #00ffcc;
            color: black;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: bold;
            border: none;
        }
        .stButton>button:hover {
            background-color: #00ccaa;
            color: white;
        }
        textarea, .stTextArea textarea {
            background-color: #1e222b !important;
            color: white !important;
            border-radius: 8px !important;
        }
        .uploadedFile {
            text-align: center;
            font-size: 14px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📄 AI Resume Analyzer")
st.write("<p style='text-align:center;'>Upload your resume and match it with job descriptions using <b>Google Gemini AI</b>.</p>", unsafe_allow_html=True)

col1 , col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("📤 Upload your resume (PDF)", type=["pdf"])
with col2:
    job_description = st.text_area("📝 Enter Job Description", placeholder="Paste the job description here...")

if uploaded_file is not None:
    st.success(f"✅ {uploaded_file.name} uploaded successfully!")
else:
    st.info("📌 Please upload a resume in PDF format.")

st.markdown("<br>", unsafe_allow_html=True)


st.markdown("<div style= 'padding-top: 10px;'></div>", unsafe_allow_html=True)

if uploaded_file:
    with open("uploaded_resume.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    resume_text = extract_text_from_pdf("uploaded_resume.pdf")

    if st.button("🔍 Analyze Resume"):
        with st.spinner("Analyzing resume with Google Gemini AI..."):
            try:
                analysis = analyze_resume(resume_text, job_description)
                st.success("✅ Analysis complete!")
                st.write(analysis)
            except Exception as e:
                st.error(f"❌ Analysis failed: {e}")

st.markdown("---")
st.markdown("""
    <p style='text-align: center; font-size: 14px;'>
    Powered by <b>Streamlit</b> & <b>Google Gemini AI</b> | Developed by 
    <a href="https://www.linkedin.com/in/yashaswinijoshi23" target="_blank" style='color: #00ffcc; text-decoration: none;'>
    Yashaswini Joshi
    </a>
    </p>
""", unsafe_allow_html=True)