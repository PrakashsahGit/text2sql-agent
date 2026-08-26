from fastapi import FastAPI
from tools.analyzer import analyze_data

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Analyzer API running 🚀"}


@app.post("/analyze")
def analyze(query: str):
    # Sample data (you can later replace with DB output)
    data = [
        {"product_name": "Product A", "revenue": 1000, "region": "Kathmandu"},
        {"product_name": "Product B", "revenue": 500, "region": "Pokhara"},
        {"product_name": "Product C", "revenue": 1200, "region": "Lalitpur"},
    ]

    result = analyze_data(query, data)

    return {
        "query": query,
        "insight": result
    }