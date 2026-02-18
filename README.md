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
