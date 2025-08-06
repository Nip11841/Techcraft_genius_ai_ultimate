"""
Web Scraping System for Real-time Data Collection
Monitors prices, technologies, and research for TechCraft Genius AI
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import re
from urllib.parse import urljoin, urlparse
import sqlite3
from dataclasses import dataclass

@dataclass
class ComponentPrice:
    name: str
    price: float
    currency: str
    supplier: str
    url: str
    availability: str
    last_updated: datetime

@dataclass
class TechNews:
    title: str
    summary: str
    url: str
    source: str
    published_date: datetime
    relevance_score: float

class PriceMonitor:
    def __init__(self, db_path: str = "price_monitor.db"):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for storing price data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS component_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                currency TEXT NOT NULL,
                supplier TEXT NOT NULL,
                url TEXT NOT NULL,
                availability TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tech_news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                summary TEXT,
                url TEXT UNIQUE NOT NULL,
                source TEXT NOT NULL,
                published_date TIMESTAMP,
                relevance_score REAL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def scrape_amazon_uk_price(self, search_term: str) -> List[ComponentPrice]:
        """Scrape Amazon UK for component prices"""
        prices = []
        try:
            # Amazon UK search URL
            search_url = f"https://www.amazon.co.uk/s?k={search_term.replace(' ', '+')}"
            
            response = self.session.get(search_url)
            if response.status_code != 200:
                logging.warning(f"Failed to fetch Amazon UK data: {response.status_code}")
                return prices
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find product containers
            products = soup.find_all('div', {'data-component-type': 's-search-result'})
            
            for product in products[:5]:  # Limit to first 5 results
                try:
                    # Extract product name
                    name_elem = product.find('h2', class_='a-size-mini')
                    if not name_elem:
                        continue
                    name = name_elem.get_text(strip=True)
                    
                    # Extract price
                    price_elem = product.find('span', class_='a-price-whole')
                    if not price_elem:
                        continue
                    
                    price_text = price_elem.get_text(strip=True).replace(',', '')
                    price = float(re.findall(r'\d+', price_text)[0])
                    
                    # Extract URL
                    link_elem = product.find('h2').find('a')
                    if link_elem:
                        url = urljoin("https://www.amazon.co.uk", link_elem.get('href'))
                    else:
                        url = search_url
                    
                    # Check availability
                    availability = "In Stock"
                    availability_elem = product.find('span', string=re.compile(r'(out of stock|unavailable)', re.I))
                    if availability_elem:
                        availability = "Out of Stock"
                    
                    prices.append(ComponentPrice(
                        name=name,
                        price=price,
                        currency="GBP",
                        supplier="Amazon UK",
                        url=url,
                        availability=availability,
                        last_updated=datetime.now()
                    ))
                
                except Exception as e:
                    logging.warning(f"Error parsing Amazon product: {e}")
                    continue
            
            time.sleep(1)  # Be respectful to the server
            
        except Exception as e:
            logging.error(f"Error scraping Amazon UK: {e}")
        
        return prices
    
    def scrape_currys_price(self, search_term: str) -> List[ComponentPrice]:
        """Scrape Currys UK for component prices"""
        prices = []
        try:
            search_url = f"https://www.currys.co.uk/search?q={search_term.replace(' ', '%20')}"
            
            response = self.session.get(search_url)
            if response.status_code != 200:
                logging.warning(f"Failed to fetch Currys data: {response.status_code}")
                return prices
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find product containers (Currys specific selectors)
            products = soup.find_all('article', class_='product-item')
            
            for product in products[:3]:  # Limit to first 3 results
                try:
                    # Extract product name
                    name_elem = product.find('h3')
                    if not name_elem:
                        continue
                    name = name_elem.get_text(strip=True)
                    
                    # Extract price
                    price_elem = product.find('span', class_='price')
                    if not price_elem:
                        continue
                    
                    price_text = price_elem.get_text(strip=True)
                    price_match = re.search(r'£([\d,]+\.?\d*)', price_text)
                    if not price_match:
                        continue
                    
                    price = float(price_match.group(1).replace(',', ''))
                    
                    # Extract URL
                    link_elem = product.find('a')
                    if link_elem:
                        url = urljoin("https://www.currys.co.uk", link_elem.get('href'))
                    else:
                        url = search_url
                    
                    prices.append(ComponentPrice(
                        name=name,
                        price=price,
                        currency="GBP",
                        supplier="Currys",
                        url=url,
                        availability="Check Website",
                        last_updated=datetime.now()
                    ))
                
                except Exception as e:
                    logging.warning(f"Error parsing Currys product: {e}")
                    continue
            
            time.sleep(1)  # Be respectful to the server
            
        except Exception as e:
            logging.error(f"Error scraping Currys: {e}")
        
        return prices
    
    def monitor_component_prices(self, components: List[str]) -> Dict[str, List[ComponentPrice]]:
        """Monitor prices for a list of components across multiple suppliers"""
        all_prices = {}
        
        for component in components:
            logging.info(f"Monitoring prices for: {component}")
            component_prices = []
            
            # Scrape Amazon UK
            amazon_prices = self.scrape_amazon_uk_price(component)
            component_prices.extend(amazon_prices)
            
            # Scrape Currys
            currys_prices = self.scrape_currys_price(component)
            component_prices.extend(currys_prices)
            
            # Store in database
            self.store_prices(component_prices)
            
            all_prices[component] = component_prices
            
            # Delay between components to avoid rate limiting
            time.sleep(2)
        
        return all_prices
    
    def store_prices(self, prices: List[ComponentPrice]):
        """Store prices in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for price in prices:
            cursor.execute('''
                INSERT INTO component_prices 
                (name, price, currency, supplier, url, availability, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                price.name, price.price, price.currency, price.supplier,
                price.url, price.availability, price.last_updated
            ))
        
        conn.commit()
        conn.close()
    
    def get_best_prices(self, component: str, limit: int = 5) -> List[ComponentPrice]:
        """Get best prices for a component from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT name, price, currency, supplier, url, availability, last_updated
            FROM component_prices
            WHERE name LIKE ?
            ORDER BY price ASC
            LIMIT ?
        ''', (f'%{component}%', limit))
        
        results = cursor.fetchall()
        conn.close()
        
        prices = []
        for row in results:
            prices.append(ComponentPrice(
                name=row[0],
                price=row[1],
                currency=row[2],
                supplier=row[3],
                url=row[4],
                availability=row[5],
                last_updated=datetime.fromisoformat(row[6])
            ))
        
        return prices


