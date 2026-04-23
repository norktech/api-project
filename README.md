# 🔌 REST API — NorkTech

API built with FastAPI that serves book data collected by the web scraper.

## 🛠️ Technologies
- Python
- FastAPI
- Uvicorn
- OpenPyXL

## ▶️ How to run
pip install fastapi uvicorn openpyxl
uvicorn api:app --reload

## 📡 Endpoints
- GET / — API status
- GET /livros — List all books
- GET /livros/{nome} — Search book by name

---
Made by [NorkTech](https://github.com/norktech)