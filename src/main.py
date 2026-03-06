import os
import sys
import json
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image

def load_prompt(file_path):
    """Loads a prompt file from the project directory."""
    try:
        with open(file_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Prompt file not found at {file_path}", file=sys.stderr)
        sys.exit(1)

def main():
    # 1. Load Environment Variables
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment variables.", file=sys.stderr)
        print("Please create a .env file based on .env.example", file=sys.stderr)
        sys.exit(1)

    # 2. Configure Gemini
    genai.configure(api_key=api_key)
    
    # Using gemini-2.5-flash for speed and cost-effectiveness with images
    model = genai.GenerativeModel('gemini-2.5-flash')

    # 3. Parse Arguments (Image Paths)
    image_paths = sys.argv[1:]
    if not image_paths:
        print("Usage: python src/main.py <path_to_image1> [path_to_image2 ...]", file=sys.stderr)
        sys.exit(1)

    # 4. Load Prompts
    # Assuming script is run from project root, or we can use relative paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    system_prompt_path = os.path.join(base_dir, "prompts", "inventory_ingestion.md")
    task_prompt_path = os.path.join(base_dir, "prompts", "inventory_extraction_task.md")

    system_prompt = load_prompt(system_prompt_path)
    task_prompt = load_prompt(task_prompt_path)

    # 5. Prepare Inputs
    # Combine prompts and load images
    inputs = [system_prompt, task_prompt]
    
    for path in image_paths:
        try:
            img = Image.open(path)
            inputs.append(img)
        except Exception as e:
            print(f"Error loading image {path}: {e}", file=sys.stderr)
            sys.exit(1)

    inputs.append("Generate the JSON output based on the provided image(s).")

    # 6. Generate Content
    try:
        response = model.generate_content(inputs)
        
        # 7. Output Result
        # Clean up code blocks if the model includes them despite instructions
        text_response = response.text.strip()
        if text_response.startswith("```json"):
            text_response = text_response[7:]
        if text_response.endswith("```"):
            text_response = text_response[:-3]
            
        print(text_response.strip())

    except Exception as e:
        print(f"Error generating content: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
