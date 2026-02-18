import os
import sys
from PIL import Image
from rembg import remove

def process_image(input_path, output_folder="output"):
    """
    Removes the background from an image, replaces it with white, and saves it.
    
    Args:
        input_path (str): Path to the original image.
        output_folder (str): Directory to save the processed image.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    filename = os.path.basename(input_path)
    name, ext = os.path.splitext(filename)
    output_path = os.path.join(output_folder, f"{name}_processed.jpg")

    try:
        print(f"Processing: {input_path}...")
        
        # 1. Load Original Image
        original = Image.open(input_path)
        
        # 2. Remove Background (returns RGBA)
        print("  - Removing background...")
        removed_bg = remove(original)
        
        # 3. Create Solid White Background
        # Create a white image of the same size
        white_bg = Image.new("RGB", original.size, (255, 255, 255))
        
        # 4. Composite
        # Paste the cutout onto the white background using the alpha channel as a mask
        print("  - Applying white background...")
        white_bg.paste(removed_bg, mask=removed_bg.split()[3]) # Use alpha channel as mask
        
        # 5. Save
        white_bg.save(output_path, "JPEG", quality=95)
        print(f"Done! Saved to: {output_path}")
        return output_path

    except Exception as e:
        print(f"Error processing {input_path}: {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/background_remover.py <path_to_image> [output_folder]")
        sys.exit(1)
        
    img_path = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
    
    process_image(img_path, out_dir)
