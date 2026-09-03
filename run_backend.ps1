.venv\Scripts\activate
python scripts/seed_demo.py
uvicorn app.main:app --reload --app-dir backend
