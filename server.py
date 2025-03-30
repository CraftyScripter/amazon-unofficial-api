from flask import Flask, request, jsonify
from amazon import AmazonScraper

app = Flask(__name__)
scraper = AmazonScraper()

@app.route('/api/search', methods=['GET'])
def search_products():
    query = request.args.get('query')
    page = request.args.get('page', default=1, type=int)
    
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    
    results = scraper.search_products(query, page)
    return jsonify({
        "query": query,
        "page": page,
        "results": results
    })

@app.route('/api/product/<product_id>', methods=['GET'])
def get_product(product_id):
    if not product_id:
        return jsonify({"error": "Product ID is required"}), 400
    
    product_details = scraper.get_product_details(product_id)
    
    if product_details:
        return jsonify(product_details)
    else:
        return jsonify({"error": "Product not found or error occurred"}), 404

if __name__ == '__main__':
    app.run(debug=True)