class TechNewsMonitor:
    def __init__(self, db_path: str = "price_monitor.db"):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_tech_news(self) -> List[TechNews]:
        """Scrape technology news from various sources"""
        news_items = []
        
        # Scrape from multiple tech news sources
        sources = [
            {
                'name': 'TechCrunch',
                'url': 'https://techcrunch.com/category/hardware/',
                'selector': 'article'
            },
            {
                'name': 'The Verge',
                'url': 'https://www.theverge.com/tech',
                'selector': 'article'
            }
        ]
        
        for source in sources:
            try:
                response = self.session.get(source['url'])
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                articles = soup.find_all(source['selector'])[:5]  # Limit to 5 articles
                
                for article in articles:
                    try:
                        # Extract title
                        title_elem = article.find(['h1', 'h2', 'h3'])
                        if not title_elem:
                            continue
                        title = title_elem.get_text(strip=True)
                        
                        # Extract URL
                        link_elem = article.find('a')
                        if not link_elem:
                            continue
                        url = urljoin(source['url'], link_elem.get('href'))
                        
                        # Extract summary (first paragraph or description)
                        summary_elem = article.find('p')
                        summary = summary_elem.get_text(strip=True) if summary_elem else ""
                        
                        # Calculate relevance score based on keywords
                        relevance_keywords = [
                            'smart home', 'iot', 'automation', 'ai', 'machine learning',
                            'raspberry pi', 'arduino', 'diy', 'maker', 'electronics'
                        ]
                        
                        relevance_score = 0
                        text_to_check = (title + " " + summary).lower()
                        for keyword in relevance_keywords:
                            if keyword in text_to_check:
                                relevance_score += 1
                        
                        relevance_score = relevance_score / len(relevance_keywords)
                        
                        news_items.append(TechNews(
                            title=title,
                            summary=summary,
                            url=url,
                            source=source['name'],
                            published_date=datetime.now(),
                            relevance_score=relevance_score
                        ))
                    
                    except Exception as e:
                        logging.warning(f"Error parsing article from {source['name']}: {e}")
                        continue
                
                time.sleep(1)  # Be respectful
                
            except Exception as e:
                logging.error(f"Error scraping {source['name']}: {e}")
        
        return news_items
    
    def store_news(self, news_items: List[TechNews]):
        """Store news items in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for news in news_items:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO tech_news 
                    (title, summary, url, source, published_date, relevance_score)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    news.title, news.summary, news.url, news.source,
                    news.published_date, news.relevance_score
                ))
            except sqlite3.IntegrityError:
                # URL already exists, skip
                continue
        
        conn.commit()
        conn.close()
    
    def get_relevant_news(self, limit: int = 10) -> List[TechNews]:
        """Get most relevant tech news from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT title, summary, url, source, published_date, relevance_score
            FROM tech_news
            WHERE relevance_score > 0.1
            ORDER BY relevance_score DESC, published_date DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        news_items = []
        for row in results:
            news_items.append(TechNews(
                title=row[0],
                summary=row[1],
                url=row[2],
                source=row[3],
                published_date=datetime.fromisoformat(row[4]),
                relevance_score=row[5]
            ))
        
        return news_items


