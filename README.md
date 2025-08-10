# Court-Data Fetcher & Mini-Dashboard

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Node.js](https://img.shields.io/badge/Node.js-18.18.0%2B-green.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

This project is a full-stack web application that allows users to fetch case information from the **Delhi High Court** public portal. It features a **React** frontend, a **Python FastAPI** backend, and a **SQLite** database for logging queries.

**License:** MIT License

---

## 1. Project Overview

**Court Chosen:** [Delhi High Court](https://delhihighcourt.nic.in/app/)

### Core Functionality

1. A user enters a **Case Type**, **Case Number**, and **Filing Year** into a simple web form.
2. The **React** frontend sends this request to the backend API.
3. The **FastAPI** backend uses a web scraping utility to fetch live data from the court's website.
4. The backend parses the JSON response to extract key information (**Party Names**, **Dates**, **Orders Link**).
5. The query and its parsed result are logged in a local **SQLite** database.
6. The parsed information is sent back to the frontend and displayed in a clean format.

### Tech Stack

- **Frontend:** React (Vite)
- **Backend:** Python with FastAPI
- **Database:** SQLite (SQLAlchemy ORM)
- **Web Scraping:** requests, BeautifulSoup4

---

## 2. Scraping & CAPTCHA Strategy

The Delhi High Court website has modern security to prevent basic scraping.  
Our strategy mimics a real browser's AJAX requests.

### Strategy Steps

- **Session Initiation:** Start a `requests.Session()` to persist cookies.
- **Cookie Acquisition:** Send a `GET` request to `/app/get-case-type-status` to get the `XSRF-TOKEN` cookie.
- **Dynamic Parameter Request:** Use a `GET` request with URL parameters (as the site’s JS does).
- **Header Spoofing:**
  - `X-XSRF-TOKEN` with the cookie value.
  - `X-Requested-With: XMLHttpRequest` to mimic AJAX.
- **No CAPTCHA Needed:** This endpoint does not require solving CAPTCHA.
- **JSON Parsing:** The response is JSON, parsed directly without messy HTML.

This approach is **robust**, **efficient**, and uses the site’s own data-fetching method.

---

## 3. Setup and Installation

### Prerequisites

- Python **3.8+**
- Node.js **v18.18.0+** (LTS recommended)

### Backend Setup (FastAPI)

#### 1. Navigate to the backend directory

```bash
cd backend
```

#### 2. Create and activate a virtual environment

##### On macOS/Linux:

#

```bash
python3 -m venv venv
source venv/bin/activate
```

##### On Windows:

#

```bash
python -m venv venv
.\venv\Scripts\activate
```

#### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

#### 4. Run the FastAPI server

```bash
uvicorn main:app --reload
```

##### The backend will be available at http://127.0.0.1:8000

### Frontend Setup (React + Vite)

#### 1. Navigate to the frontend directory

```bash
cd frontend
```

#### 2. Install npm packages

```bash
npm install
```

#### 3. Start the Vite development server

```bash
npm run dev
```

##### The frontend will be available at http://localhost:5173 (or another port if 5173 is busy)

#

#### 4. API Endpoint

The FastAPI backend exposes the following endpoint:

POST /api/fetch-case

Request Body (JSON):

```bash
{
  "case_type": "W.P.(C)",
  "case_number": "5595",
  "case_year": "2021"
}
```

Success Response (JSON):

```bash
{
  "party_names": "RM3D MINING AND LOGISTICS PVT LTD VS. COAL INDIA LIMITED & ORS.",
  "filing_date": "Year: 2021",
  "next_hearing_date": "07/08/2025",
  "orders_link": "https://delhihighcourt.nic.in/app/case-type-status-details/..."
}
```

Error Response (JSON):

```bash
{
  "detail": "Case not found or scraper failed."
}
```
