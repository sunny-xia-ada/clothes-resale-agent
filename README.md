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
See [prompts/inventory_extraction_task.md](prompts/inventory_extraction_task.md) for the specific task instructions and JSON output schema.

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
