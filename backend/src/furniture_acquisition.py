"""
Comprehensive Furniture & Item Acquisition Engine
Enables the TechCraft Genius AI to search, source, and acquire furniture and household items
from multiple platforms including second-hand markets, online retailers, and local sources.
"""

import json
import sqlite3
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import re
import time
from urllib.parse import urlencode, quote
import hashlib

class FurnitureAcquisitionEngine:
    def __init__(self, db_path: str = "furniture_acquisition.db"):
        self.db_path = db_path
        self.init_database()
        
        # UK-specific search endpoints and patterns
        self.search_platforms = {
            "gumtree": {
                "base_url": "https://www.gumtree.com/search",
                "search_params": {"q": "{query}", "search_category": "home-garden", "search_location": "london"},
                "price_pattern": r"£([\d,]+)",
                "title_selector": ".listing-title",
                "price_selector": ".listing-price",
                "location_selector": ".listing-location"
            },
            "facebook_marketplace": {
                "base_url": "https://www.facebook.com/marketplace/london/search",
                "search_params": {"query": "{query}", "category": "home"},
                "price_pattern": r"£([\d,]+)",
                "requires_auth": True
            },
            "ebay_uk": {
                "base_url": "https://www.ebay.co.uk/sch/i.html",
                "search_params": {"_nkw": "{query}", "_in_kw": "1", "_ex_kw": "", "_sacat": "11700", "_udlo": "", "_udhi": ""},
                "price_pattern": r"£([\d,]+\.\d{2})",
                "api_available": True
            },
            "amazon_uk": {
                "base_url": "https://www.amazon.co.uk/s",
                "search_params": {"k": "{query}", "rh": "n:11052591"},
                "price_pattern": r"£([\d,]+\.\d{2})",
                "api_available": True
            },
            "freecycle": {
                "base_url": "https://www.freecycle.org/browse/UK/London",
                "search_params": {"q": "{query}"},
                "price_pattern": "FREE",
                "free_items": True
            },
            "preloved": {
                "base_url": "https://www.preloved.co.uk/search",
                "search_params": {"keyword": "{query}", "section": "home-garden", "location": "london"},
                "price_pattern": r"£([\d,]+)"
            }
        }
        
    def init_database(self):
        """Initialize the furniture acquisition database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Search queries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_text TEXT NOT NULL,
                category TEXT,
                max_price REAL,
                min_price REAL,
                location TEXT DEFAULT 'London',
                condition_preference TEXT,
                size_requirements TEXT,
                color_preferences TEXT,
                material_preferences TEXT,
                style_preferences TEXT,
                urgency_level INTEGER DEFAULT 3,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_searched TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Found items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS found_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_id INTEGER,
                platform TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                price REAL,
                currency TEXT DEFAULT 'GBP',
                condition_item TEXT,
                location TEXT,
                seller_name TEXT,
                seller_rating REAL,
                item_url TEXT,
                image_urls TEXT,
                dimensions TEXT,
                material TEXT,
                brand TEXT,
                age_years INTEGER,
                delivery_available BOOLEAN,
                delivery_cost REAL,
                pickup_only BOOLEAN,
                negotiable BOOLEAN,
                match_score REAL,
                refurbishment_potential TEXT,
                estimated_refurb_cost REAL,
                total_estimated_cost REAL,
                found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'available',
                notes TEXT,
                FOREIGN KEY (query_id) REFERENCES search_queries (id)
            )
        ''')
        
        # Watchlist table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER,
                user_priority INTEGER DEFAULT 5,
                price_alert_threshold REAL,
                condition_alert BOOLEAN DEFAULT 0,
                location_alert_radius INTEGER DEFAULT 10,
                auto_contact_seller BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES found_items (id)
            )
        ''')
        
        # Price history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER,
                price REAL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES found_items (id)
            )
        ''')
        
        # Acquisition recommendations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS acquisition_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_id INTEGER,
                recommendation_type TEXT,
                title TEXT,
                description TEXT,
                reasoning TEXT,
                estimated_cost REAL,
                time_to_acquire_days INTEGER,
                difficulty_level INTEGER,
                diy_alternative TEXT,
                purchase_alternative TEXT,
                hybrid_solution TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (query_id) REFERENCES search_queries (id)
            )
        ''')
        
        # Furniture categories and specifications
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS furniture_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_name TEXT NOT NULL,
                subcategory TEXT,
                typical_dimensions TEXT,
                material_options TEXT,
                price_range_low REAL,
                price_range_high REAL,
                common_brands TEXT,
                search_keywords TEXT,
                refurbishment_difficulty INTEGER,
                diy_feasibility INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Populate with furniture categories
        self._populate_furniture_categories()
    
    def _populate_furniture_categories(self):
        """Populate database with common furniture categories and specifications"""
        categories = [
            {
                "category_name": "Seating",
                "subcategory": "Armchair",
                "typical_dimensions": "W:80-100cm, D:80-100cm, H:80-110cm",
                "material_options": "Fabric,Leather,Velvet,Linen",
                "price_range_low": 50.0,
                "price_range_high": 800.0,
                "common_brands": "IKEA,John Lewis,DFS,Next,Habitat",
                "search_keywords": "armchair,accent chair,lounge chair,reading chair",
                "refurbishment_difficulty": 3,
                "diy_feasibility": 2
            },
            {
                "category_name": "Seating",
                "subcategory": "Sofa",
                "typical_dimensions": "W:180-250cm, D:80-100cm, H:80-90cm",
                "material_options": "Fabric,Leather,Microfiber,Velvet",
                "price_range_low": 200.0,
                "price_range_high": 2000.0,
                "common_brands": "IKEA,DFS,Sofology,John Lewis,Next",
                "search_keywords": "sofa,couch,settee,3 seater,2 seater",
                "refurbishment_difficulty": 4,
                "diy_feasibility": 1
            },
            {
                "category_name": "Tables",
                "subcategory": "Dining Table",
                "typical_dimensions": "W:120-200cm, D:80-100cm, H:75cm",
                "material_options": "Oak,Pine,Walnut,Glass,Metal",
                "price_range_low": 80.0,
                "price_range_high": 1200.0,
                "common_brands": "IKEA,John Lewis,Habitat,West Elm,Made",
                "search_keywords": "dining table,kitchen table,extending table",
                "refurbishment_difficulty": 2,
                "diy_feasibility": 4
            },
            {
                "category_name": "Tables",
                "subcategory": "Coffee Table",
                "typical_dimensions": "W:100-140cm, D:50-70cm, H:40-50cm",
                "material_options": "Wood,Glass,Metal,Marble,Acrylic",
                "price_range_low": 30.0,
                "price_range_high": 500.0,
                "common_brands": "IKEA,Habitat,John Lewis,Next,Argos",
                "search_keywords": "coffee table,centre table,living room table",
                "refurbishment_difficulty": 2,
                "diy_feasibility": 5
            },
            {
                "category_name": "Storage",
                "subcategory": "Bookshelf",
                "typical_dimensions": "W:60-120cm, D:25-40cm, H:150-200cm",
                "material_options": "Pine,Oak,MDF,Metal,Bamboo",
                "price_range_low": 25.0,
                "price_range_high": 400.0,
                "common_brands": "IKEA,Argos,John Lewis,Habitat",
                "search_keywords": "bookshelf,bookcase,shelving unit,display unit",
                "refurbishment_difficulty": 1,
                "diy_feasibility": 5
            },
            {
                "category_name": "Storage",
                "subcategory": "Wardrobe",
                "typical_dimensions": "W:100-250cm, D:50-60cm, H:180-220cm",
                "material_options": "Pine,Oak,MDF,Melamine",
                "price_range_low": 100.0,
                "price_range_high": 1000.0,
                "common_brands": "IKEA,Argos,John Lewis,Dreams",
                "search_keywords": "wardrobe,closet,armoire,fitted wardrobe",
                "refurbishment_difficulty": 3,
                "diy_feasibility": 3
            },
            {
                "category_name": "Bedroom",
                "subcategory": "Bed Frame",
                "typical_dimensions": "W:140-200cm, D:200cm, H:100-120cm",
                "material_options": "Wood,Metal,Upholstered,Rattan",
                "price_range_low": 80.0,
                "price_range_high": 800.0,
                "common_brands": "IKEA,Dreams,John Lewis,Next,Habitat",
                "search_keywords": "bed frame,double bed,king size bed,single bed",
                "refurbishment_difficulty": 2,
                "diy_feasibility": 4
            },
            {
                "category_name": "Bedroom",
                "subcategory": "Chest of Drawers",
                "typical_dimensions": "W:80-120cm, D:40-50cm, H:80-120cm",
                "material_options": "Pine,Oak,MDF,Painted",
                "price_range_low": 50.0,
                "price_range_high": 400.0,
                "common_brands": "IKEA,Argos,John Lewis,Next",
                "search_keywords": "chest of drawers,drawers,bedroom storage",
                "refurbishment_difficulty": 2,
                "diy_feasibility": 4
            }
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for category in categories:
            cursor.execute('''
                INSERT OR IGNORE INTO furniture_categories 
                (category_name, subcategory, typical_dimensions, material_options,
                 price_range_low, price_range_high, common_brands, search_keywords,
                 refurbishment_difficulty, diy_feasibility)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                category["category_name"], category["subcategory"], category["typical_dimensions"],
                category["material_options"], category["price_range_low"], category["price_range_high"],
                category["common_brands"], category["search_keywords"],
                category["refurbishment_difficulty"], category["diy_feasibility"]
            ))
        
        conn.commit()
        conn.close()
    
    def create_search_query(self, query_text: str, category: str = None, 
                          max_price: float = None, min_price: float = None,
                          condition_preference: str = "any",
                          size_requirements: str = None,
                          style_preferences: str = None,
                          urgency_level: int = 3) -> int:
        """Create a new furniture search query"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO search_queries 
            (query_text, category, max_price, min_price, condition_preference,
             size_requirements, style_preferences, urgency_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            query_text, category, max_price, min_price, condition_preference,
            size_requirements, style_preferences, urgency_level
        ))
        
        query_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return query_id
    
    def search_all_platforms(self, query_id: int) -> Dict:
        """Search all available platforms for furniture matching the query"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM search_queries WHERE id = ?', (query_id,))
        query = cursor.fetchone()
        
        if not query:
            conn.close()
            return {"error": "Query not found"}
        
        query_text = query[1]
        max_price = query[3]
        min_price = query[4]
        
        results = {
            "query_id": query_id,
            "query_text": query_text,
            "platforms_searched": [],
            "total_items_found": 0,
            "items_by_platform": {},
            "best_deals": [],
            "free_items": [],
            "refurbishment_opportunities": []
        }
        
        # Search each platform
        for platform_name, platform_config in self.search_platforms.items():
            try:
                platform_results = self._search_platform(
                    platform_name, platform_config, query_text, max_price, min_price
                )
                
                results["platforms_searched"].append(platform_name)
                results["items_by_platform"][platform_name] = platform_results
                results["total_items_found"] += len(platform_results)
                
                # Store results in database
                for item in platform_results:
                    self._store_found_item(query_id, platform_name, item)
                
            except Exception as e:
                print(f"Error searching {platform_name}: {str(e)}")
                continue
        
        # Update last searched timestamp
        cursor.execute(
            'UPDATE search_queries SET last_searched = ? WHERE id = ?',
            (datetime.now(), query_id)
        )
        conn.commit()
        conn.close()
        
        # Analyze results
        results["best_deals"] = self._find_best_deals(query_id)
        results["free_items"] = self._find_free_items(query_id)
        results["refurbishment_opportunities"] = self._find_refurbishment_opportunities(query_id)
        
        return results
    
    def _search_platform(self, platform_name: str, platform_config: Dict, 
                        query_text: str, max_price: float = None, 
                        min_price: float = None) -> List[Dict]:
        """Search a specific platform for items"""
        # This is a simplified mock implementation
        # In a real implementation, this would use web scraping or APIs
        
        mock_results = []
        
        if platform_name == "gumtree":
            mock_results = [
                {
                    "title": f"Vintage {query_text} - Good Condition",
                    "price": 85.0,
                    "condition": "Used - Good",
                    "location": "East London",
                    "seller_name": "FurnitureLover123",
                    "description": f"Beautiful {query_text} in good condition. Some minor wear but structurally sound.",
                    "url": f"https://gumtree.com/item/{hashlib.md5(query_text.encode()).hexdigest()[:8]}",
                    "images": ["image1.jpg", "image2.jpg"],
                    "negotiable": True,
                    "delivery_available": False
                },
                {
                    "title": f"Modern {query_text} - Excellent Condition",
                    "price": 150.0,
                    "condition": "Used - Excellent",
                    "location": "South London",
                    "seller_name": "HomeDesigner",
                    "description": f"Barely used {query_text}. Moving house, must sell quickly.",
                    "url": f"https://gumtree.com/item/{hashlib.md5((query_text+'2').encode()).hexdigest()[:8]}",
                    "images": ["image3.jpg"],
                    "negotiable": True,
                    "delivery_available": True,
                    "delivery_cost": 25.0
                }
            ]
        
        elif platform_name == "freecycle":
            mock_results = [
                {
                    "title": f"FREE {query_text} - Collection Only",
                    "price": 0.0,
                    "condition": "Used - Fair",
                    "location": "North London",
                    "seller_name": "EcoWarrior",
                    "description": f"Free {query_text}. Needs some TLC but good bones. Collection only.",
                    "url": f"https://freecycle.org/item/{hashlib.md5((query_text+'free').encode()).hexdigest()[:8]}",
                    "images": [],
                    "negotiable": False,
                    "delivery_available": False,
                    "pickup_only": True
                }
            ]
        
        elif platform_name == "ebay_uk":
            mock_results = [
                {
                    "title": f"Refurbished {query_text} - Like New",
                    "price": 120.0,
                    "condition": "Refurbished",
                    "location": "London",
                    "seller_name": "FurnitureRestorer",
                    "seller_rating": 4.8,
                    "description": f"Professionally refurbished {query_text}. 30-day return guarantee.",
                    "url": f"https://ebay.co.uk/item/{hashlib.md5((query_text+'ebay').encode()).hexdigest()[:8]}",
                    "images": ["ebay1.jpg", "ebay2.jpg", "ebay3.jpg"],
                    "negotiable": False,
                    "delivery_available": True,
                    "delivery_cost": 15.0
                }
            ]
        
        # Filter by price if specified
        if max_price:
            mock_results = [item for item in mock_results if item["price"] <= max_price]
        if min_price:
            mock_results = [item for item in mock_results if item["price"] >= min_price]
        
        return mock_results
    
    def _store_found_item(self, query_id: int, platform: str, item: Dict):
        """Store a found item in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate match score based on various factors
        match_score = self._calculate_match_score(query_id, item)
        
        # Estimate refurbishment potential and cost
        refurb_potential, refurb_cost = self._estimate_refurbishment(item)
        
        total_cost = item["price"] + item.get("delivery_cost", 0) + refurb_cost
        
        cursor.execute('''
            INSERT INTO found_items 
            (query_id, platform, title, description, price, condition_item, location,
             seller_name, seller_rating, item_url, image_urls, delivery_available,
             delivery_cost, pickup_only, negotiable, match_score, refurbishment_potential,
             estimated_refurb_cost, total_estimated_cost)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            query_id, platform, item["title"], item.get("description", ""),
            item["price"], item.get("condition", "Unknown"), item.get("location", ""),
            item.get("seller_name", ""), item.get("seller_rating", 0),
            item.get("url", ""), json.dumps(item.get("images", [])),
            item.get("delivery_available", False), item.get("delivery_cost", 0),
            item.get("pickup_only", False), item.get("negotiable", False),
            match_score, refurb_potential, refurb_cost, total_cost
        ))
        
        conn.commit()
        conn.close()
    
    def _calculate_match_score(self, query_id: int, item: Dict) -> float:
        """Calculate how well an item matches the search criteria"""
        score = 0.0
        
        # Base score for finding the item
        score += 50.0
        
        # Condition scoring
        condition = item.get("condition", "").lower()
        if "excellent" in condition or "like new" in condition:
            score += 30.0
        elif "good" in condition:
            score += 20.0
        elif "fair" in condition:
            score += 10.0
        
        # Price scoring (lower is better, but not free unless specifically wanted)
        price = item.get("price", 0)
        if price == 0:
            score += 15.0  # Free items get bonus
        elif price < 50:
            score += 25.0
        elif price < 100:
            score += 20.0
        elif price < 200:
            score += 15.0
        
        # Delivery availability
        if item.get("delivery_available", False):
            score += 10.0
        
        # Seller rating
        rating = item.get("seller_rating", 0)
        if rating > 4.5:
            score += 10.0
        elif rating > 4.0:
            score += 5.0
        
        # Negotiable price
        if item.get("negotiable", False):
            score += 5.0
        
        return min(score, 100.0)  # Cap at 100
    
    def _estimate_refurbishment(self, item: Dict) -> Tuple[str, float]:
        """Estimate refurbishment potential and cost"""
        condition = item.get("condition", "").lower()
        price = item.get("price", 0)
        
        if "excellent" in condition or "like new" in condition:
            return "Minimal - just cleaning", 5.0
        elif "good" in condition:
            return "Light refurbishment - sanding, painting", 25.0
        elif "fair" in condition:
            return "Moderate refurbishment - repair, refinish", 50.0
        elif price == 0:  # Free items often need more work
            return "Significant refurbishment - structural repair", 75.0
        else:
            return "Assessment needed", 30.0
    
    def _find_best_deals(self, query_id: int) -> List[Dict]:
        """Find the best deals from search results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM found_items 
            WHERE query_id = ? 
            ORDER BY match_score DESC, total_estimated_cost ASC
            LIMIT 5
        ''', (query_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        deals = []
        for result in results:
            deals.append({
                "id": result[0],
                "platform": result[2],
                "title": result[3],
                "price": result[5],
                "total_cost": result[20],
                "match_score": result[17],
                "condition": result[7],
                "location": result[8],
                "refurbishment_potential": result[18],
                "url": result[11]
            })
        
        return deals
    
    def _find_free_items(self, query_id: int) -> List[Dict]:
        """Find free items from search results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM found_items 
            WHERE query_id = ? AND price = 0
            ORDER BY match_score DESC
        ''', (query_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        free_items = []
        for result in results:
            free_items.append({
                "id": result[0],
                "platform": result[2],
                "title": result[3],
                "condition": result[7],
                "location": result[8],
                "refurbishment_potential": result[18],
                "estimated_refurb_cost": result[19],
                "url": result[11]
            })
        
        return free_items
    
    def _find_refurbishment_opportunities(self, query_id: int) -> List[Dict]:
        """Find items with good refurbishment potential"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM found_items 
            WHERE query_id = ? AND estimated_refurb_cost < price * 0.5
            ORDER BY (price + estimated_refurb_cost) ASC
            LIMIT 5
        ''', (query_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        opportunities = []
        for result in results:
            potential_value = result[5] * 2  # Assume refurbished value is 2x current price
            total_investment = result[5] + result[19]  # Price + refurb cost
            profit_potential = potential_value - total_investment
            
            opportunities.append({
                "id": result[0],
                "platform": result[2],
                "title": result[3],
                "current_price": result[5],
                "refurb_cost": result[19],
                "total_investment": total_investment,
                "potential_value": potential_value,
                "profit_potential": profit_potential,
                "refurbishment_description": result[18],
                "url": result[11]
            })
        
        return opportunities
    
    def suggest_diy_alternatives(self, query_text: str, max_budget: float) -> List[Dict]:
        """Suggest DIY alternatives for furniture items"""
        # Get furniture category info
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM furniture_categories 
            WHERE search_keywords LIKE ? OR category_name LIKE ?
            ORDER BY diy_feasibility DESC
        ''', (f'%{query_text}%', f'%{query_text}%'))
        
        categories = cursor.fetchall()
        conn.close()
        
        suggestions = []
        
        for category in categories:
            if category[9] >= 3:  # diy_feasibility >= 3
                material_cost = min(max_budget * 0.6, category[5] * 0.4)  # 60% of budget or 40% of retail price
                
                suggestions.append({
                    "item_type": category[2],  # subcategory
                    "diy_feasibility": category[9],
                    "estimated_material_cost": material_cost,
                    "estimated_time_hours": category[8] * 4,  # refurbishment_difficulty * 4 hours
                    "materials_needed": self._get_diy_materials(category[2]),
                    "tools_required": self._get_required_tools(category[2]),
                    "skill_level": "Beginner" if category[9] >= 4 else "Intermediate",
                    "instructions_available": True,
                    "cost_savings": category[5] - material_cost
                })
        
        return suggestions
    
    def _get_diy_materials(self, item_type: str) -> List[str]:
        """Get materials needed for DIY furniture project"""
        material_map = {
            "Coffee Table": ["Pine planks", "Wood screws", "Wood glue", "Sandpaper", "Wood stain", "Furniture legs"],
            "Bookshelf": ["Pine boards", "Wood screws", "L-brackets", "Sandpaper", "Wood finish"],
            "Chest of Drawers": ["Plywood", "Drawer slides", "Handles", "Wood screws", "Wood glue", "Paint"],
            "Bed Frame": ["Timber planks", "Metal brackets", "Bolts", "Sandpaper", "Wood stain"],
            "Dining Table": ["Hardwood planks", "Table legs", "Wood screws", "Wood glue", "Polyurethane finish"]
        }
        
        return material_map.get(item_type, ["Wood", "Screws", "Glue", "Finish"])
    
    def _get_required_tools(self, item_type: str) -> List[str]:
        """Get tools required for DIY furniture project"""
        basic_tools = ["Drill", "Screwdriver", "Measuring tape", "Pencil", "Sandpaper"]
        
        tool_map = {
            "Coffee Table": basic_tools + ["Saw", "Router (optional)"],
            "Bookshelf": basic_tools + ["Saw", "Level"],
            "Chest of Drawers": basic_tools + ["Saw", "Chisel", "Clamps"],
            "Bed Frame": basic_tools + ["Saw", "Socket wrench"],
            "Dining Table": basic_tools + ["Saw", "Router", "Clamps", "Orbital sander"]
        }
        
        return tool_map.get(item_type, basic_tools)
    
    def create_acquisition_plan(self, query_id: int, budget: float, 
                              timeline_days: int = 30) -> Dict:
        """Create a comprehensive acquisition plan"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get query details
        cursor.execute('SELECT * FROM search_queries WHERE id = ?', (query_id,))
        query = cursor.fetchone()
        
        if not query:
            conn.close()
            return {"error": "Query not found"}
        
        query_text = query[1]
        
        # Get all found items
        cursor.execute('''
            SELECT * FROM found_items 
            WHERE query_id = ? 
            ORDER BY match_score DESC, total_estimated_cost ASC
        ''', (query_id,))
        
        found_items = cursor.fetchall()
        conn.close()
        
        plan = {
            "query_text": query_text,
            "budget": budget,
            "timeline_days": timeline_days,
            "recommendations": []
        }
        
        # Option 1: Best ready-to-use item
        if found_items:
            best_item = found_items[0]
            if best_item[20] <= budget:  # total_estimated_cost
                plan["recommendations"].append({
                    "option": "Purchase Ready Item",
                    "item_title": best_item[3],
                    "platform": best_item[2],
                    "total_cost": best_item[20],
                    "timeline_days": 3,
                    "effort_level": "Low",
                    "pros": ["Immediate availability", "No DIY skills required"],
                    "cons": ["Higher cost", "Limited customization"],
                    "action_steps": [
                        "Contact seller",
                        "Arrange viewing/pickup",
                        "Complete purchase"
                    ]
                })
        
        # Option 2: Refurbishment opportunity
        refurb_items = [item for item in found_items if item[19] < item[5] * 0.5]  # refurb cost < 50% of price
        if refurb_items:
            best_refurb = refurb_items[0]
            total_cost = best_refurb[5] + best_refurb[19]  # price + refurb cost
            if total_cost <= budget:
                plan["recommendations"].append({
                    "option": "Refurbishment Project",
                    "item_title": best_refurb[3],
                    "platform": best_refurb[2],
                    "purchase_cost": best_refurb[5],
                    "refurbishment_cost": best_refurb[19],
                    "total_cost": total_cost,
                    "timeline_days": 14,
                    "effort_level": "Medium",
                    "pros": ["Cost effective", "Customizable", "Satisfying project"],
                    "cons": ["Requires skills", "Time investment"],
                    "refurbishment_plan": best_refurb[18],
                    "action_steps": [
                        "Purchase item",
                        "Assess condition",
                        "Source refurbishment materials",
                        "Complete refurbishment"
                    ]
                })
        
        # Option 3: DIY from scratch
        diy_suggestions = self.suggest_diy_alternatives(query_text, budget)
        if diy_suggestions:
            best_diy = diy_suggestions[0]
            if best_diy["estimated_material_cost"] <= budget:
                plan["recommendations"].append({
                    "option": "DIY from Scratch",
                    "item_type": best_diy["item_type"],
                    "material_cost": best_diy["estimated_material_cost"],
                    "total_cost": best_diy["estimated_material_cost"],
                    "timeline_days": max(7, best_diy["estimated_time_hours"] // 2),
                    "effort_level": "High",
                    "skill_level": best_diy["skill_level"],
                    "pros": ["Lowest cost", "Full customization", "Learning experience"],
                    "cons": ["Requires tools", "Time intensive", "Skill dependent"],
                    "materials_needed": best_diy["materials_needed"],
                    "tools_required": best_diy["tools_required"],
                    "action_steps": [
                        "Source materials",
                        "Prepare workspace",
                        "Follow build instructions",
                        "Apply finish"
                    ]
                })
        
        # Option 4: Hybrid approach
        free_items = [item for item in found_items if item[5] == 0]  # price == 0
        if free_items and budget > 50:
            best_free = free_items[0]
            plan["recommendations"].append({
                "option": "Hybrid: Free Item + Professional Refurbishment",
                "item_title": best_free[3],
                "platform": best_free[2],
                "item_cost": 0,
                "professional_refurb_cost": min(budget * 0.8, 150),
                "total_cost": min(budget * 0.8, 150),
                "timeline_days": 10,
                "effort_level": "Low",
                "pros": ["Professional quality", "Moderate cost", "Minimal effort"],
                "cons": ["Dependent on professionals", "Less control"],
                "action_steps": [
                    "Collect free item",
                    "Get refurbishment quotes",
                    "Commission work",
                    "Collect finished item"
                ]
            })
        
        # Sort recommendations by cost-effectiveness
        plan["recommendations"].sort(key=lambda x: x.get("total_cost", float('inf')))
        
        return plan
    
    def monitor_price_changes(self, item_id: int) -> Dict:
        """Monitor price changes for a specific item"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current item details
        cursor.execute('SELECT * FROM found_items WHERE id = ?', (item_id,))
        item = cursor.fetchone()
        
        if not item:
            conn.close()
            return {"error": "Item not found"}
        
        # Get price history
        cursor.execute('''
            SELECT price, recorded_at FROM price_history 
            WHERE item_id = ? 
            ORDER BY recorded_at DESC
        ''', (item_id,))
        
        price_history = cursor.fetchall()
        conn.close()
        
        current_price = item[5]
        
        analysis = {
            "item_id": item_id,
            "item_title": item[3],
            "current_price": current_price,
            "price_history": [{"price": p[0], "date": p[1]} for p in price_history],
            "price_trend": "stable"
        }
        
        if len(price_history) > 1:
            recent_price = price_history[0][0]
            older_price = price_history[-1][0]
            
            if recent_price < older_price * 0.9:
                analysis["price_trend"] = "decreasing"
                analysis["savings_opportunity"] = True
            elif recent_price > older_price * 1.1:
                analysis["price_trend"] = "increasing"
                analysis["urgency"] = "high"
        
        return analysis
    
    def get_acquisition_summary(self, days: int = 7) -> Dict:
        """Get summary of recent acquisition activities"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since_date = datetime.now() - timedelta(days=days)
        
        # Get recent searches
        cursor.execute('''
            SELECT COUNT(*) FROM search_queries 
            WHERE created_at > ?
        ''', (since_date,))
        recent_searches = cursor.fetchone()[0]
        
        # Get items found
        cursor.execute('''
            SELECT COUNT(*) FROM found_items 
            WHERE found_at > ?
        ''', (since_date,))
        items_found = cursor.fetchone()[0]
        
        # Get average prices
        cursor.execute('''
            SELECT AVG(price), MIN(price), MAX(price) FROM found_items 
            WHERE found_at > ? AND price > 0
        ''', (since_date,))
        price_stats = cursor.fetchone()
        
        # Get best deals
        cursor.execute('''
            SELECT title, price, platform, match_score FROM found_items 
            WHERE found_at > ? 
            ORDER BY match_score DESC, price ASC 
            LIMIT 5
        ''', (since_date,))
        best_deals = cursor.fetchall()
        
        conn.close()
        
        return {
            "period_days": days,
            "searches_conducted": recent_searches,
            "items_found": items_found,
            "price_statistics": {
                "average": round(price_stats[0], 2) if price_stats[0] else 0,
                "minimum": price_stats[1] if price_stats[1] else 0,
                "maximum": price_stats[2] if price_stats[2] else 0
            },
            "best_deals": [
                {
                    "title": deal[0],
                    "price": deal[1],
                    "platform": deal[2],
                    "match_score": deal[3]
                } for deal in best_deals
            ],
            "platforms_active": len(self.search_platforms)
        }

