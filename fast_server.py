import os
from fastapi import FastAPI, Query, HTTPException
from amazon import AmazonScraper

app = FastAPI()
scraper = AmazonScraper()

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

# Dynamic port handling for Render
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("fast_server:app", host="0.0.0.0", port=port)
