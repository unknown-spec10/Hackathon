Hackathon API

Setup
- Create a .env in repo root with DATABASE_URL, e.g.
	DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/hackathon_db

Install
- pip install -r requirments.txt

Seed DB
- python -m database.seed

Run
- uvicorn main:app --reload

