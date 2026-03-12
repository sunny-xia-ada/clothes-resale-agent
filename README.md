# 💍 XYLAB Luxe Resale Agent

> **An AI-powered full-stack web app for premium clothing resale.** Upload a photo, get an instant professional price appraisal, platform-specific listing copy, and a clean white-background product image — all in seconds.

---

## ✨ What It Does

| Feature | Description |
|---|---|
| 🖼️ **Background Removal** | Strips messy backgrounds and replaces with clean white using `rembg` (runs 100% locally, zero cost) |
| 🤖 **AI Appraisal** | Google Gemini analyzes the item and returns fast-sale price, market value, brand, category, and condition |
| 📝 **Listing Copywriter** | Auto-generates platform-optimized descriptions for Poshmark, eBay, Mercari, and Depop |
| 💅 **XYLAB UI** | Beautiful pink-themed mobile-friendly React interface with Loopy loading animations |
| 📦 **Inventory Tracking** | Saves processed items to `inventory.csv` for easy tracking |

---

## 🏗️ Architecture

```
clothes-resale-agent/
├── api.py                  # FastAPI backend (POST /process-item)
├── src/
│   └── background_remover.py  # rembg image processing
├── prompts/                # Gemini system prompts
│   ├── inventory_ingestion.md
│   └── visual_merchandiser.md
├── output/                 # Processed images saved here
├── inventory.csv           # Running inventory database
└── frontend/               # React + TypeScript + Tailwind UI
    └── src/
        ├── App.tsx         # Main app with upload → processing → results flow
        └── components/
            └── resale-agent/
                ├── upload-zone.tsx
                ├── brand-tier-toggle.tsx
                ├── image-comparison.tsx
                ├── pricing-card.tsx
                ├── description-accordions.tsx
                └── floating-cta.tsx
```

---

## 🛠️ Tech Stack

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) — REST API
- [Google Gemini](https://ai.google.dev/) (`gemini-2.0-flash`) — AI vision & copywriting
- [rembg](https://github.com/danielgatis/rembg) — Local background removal
- [Pillow](https://python-pillow.org/) — Image processing

**Frontend**
- [React](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/) + [Vite](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/) with custom XYLAB pink color system
- [shadcn/ui](https://ui.shadcn.com/) component primitives
- [Lucide React](https://lucide.dev/) icons

---

## 🚀 Getting Started

### 1. Clone & install backend dependencies

```bash
git clone https://github.com/sunny-xia-ada/clothes-resale-agent.git
cd clothes-resale-agent
pip install -r requirements.txt
```

### 2. Configure your Gemini API key

Create a `.env` file in the project root:

```bash
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

> Get a free API key at [aistudio.google.com](https://aistudio.google.com/app/apikey)

### 3. Start the backend

```bash
uvicorn api:app --reload --port 8000
```

### 4. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 📡 API Reference

### `POST /process-item`

Uploads an image and returns AI analysis.

**Request** — `multipart/form-data`

| Field | Type | Description |
|---|---|---|
| `file` | `File` | Clothing image (JPEG/PNG) |
| `brand_tier` | `string` | `"luxury/designer"` or `"regular"` |

**Response** — `application/json`

```json
{
  "pricing": {
    "fastSale": 850,
    "marketValue": 1200,
    "currency": "USD"
  },
  "descriptions": {
    "poshmark": "...",
    "ebay": "...",
    "mercari": "...",
    "depop": "..."
  },
  "itemDetails": {
    "brand": "Gucci",
    "category": "Handbag",
    "condition": "Excellent"
  },
  "processedImage": "http://localhost:8000/output/item_processed.jpg"
}
```

---

## 📈 Development Progress

### ✅ Phase 1 — AI & Processing Core
- Gemini prompt engineering for structured JSON metadata extraction
- Local background removal with `rembg` (zero API cost)
- Price prediction and platform-specific copywriting
- Initial Streamlit MVP for pipeline validation

### ✅ Phase 2 — Backend (FastAPI)
- Migrated to headless FastAPI service
- `POST /process-item` endpoint with image upload, AI routing, and CSV persistence
- Static file serving for processed output images
- CORS configured for frontend integration

### ✅ Phase 3 — Frontend (React)
- Full React + TypeScript + Vite frontend
- XYLAB pink design system with custom Tailwind tokens
- Upload → Processing (Loopy animation) → Results flow
- Pricing card, image comparison, description accordions
- Error states with personality-driven Loopy error messages
- Mobile-first responsive layout

### 🚧 Phase 4 — In Progress
- Real Gemini AI integration (currently in mock/UI dev mode)
- User authentication and multi-user inventory
- Export to Poshmark / eBay draft listings via API

---

## 🔒 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | ✅ | Google Gemini API key |

---

## 📄 License

MIT — built with 💍 by XYLAB
