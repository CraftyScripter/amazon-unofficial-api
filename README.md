# Amazon Unofficial API

A Flask-based API that scrapes product data from amazon.in and returns it in JSON format.

## Features

- Search Amazon products by keyword
- Get detailed product information by ASIN
- Pagination support for search results
- Comprehensive product data including:
  - Pricing (current & original)
  - Ratings and reviews
  - Product descriptions and features
  - Technical specifications
  - Product images
  - Variants and availability

## Installation

1. Clone the repository:
   ```bash
    git clone https://github.com/CraftyScripter/amazon-unofficial-api.git
    cd amazon-scraper-api
   ```

2. Install dependencies:
   ```bash
    pip install -r requirements.txt
   ```

## Usage
The API will run at http://localhost:5000 in debug mode.
   ```bash
    python server.py
   ```

## API Endpoints

1. Search Products
   ```bash
    GET /api/search?query=<search_term>&page=<page_number>
   ```
2. Get Product Details
   ```bash
    GET /api/product/<product_id>
   ```

## NOTE : Amazon may block requests if made too frequently. Use responsibly.
