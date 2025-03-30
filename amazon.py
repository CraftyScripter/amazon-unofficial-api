import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

class AmazonScraper:
    def __init__(self):
        self.BASE_DOMAIN = 'https://www.amazon.in'
        self.headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'accept-language': 'en-US,en;q=0.9'
        }

    def search_products(self, query, page=1):
        """Search products on Amazon"""
        url = f"{self.BASE_DOMAIN}/s?k={query}&page={page}" if page > 1 else f"{self.BASE_DOMAIN}/s?k={query}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return self._parse_search_results(response.text)
        except Exception as e:
            print(f"Error scraping Amazon: {str(e)}")
            return []

    def get_product_details(self, product_id):
        """Get detailed product information by ASIN"""
        url = f"{self.BASE_DOMAIN}/dp/{product_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            data = {
                "asin": product_id,
                "title": self._get_text(soup.find(id='productTitle')),
                "price": self._get_price(soup),
                "rating": self._get_rating(soup),
                "description": self._get_description(soup),
                "features": self._get_bullet_points(soup),
                "specifications": self._get_specifications(soup),
                "images": self._get_images(soup),
                "variants": self._get_variants(soup),
                "availability": self._get_text(soup.find(id='availability')),
                "best_sellers_rank": self._get_best_sellers_rank(soup),
                "product_url": url
            }

            return {k: v for k, v in data.items() if v is not None}
        except Exception as e:
            print(f"Error getting product details: {str(e)}")
            return None

    def _parse_search_results(self, html_content):
        """Parse search results HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        product_cards = soup.find_all('div', {'data-component-type': 's-search-result'})
        return [self._extract_product_data(card) for card in product_cards]

    def _extract_product_data(self, card):
        """Extract product details from a card"""
        return {
            "asin": card.get('data-asin'),
            "title": self._get_text(card.find('h2')),
            "price": self._extract_price(card),
            "rating": self._extract_rating(card),
            "image_url": self._get_attr(card.find('img', {'class': 's-image'}), 'src'),
            "product_url": self._get_product_url(card),
            "prime_eligible": bool(card.find('i', {'class': 'a-icon-prime'}))
        }

    def _get_price(self, soup):
        current_price = soup.find('span', {'class': 'a-price-whole'})
        original_price = soup.find('span', {'class': 'a-price a-text-price'})
        original_price_text = None

        if original_price:
            original_price_text = original_price.get_text(strip=True)
            original_price_text = "₹" + original_price_text.split("₹")[1] if "₹" in original_price_text else original_price_text

        return {
            "current": f"₹{current_price.get_text().strip()}" if current_price else None,
            "original": original_price_text
        }

    def _extract_price(self, card):
        """Extract price information from search card"""
        current = card.find('span', {'class': 'a-price-whole'})
        original = card.find('span', {'class': 'a-price a-text-price'})
        
        return {
            "current": f"₹{current.get_text()}" if current else None,
            "original": original.find('span').get_text() if original else None,
            "discount": self._extract_discount(card)
        }

    def _extract_discount(self, card):
        """Extract discount information"""
        discount = card.find('span', string=re.compile(r'\(\d+% off\)'))
        if discount:
            match = re.search(r'(\d+)%', discount.get_text())
            return match.group(0) if match else None
        return None

    def _get_rating(self, soup):
        rating = soup.find('span', {'class': 'a-icon-alt'})
        review_count = soup.find('span', {'id': 'acrCustomerReviewText'})
        
        return {
            "stars": rating.get_text().split()[0] if rating else None,
            "review_count": review_count.get_text().split()[0] if review_count else None
        }

    def _extract_rating(self, card):
        """Extract rating information from search card"""
        rating = card.find('span', {'class': 'a-icon-alt'})
        count = card.find('span', {'class': 'a-size-base'})
        
        return {
            "stars": rating.get_text().split()[0] if rating else None,
            "count": count.get_text() if count else None
        }

    def _get_description(self, soup):
        description = soup.find('div', {'id': 'productDescription'})
        return self._get_text(description)

    def _get_bullet_points(self, soup):
        bullets = soup.find('ul', {'class': 'a-unordered-list a-vertical a-spacing-mini'})
        if bullets:
            return [li.get_text(strip=True) for li in bullets.find_all('li')]
        return None

    def _get_specifications(self, soup):
        specs = {}
        
        # Extracting specification tables from different sections
        tables = soup.find_all('table', {'class': 'a-keyvalue', 'id': re.compile(r'.*')})
        for table in tables:
            for row in table.find_all('tr'):
                th = row.find('th')
                td = row.find('td')
                if th and td:
                    key = self._get_text(th)
                    value = self._get_text(td)
                    if key and value:
                        specs[key] = value
        
        # Also trying to extract from 'prodDetails' section
        detail_section = soup.find('div', {'id': 'prodDetails'})
        if detail_section:
            rows = detail_section.find_all('tr')
            for row in rows:
                th = row.find('th')
                td = row.find('td')
                if th and td:
                    key = self._get_text(th)
                    value = self._get_text(td)
                    if key and value:
                        specs[key] = value

        return specs if specs else None

    def _get_images(self, soup):
        image_urls = []
        image_tags = soup.find_all('img', {'src': re.compile(r'https://m.media-amazon.com/images/')})
        
        for img in image_tags:
            img_url = img.get('src')
            if img_url and img_url not in image_urls:
                image_urls.append(img_url)
        
        return image_urls if image_urls else None

    def _get_variants(self, soup):
        variants = []
        variant_sections = soup.find_all('div', {'id': 'variation_color_name'})
        
        for section in variant_sections:
            variant_name = self._get_text(section.find('span', {'class': 'selection'}))
            if variant_name:
                variants.append(variant_name)
        
        return variants if variants else None

    def _get_best_sellers_rank(self, soup):
        bsr_section = soup.find('th', text=re.compile(r'Best Sellers Rank'))
        if bsr_section:
            rank_value = bsr_section.find_next('td')
            return self._get_text(rank_value)
        return None

    def _get_product_url(self, card):
        """Get product URL from search card"""
        link = card.find('a', {'class': 'a-link-normal'})
        return urljoin(self.BASE_DOMAIN, link['href']) if link else None

    def _get_text(self, element):
        """Safe text extraction"""
        return element.get_text(strip=True) if element else None

    def _get_attr(self, element, attr):
        """Safe attribute extraction"""
        return element.get(attr) if element else None