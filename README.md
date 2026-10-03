# Business Listings Dashboard

Scrape business listings from Google Maps, store them in MySQL, serve them with FastAPI and visualise them in a React dashboard.

```
intern/
├── BACKEND/   # Backend: FastAPI API + MySQL loader (uv project)
├── FRONTEND/     # React + Vite dashboard
└── scrapper/     # Playwright scraper + cleaning script + final CSV
```

## Setup

Requirements: Python 3.14 + [uv](https://docs.astral.sh/uv/), Node 20+, MySQL/MariaDB running locally.

### 1. Backend

```bash
cd internship
cp .env.example .env            # Windows: copy .env.example .env   (then set DB_PASSWORD if you have one)
uv sync
uv run python load_data.py      # creates business_db.listing_master and loads the CSV
uv run uvicorn main:app --reload
```

API runs on http://localhost:8000 (docs at `/docs`).

| Endpoint | Returns |
|---|---|
| `GET /city-count` | listings per city |
| `GET /category-count` | listings per category |
| `GET /source-count` | listings per source |


### 2. Frontend

```bash
cd FRONTEND
npm install
cp .env.example .env            # optional; only needed if the API is not on localhost:8000
npm run dev
```

Open http://localhost:5173.

### 3. Re-scraping (optional)

```bash
cd internship
uv run playwright install firefox
uv run python ../scrapper/scraper.py     # writes scrapper/gmaps_data.csv
uv run python ../scrapper/cleaning.py    # writes scrapper/full_FINAL_FIXED.csv
uv run python load_data.py               # reload into MySQL
```

Note: scraping Google Maps may be against its Terms of Service - use for learning/demo purposes only.
