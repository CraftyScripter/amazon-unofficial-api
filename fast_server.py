import os
import threading
import time
import requests
from fastapi import FastAPI, Query, HTTPException
from amazon import AmazonScraper
from dotenv import load_dotenv

# Load .env file
load_dotenv()

app = FastAPI()
scraper = AmazonScraper()

RENDER_URL = os.getenv("RENDER_URL")
PORT = int(os.getenv("PORT", 10000))

@app.get("/")
def root():
    return {"status": "Success", "message": "Welcome to Amazon Scraper API"}

@app.get("/api/search")
def search_products(query: str = Query(...), page: int = Query(1)):
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter is required")
    results = scraper.search_products(query, page)
    return {"query": query, "page": page, "results": results}

@app.get("/api/product/{product_id}")
def get_product(product_id: str):
    if not product_id:
        raise HTTPException(status_code=400, detail="Product ID is required")
    product_details = scraper.get_product_details(product_id)
    if product_details:
        return product_details
    else:
        raise HTTPException(status_code=404, detail="Product not found or error occurred")


# ----------------- Keep-alive function -----------------
def keep_alive():
    while True:
        try:
            requests.get(RENDER_URL, timeout=10)
            print("Pinged self to prevent sleep")
        except Exception as e:
            print("Error pinging self:", e)
        time.sleep(30 * 60)  # 30 minutes delay

# Start the keep-alive thread when server starts
threading.Thread(target=keep_alive, daemon=True).start()
# -------------------------------------------------------


# Dynamic port handling for Render
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fast_server:app", host="0.0.0.0", port=PORT)
