import os
import streamlit as st
from PIL import Image
import tempfile
import sys
import base64
from dotenv import load_dotenv

# Import project modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.background_remover import process_image

# To reuse the generation logic, we will need to load prompts and configure gemini
import google.generativeai as genai

def load_prompt(file_path):
    """Loads a prompt file from the project directory."""
    try:
        with open(file_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"Error: Prompt file not found at {file_path}")
        return None

def analyze_image_with_gemini(image_path, api_key):
    """Runs the Inventory Ingestion Agent on a processed image."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    system_prompt_path = os.path.join(base_dir, "prompts", "inventory_ingestion.md")
    task_prompt_path = os.path.join(base_dir, "prompts", "inventory_extraction_task.md")
    
    system_prompt = load_prompt(system_prompt_path)
    task_prompt = load_prompt(task_prompt_path)
    
    if not system_prompt or not task_prompt:
        return None
        
    try:
        img = Image.open(image_path)
    except Exception as e:
        st.error(f"Failed to load image for analysis: {e}")
        return None
        
    inputs = [system_prompt, task_prompt, img, "Generate the JSON output based on the provided image(s)."]
    
    with st.spinner("🤖 Analyzing garment with Gemini..."):
        try:
            response = model.generate_content(inputs)
            text_response = response.text.strip()
            if text_response.startswith("```json"):
                text_response = text_response[7:]
            if text_response.endswith("```"):
                text_response = text_response[:-3]
            return text_response.strip()
        except Exception as e:
            st.error(f"Error generating content: {e}")
            return None

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = f'''
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-repeat: repeat;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="Clothes Resale Agent", layout="wide")
    
    # Try to set the Hello Kitty background
    try:
        set_bg(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hello_kitty_bg.png'))
    except Exception as e:
        pass
        
    st.title("👕 Clothes Resale Agent UI")
    st.markdown("Test the **Background Remover** and **Inventory Ingestion Agent** in one simple workflow.")
    
    # Check for API key
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        api_key = st.text_input("Enter your Gemini API Key:", type="password")
        if not api_key:
            st.warning("⚠️ Please provide a Gemini API Key to run the extraction.")
            st.stop()
            
    # File uploader
    uploaded_file = st.file_uploader("Upload a raw clothing image...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Create clear layout
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("1. Original Image")
            st.image(uploaded_file, use_container_width=True)
            
        # Create a temporary directory to save the file
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_input_path = os.path.join(temp_dir, uploaded_file.name)
            
            with open(temp_input_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            if st.button("✨ Process Image", type="primary"):
                # Clean up old output logic
                st.divider()
                st.subheader("Results")
                
                # 1. Background removal
                res_col1, res_col2 = st.columns(2)
                
                with res_col1:
                    with st.spinner("🧹 Removing background..."):
                        processed_img_path = process_image(temp_input_path, output_folder=temp_dir)
                        
                    if processed_img_path and os.path.exists(processed_img_path):
                        st.image(processed_img_path, caption="Processed Image", use_container_width=True)
                        st.success("Background removed successfully!")
                    else:
                        st.error("Background removal failed.")
                        st.stop()
                
                # 2. Information Extraction
                with res_col2:
                    st.markdown("### 📋 Extracted Structured Data")
                    json_data = analyze_image_with_gemini(processed_img_path, api_key)
                    
                    if json_data:
                        st.json(json_data)
                        st.success("Extraction complete!")
                    else:
                        st.error("Failed to extract data.")

if __name__ == "__main__":
    main()
