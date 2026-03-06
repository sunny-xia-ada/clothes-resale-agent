import os
import streamlit as st
from PIL import Image
import tempfile
import sys
import base64
import json
import csv
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

def predict_price_with_gemini(extracted_json, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(base_dir, "prompts", "price_prediction.md")
    system_prompt = load_prompt(prompt_path)
    
    if not system_prompt:
        return None
        
    try:
        parsed_data = json.loads(extracted_json)
        
        # safely access nested dictionaries
        basics = parsed_data.get("basics", {})
        condition_data = parsed_data.get("condition", {})
        
        brand = basics.get("brand", "Unknown") if isinstance(basics, dict) else "Unknown"
        category = basics.get("category", "Unknown") if isinstance(basics, dict) else "Unknown"
        
        # Get the condition grade, or default back to the entire condition object if it's not a dict
        if isinstance(condition_data, dict):
            condition = condition_data.get("grade", "Unknown")
        else:
            condition = str(condition_data)
            
        input_data = f"Brand: {brand}\\nCategory: {category}\\nCondition: {condition}"
        inputs = [system_prompt, input_data]
        
        response = model.generate_content(inputs)
        text_response = response.text.strip()
        if text_response.startswith("```json"):
            text_response = text_response[7:]
        if text_response.endswith("```"):
            text_response = text_response[:-3]
        return text_response.strip()
    except Exception as e:
        st.error(f"Error predicting price: {e}")
        return None

def generate_copywriting_with_gemini(extracted_json, api_key, is_luxury):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(base_dir, "prompts", "platform_copywriting.md")
    system_prompt = load_prompt(prompt_path)
    
    if not system_prompt:
        return None
        
    try:
        routing_instruction = ""
        if is_luxury:
            routing_instruction = "\n\nIMPORTANT: Since this is a Luxury/Designer brand, generate ALL 5 descriptions: Poshmark, eBay, Mercari, Vestiaire Collective, and Fashionphile."
        else:
            routing_instruction = "\n\nIMPORTANT: Since this is NOT a Luxury/Designer brand, ONLY generate Poshmark, eBay, and Mercari descriptions. Omit Vestiaire Collective and Fashionphile from the JSON entirely."
            
        inputs = [system_prompt + routing_instruction, f"JSON Data: {extracted_json}"]
        
        response = model.generate_content(inputs)
        text_response = response.text.strip()
        if text_response.startswith("```json"):
            text_response = text_response[7:]
        if text_response.endswith("```"):
            text_response = text_response[:-3]
        return text_response.strip()
    except Exception as e:
        st.error(f"Error generating copywriting: {e}")
        return None

def flatten_and_save_data(extracted_json, price_json, copy_json, orig_path, proc_path):
    try:
        data = json.loads(extracted_json)
        price_data = json.loads(price_json) if price_json else {}
        copy_data = json.loads(copy_json) if copy_json else {}
        
        flat = {}
        # flatten extracted sections
        for section in ["basics", "visuals", "condition"]:
            for k, v in data.get(section, {}).items():
                if isinstance(v, list):
                    flat[f"{section}_{k}"] = ", ".join([str(i) for i in v])
                else:
                    flat[f"{section}_{k}"] = v
                    
        # flatten marketing
        mkt = data.get("marketing", {})
        flat["marketing_keywords"] = ", ".join(mkt.get("keywords", []))
        flat["marketing_occasions"] = ", ".join(mkt.get("suggested_occasions", []))
        
        # pricing and copywriting
        flat["fast_sale_price"] = price_data.get("fast_sale_price", "")
        flat["market_value_price"] = price_data.get("market_value_price", "")
        
        flat["poshmark_desc"] = copy_data.get("poshmark_description", "")
        flat["ebay_desc"] = copy_data.get("ebay_description", "")
        flat["mercari_desc"] = copy_data.get("mercari_description", "")
        flat["vestiaire_desc"] = copy_data.get("vestiaire_description", "")
        flat["fashionphile_desc"] = copy_data.get("fashionphile_description", "")
        
        # file paths
        flat["original_image_path"] = orig_path
        flat["processed_image_path"] = proc_path
        
        # write to csv
        base_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file = os.path.join(base_dir, "inventory.csv")
        file_exists = os.path.isfile(csv_file)
        
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            # We determine headers from the dictionary keys
            headers = list(flat.keys())
            writer = csv.DictWriter(f, fieldnames=headers)
            
            if not file_exists:
                writer.writeheader()
                
            writer.writerow(flat)
            
        return True
    except Exception as e:
        st.error(f"Error saving to CSV: {e}")
        return False

def main():
    st.set_page_config(page_title="Clothes Resale Agent", layout="wide")
    
    # Inject minimal CSS for rounded corners
    st.markdown("""
    <style>
    img, div[data-testid="stImage"] > img {
        border-radius: 15px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state for retaining extraction data
    if 'processing_done' not in st.session_state:
        st.session_state.processing_done = False
        

        
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
            
    # Input options: mobile-friendly camera or file uploader
    tab1, tab2 = st.tabs(["📸 Take Photo", "📂 Upload File"])
    
    with tab1:
        camera_file = st.camera_input("Take a photo directly")
        
    with tab2:
        uploaded_file = st.file_uploader("Upload a raw clothing image...", type=["jpg", "jpeg", "png"])
        
    active_file = camera_file if camera_file is not None else uploaded_file
    
    tier_option = st.radio(
        "Select Brand Tier Routing:",
        options=[
            'Luxury/Designer (Include Vestiaire & Fashionphile)',
            'Regular/Fast Fashion (Poshmark, eBay, Mercari only)'
        ],
        index=1
    )
    is_luxury = tier_option == 'Luxury/Designer (Include Vestiaire & Fashionphile)'
    
    if active_file is not None:
        # We don't use temp_dir for saving paths to CSV; we save to output directory directly
        os.makedirs("output", exist_ok=True)
        file_name = active_file.name if hasattr(active_file, 'name') and active_file.name else "camera_capture.jpg"
        original_filepath = os.path.join("output", file_name)
        
        # Display the uploaded file neatly before processing
        st.markdown("### Ready to Process!")
        
        if st.button("✨ Process Image", type="primary"):
            # Clean up old output logic and state
            st.session_state.processing_done = False
            
            with open(original_filepath, "wb") as f:
                f.write(active_file.getbuffer())
                
            st.divider()
            st.subheader("Results")
            
            # 1. Background removal
            st.markdown("### 🖼️ Image Processing")
            res_col1, res_col2 = st.columns(2)
            
            with res_col1:
                st.markdown("**Original Image**")
                st.image(original_filepath, use_container_width=True)
                
            with res_col2:
                st.markdown("**Processed Image**")
                with st.spinner("🧹 Removing background..."):
                    processed_img_path = process_image(original_filepath, output_folder="output")
                    
                if processed_img_path and os.path.exists(processed_img_path):
                    st.image(processed_img_path, use_container_width=True)
                    st.success("Background removed!")
                else:
                    st.error("Background removal failed.")
                    st.stop()
            
            # 2. Information Extraction
            st.markdown("### 🪄 AI Extraction & Analysis")
            with st.spinner("🤖 Analyzing garment specifics..."):
                json_data = analyze_image_with_gemini(processed_img_path, api_key)
                
                if json_data:
                    with st.expander("📋 Extracted Attributes"):
                        try:
                            parsed = json.loads(json_data)
                            basics = parsed.get("basics", {})
                            cond = parsed.get("condition", {})
                            st.markdown(f"**Brand:** {basics.get('brand', 'Unknown')} ({basics.get('brand_tier', 'Uncategorized')})")
                            st.markdown(f"**Category:** {basics.get('category', 'Unknown')}")
                            st.markdown(f"**Size:** {basics.get('size_on_tag', 'Unknown')}")
                            st.markdown(f"**Condition:** {cond.get('grade', 'Unknown')}")
                            # You can format the rest as needed, but this prevents displaying raw JSON directly.
                        except Exception as e:
                            st.json(json_data) # Fallback if parsing fails

                    st.markdown("### 💰 Price Prediction")
                    with st.spinner("🤖 Calculating market value..."):
                        price_json = predict_price_with_gemini(json_data, api_key)
                        if price_json:
                            with st.expander("💸 Suggested Pricing Strategy"):
                                try:
                                    price_parsed = json.loads(price_json)
                                    st.metric("Fast Sale Price", f"${price_parsed.get('fast_sale_price', '---')}")
                                    st.metric("Market Value Price", f"${price_parsed.get('market_value_price', '---')}")
                                except Exception as e:
                                    st.json(price_json)
                        else:
                            st.error("Failed to predict price.")
                            
                    st.markdown("### ✍️ Platform Copywriting")
                    with st.spinner("🤖 Generating listing descriptions..."):
                        copy_json = generate_copywriting_with_gemini(json_data, api_key, is_luxury)
                        if copy_json:
                            try:
                                copy_data = json.loads(copy_json)
                                if "poshmark_description" in copy_data:
                                    with st.expander("🎀 Poshmark Draft", expanded=False):
                                        st.info(copy_data.get("poshmark_description", ""))
                                if "ebay_description" in copy_data:
                                    with st.expander("✨ eBay Draft", expanded=False):
                                        st.info(copy_data.get("ebay_description", ""))
                                if "mercari_description" in copy_data:
                                    with st.expander("🛍️ Mercari Draft", expanded=False):
                                        st.info(copy_data.get("mercari_description", ""))
                                if "vestiaire_description" in copy_data:
                                    with st.expander("💎 Vestiaire Collective Draft", expanded=False):
                                        st.info(copy_data.get("vestiaire_description", ""))
                                if "fashionphile_description" in copy_data:
                                    with st.expander("👜 Fashionphile Draft", expanded=False):
                                        st.info(copy_data.get("fashionphile_description", ""))
                            except Exception as e:
                                st.json(copy_json)
                        else:
                            st.error("Failed to generate copywriting.")
                            
                    # Save context to session state
                    st.session_state.processing_done = True
                    st.session_state.json_data = json_data
                    st.session_state.price_json = price_json
                    st.session_state.copy_json = copy_json
                    st.session_state.original_filepath = original_filepath
                    st.session_state.processed_img_path = processed_img_path
                    
                else:
                    st.error("Failed to extract data.")
                    
        # Show the Approve button outside the evaluation loop, provided processing is completed
        if st.session_state.processing_done:
            st.divider()
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🎀 Save to Inventory 🎀", type="primary", use_container_width=True):
                    success = flatten_and_save_data(
                        st.session_state.json_data, 
                        st.session_state.price_json, 
                        st.session_state.copy_json, 
                        st.session_state.original_filepath, 
                        st.session_state.processed_img_path
                    )
                    
                    if success:
                        st.success(f"Item added to inventory! Saved original and processed images to `{st.session_state.original_filepath}` & `{st.session_state.processed_img_path}`.")
                        # Clear state for next garament
                        st.session_state.processing_done = False
                        # Optionally, we could clear the uploader here too, but Streamlit uploader is driven by user input.

if __name__ == "__main__":
    main()
