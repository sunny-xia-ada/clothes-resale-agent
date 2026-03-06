import os
import sys
import json
import csv
import shutil
import base64
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from dotenv import load_dotenv

import google.generativeai as genai

# Import project modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.background_remover import process_image

load_dotenv()

app = FastAPI(title="Clothes Resale API", description="Headless backend for processing clothing resale inventory")

# Add CORS middleware for the future React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_prompt(file_path):
    try:
        with open(file_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail=f"Prompt file not found at {file_path}")

def analyze_image_with_gemini(image_path, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    system_prompt_path = os.path.join(base_dir, "prompts", "inventory_ingestion.md")
    task_prompt_path = os.path.join(base_dir, "prompts", "inventory_extraction_task.md")
    
    system_prompt = load_prompt(system_prompt_path)
    task_prompt = load_prompt(task_prompt_path)
    
    try:
        img = Image.open(image_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load image for analysis: {e}")
        
    inputs = [system_prompt, task_prompt, img, "Generate the JSON output based on the provided image(s)."]
    
    try:
        response = model.generate_content(inputs)
        text_response = response.text.strip()
        if text_response.startswith("```json"):
            text_response = text_response[7:]
        if text_response.endswith("```"):
            text_response = text_response[:-3]
        return text_response.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing image with Gemini: {e}")

def predict_price_with_gemini(extracted_json, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(base_dir, "prompts", "price_prediction.md")
    system_prompt = load_prompt(prompt_path)
    
    try:
        parsed_data = json.loads(extracted_json)
        basics = parsed_data.get("basics", {})
        condition_data = parsed_data.get("condition", {})
        
        brand = basics.get("brand", "Unknown") if isinstance(basics, dict) else "Unknown"
        category = basics.get("category", "Unknown") if isinstance(basics, dict) else "Unknown"
        
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
        print(f"Error predicting price: {e}")
        return None

def generate_copywriting_with_gemini(extracted_json, api_key, is_luxury):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(base_dir, "prompts", "platform_copywriting.md")
    system_prompt = load_prompt(prompt_path)
    
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
        print(f"Error generating copywriting: {e}")
        return None

def flatten_and_save_data(extracted_json, price_json, copy_json, orig_path, proc_path):
    try:
        data = json.loads(extracted_json) if extracted_json else {}
        price_data = json.loads(price_json) if price_json else {}
        copy_data = json.loads(copy_json) if copy_json else {}
        
        flat = {}
        for section in ["basics", "visuals", "condition"]:
            for k, v in data.get(section, {}).items():
                if isinstance(v, list):
                    flat[f"{section}_{k}"] = ", ".join([str(i) for i in v])
                else:
                    flat[f"{section}_{k}"] = v
                    
        mkt = data.get("marketing", {})
        flat["marketing_keywords"] = ", ".join(mkt.get("keywords", []))
        flat["marketing_occasions"] = ", ".join(mkt.get("suggested_occasions", []))
        
        flat["fast_sale_price"] = price_data.get("fast_sale_price", "")
        flat["market_value_price"] = price_data.get("market_value_price", "")
        
        flat["poshmark_desc"] = copy_data.get("poshmark_description", "")
        flat["ebay_desc"] = copy_data.get("ebay_description", "")
        flat["mercari_desc"] = copy_data.get("mercari_description", "")
        flat["vestiaire_desc"] = copy_data.get("vestiaire_description", "")
        flat["fashionphile_desc"] = copy_data.get("fashionphile_description", "")
        
        flat["original_image_path"] = orig_path
        flat["processed_image_path"] = proc_path
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file = os.path.join(base_dir, "inventory.csv")
        file_exists = os.path.isfile(csv_file)
        
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            headers = list(flat.keys())
            writer = csv.DictWriter(f, fieldnames=headers)
            if not file_exists:
                writer.writeheader()
            writer.writerow(flat)
            
        return True
    except Exception as e:
        print(f"Error saving to CSV: {e}")
        return False

@app.post("/process-item")
async def process_item(
    file: UploadFile = File(...),
    is_luxury: bool = Form(False),
    api_key: str = Form(None)
):
    actual_api_key = api_key or os.getenv("GEMINI_API_KEY")
    if not actual_api_key:
        raise HTTPException(status_code=400, detail="Gemini API Key is required")
        
    os.makedirs("output", exist_ok=True)
    file_name = file.filename if file.filename else "upload.jpg"
    original_filepath = os.path.join("output", file_name)
    
    with open(original_filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 1. Background removal
    processed_img_path = process_image(original_filepath, output_folder="output")
    if not processed_img_path or not os.path.exists(processed_img_path):
        raise HTTPException(status_code=500, detail="Background removal failed")
        
    # 2. Extract Data
    json_data = analyze_image_with_gemini(processed_img_path, actual_api_key)
    if not json_data:
        raise HTTPException(status_code=500, detail="Failed to extract data")
        
    # 3. Predict Price
    price_json = predict_price_with_gemini(json_data, actual_api_key)
    
    # 4. Copywriting
    copy_json = generate_copywriting_with_gemini(json_data, actual_api_key, is_luxury)
    
    # Parse for proper JSON output response
    try:
        parsed_data = json.loads(json_data)
        parsed_price = json.loads(price_json) if price_json else {}
        parsed_copy = json.loads(copy_json) if copy_json else {}
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error parsing JSON from language model")
        
    # Save to CSV
    success = flatten_and_save_data(json_data, price_json, copy_json, original_filepath, processed_img_path)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save data to CSV pipeline")
        
    return {
        "status": "success",
        "message": "Item processed and added to inventory.",
        "data": {
            "extracted": parsed_data,
            "pricing": parsed_price,
            "copywriting": parsed_copy,
            "paths": {
                "original": original_filepath,
                "processed": processed_img_path
            }
        }
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
