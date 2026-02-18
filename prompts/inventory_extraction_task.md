### TASK
Analyze the attached image(s) of a clothing item and generate a JSON object containing the listing details.

### EXTRACTION GUIDELINES

1. **Brand & ID:** Identify the brand logo or text. If it is a sub-brand (e.g., 'Lululemon Lab' vs 'Lululemon'), specify it.
2. **Visual Characteristics:**
   - **Category:** Be specific (e.g., use 'Wide-Leg Trousers' instead of just 'Pants').
   - **Color:** Use standard color names (e.g., 'Navy Blue', 'Burgundy').
   - **Pattern:** Describe the print (e.g., 'Houndstooth', 'Floral', 'Solid').
3. **Materials:** If a care tag is visible, extract the exact fabric composition (e.g., '100% Cotton'). If not, infer the texture (e.g., 'Denim-like', 'Satin finish').
4. **Condition Assessment:**
   - Grade the item: 'New with Tags', 'Excellent', 'Good', or 'Fair'.
   - List SPECIFIC flaws if visible (e.g., 'minor pilling on underarm').
5. **SEO & Style:**
   - Generate 5-10 keywords relevant to current fashion trends (e.g., 'Y2K', 'Gorpcore', 'Old Money', 'Coquette').
   - Suggest the target demographic (Women, Men, Unisex).

### REQUIRED JSON OUTPUT STRUCTURE
{
  "basics": {
    "title_candidate": "String (e.g., Reformation Red Floral Midi Dress)",
    "brand": "String",
    "sub_brand": "String or null",
    "category": "String",
    "size_type": "String (Regular, Petite, Plus)",
    "size_on_tag": "String",
    "gender": "String"
  },
  "visuals": {
    "color_primary": "String",
    "color_secondary": "String or null",
    "pattern": "String",
    "material_composition": "String (e.g., 80% Cotton, 20% Polyester)",
    "neckline": "String or null",
    "sleeve_style": "String or null"
  },
  "condition": {
    "grade": "String",
    "defects": ["String", "String"],
    "is_vintage": "Boolean"
  },
  "marketing": {
    "keywords": ["String", "String", "String"],
    "suggested_occasions": ["String", "String"]
  }
}