class WeatherIntegration:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "demo_key"  # Use OpenWeatherMap API
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    def get_london_weather(self) -> Dict[str, Any]:
        """Get current weather data for London"""
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': 'London,UK',
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return {
                    'temperature': data['main']['temp'],
                    'humidity': data['main']['humidity'],
                    'description': data['weather'][0]['description'],
                    'wind_speed': data['wind']['speed'],
                    'pressure': data['main']['pressure'],
                    'visibility': data.get('visibility', 0) / 1000,  # Convert to km
                    'timestamp': datetime.now()
                }
            else:
                logging.error(f"Weather API error: {response.status_code}")
                return {}
        
        except Exception as e:
            logging.error(f"Error fetching weather data: {e}")
            return {}
    
    def get_weather_forecast(self, days: int = 5) -> List[Dict[str, Any]]:
        """Get weather forecast for London"""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'q': 'London,UK',
                'appid': self.api_key,
                'units': 'metric',
                'cnt': days * 8  # 8 forecasts per day (3-hour intervals)
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                forecasts = []
                
                for item in data['list']:
                    forecasts.append({
                        'datetime': datetime.fromtimestamp(item['dt']),
                        'temperature': item['main']['temp'],
                        'humidity': item['main']['humidity'],
                        'description': item['weather'][0]['description'],
                        'rain_probability': item.get('pop', 0) * 100,
                        'wind_speed': item['wind']['speed']
                    })
                
                return forecasts
            else:
                logging.error(f"Forecast API error: {response.status_code}")
                return []
        
        except Exception as e:
            logging.error(f"Error fetching forecast data: {e}")
            return []


# Global instances
price_monitor = PriceMonitor()
news_monitor = TechNewsMonitor()
weather_service = WeatherIntegration()

def run_daily_data_collection():
    """Run daily data collection tasks"""
    logging.info("Starting daily data collection...")
    
    # Monitor common smart home component prices
    components = [
        "Raspberry Pi 4",
        "Arduino Uno",
        "Smart Light Bulb",
        "Smart Thermostat",
        "Security Camera",
        "Motion Sensor",
        "Smart Plug",
        "LED Strip"
    ]
    
    # Collect price data
    price_data = price_monitor.monitor_component_prices(components)
    logging.info(f"Collected prices for {len(price_data)} components")
    
    # Collect tech news
    news_items = news_monitor.scrape_tech_news()
    news_monitor.store_news(news_items)
    logging.info(f"Collected {len(news_items)} news items")
    
    # Get weather data
    weather_data = weather_service.get_london_weather()
    logging.info(f"Collected weather data: {weather_data.get('temperature', 'N/A')}°C")
    
    logging.info("Daily data collection completed")

if __name__ == "__main__":
    # Test the system
    run_daily_data_collection()
    
    # Example: Get best prices for Raspberry Pi
    best_prices = price_monitor.get_best_prices("Raspberry Pi")
    print(f"Best Raspberry Pi prices: {[f'{p.supplier}: £{p.price}' for p in best_prices]}")
    
    # Example: Get relevant tech news
    relevant_news = news_monitor.get_relevant_news(5)
    print(f"Relevant news: {[n.title for n in relevant_news]}")

