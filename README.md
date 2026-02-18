# Clothes Resale Agent

This repository contains the code and configuration for the **Clothes Resale Agent**, an AI-powered system designed to automate the ingestion and processing of clothing inventory for a high-volume resale business.

## Core Components

### Inventory Ingestion Agent
The **Inventory Ingestion Agent** is responsible for converting unstructured images of clothing (front, back, tags) into structured JSON data.

**Key Capabilities:**
-   **Metadata Extraction:** accurate extraction of brand, size, material, and style.
-   **Defect Detection:** Identification of pilling, stains, and other imperfections.
-   **Structured Output:** Generates strictly formatted JSON data for downstream processing.

See [prompts/inventory_ingestion.md](prompts/inventory_ingestion.md) for the detailed system role and rules.
### Visual Merchandiser Agent
The **Visual Merchandiser Agent** specializes in Virtual Try-On (VTON) visualization.

**Key Capabilities:**
-   **Style Analysis:** Analyzes garment style to determine appropriate model and setting.
-   **VTON Generation:** Generates photorealistic on-model images using external tools.
-   **Contextual Styling:** Matches background and vibe to the specific garment type.

See [prompts/visual_merchandiser.md](prompts/visual_merchandiser.md) for the detailed system role.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Yidan-Xia_NordTech/clothes-resale-agent.git
    cd clothes-resale-agent
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure API Key:**
    - Copy `.env.example` to `.env`:
      ```bash
      cp .env.example .env
      ```
    - Open `.env` and paste your Google Gemini API key:
      ```
      GEMINI_API_KEY=your_actual_api_key
      ```

## Usage

Run the agent script by providing the path to one or more clothing images:

```bash
python src/main.py path/to/image.jpg
```

The script will output the structural JSON data to the console.

### Background Removal Tool

Pivot your images to a clean, professional look with the zero-cost background remover.

1.  **Run the tool:**
    ```bash
    python src/background_remover.py path/to/raw_image.jpg
    ```
    
    This will create an `output` folder containing the processed image with a solid white background.
