"""
Advanced 3D Printing & Fabrication Integration System
Enables the TechCraft Genius AI to design, optimize, and manage 3D printing projects
for furniture, household items, and custom solutions.
"""

import json
import os
import sqlite3
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import subprocess
import tempfile
import math

class PrintingFabricationManager:
    def __init__(self, db_path: str = "printing_fabrication.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize the printing and fabrication database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 3D Printer profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS printer_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                brand TEXT,
                model TEXT,
                build_volume_x REAL,
                build_volume_y REAL,
                build_volume_z REAL,
                nozzle_diameter REAL,
                layer_height_min REAL,
                layer_height_max REAL,
                supported_materials TEXT,
                connection_type TEXT,
                ip_address TEXT,
                api_key TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Print projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS print_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                stl_file_path TEXT,
                gcode_file_path TEXT,
                printer_id INTEGER,
                material_type TEXT,
                estimated_print_time INTEGER,
                estimated_material_cost REAL,
                estimated_filament_weight REAL,
                infill_percentage INTEGER,
                layer_height REAL,
                print_speed INTEGER,
                status TEXT DEFAULT 'designed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (printer_id) REFERENCES printer_profiles (id)
            )
        ''')
        
        # Material inventory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS material_inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                material_type TEXT NOT NULL,
                brand TEXT,
                color TEXT,
                diameter REAL,
                weight_remaining REAL,
                cost_per_kg REAL,
                supplier TEXT,
                purchase_date DATE,
                expiry_date DATE,
                storage_location TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Design templates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS design_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                description TEXT,
                parameters TEXT,
                openscad_code TEXT,
                thumbnail_path TEXT,
                difficulty_level INTEGER,
                estimated_print_time INTEGER,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Print queue table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS print_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                printer_id INTEGER,
                priority INTEGER DEFAULT 5,
                scheduled_start TIMESTAMP,
                status TEXT DEFAULT 'queued',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES print_projects (id),
                FOREIGN KEY (printer_id) REFERENCES printer_profiles (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Initialize with some default templates
        self._populate_default_templates()
    
    def _populate_default_templates(self):
        """Populate database with default furniture and household item templates"""
        default_templates = [
            {
                "name": "Modular Shelf Bracket",
                "category": "furniture",
                "description": "Customizable shelf bracket for modular shelving systems",
                "parameters": json.dumps({
                    "width": {"min": 50, "max": 300, "default": 150, "unit": "mm"},
                    "depth": {"min": 30, "max": 200, "default": 100, "unit": "mm"},
                    "thickness": {"min": 5, "max": 20, "default": 10, "unit": "mm"},
                    "screw_holes": {"min": 2, "max": 8, "default": 4}
                }),
                "openscad_code": """
// Modular Shelf Bracket
module shelf_bracket(width=150, depth=100, thickness=10, screw_holes=4) {
    difference() {
        union() {
            // Main bracket
            cube([width, thickness, depth]);
            // Support triangle
            linear_extrude(height=thickness)
                polygon([[0,0], [width*0.7,0], [0,depth*0.7]]);
        }
        // Screw holes
        for(i=[0:screw_holes-1]) {
            translate([width/(screw_holes+1)*(i+1), thickness/2, depth-15])
                cylinder(h=thickness*2, d=5, center=true);
        }
    }
}
shelf_bracket();
                """,
                "difficulty_level": 2,
                "estimated_print_time": 45,
                "tags": "furniture,bracket,modular,shelf"
            },
            {
                "name": "Cable Management Box",
                "category": "organization",
                "description": "Customizable cable management solution for desks",
                "parameters": json.dumps({
                    "length": {"min": 100, "max": 400, "default": 200, "unit": "mm"},
                    "width": {"min": 50, "max": 150, "default": 80, "unit": "mm"},
                    "height": {"min": 30, "max": 100, "default": 50, "unit": "mm"},
                    "cable_slots": {"min": 2, "max": 10, "default": 4}
                }),
                "openscad_code": """
// Cable Management Box
module cable_box(length=200, width=80, height=50, cable_slots=4) {
    wall_thickness = 2;
    difference() {
        // Outer box
        cube([length, width, height]);
        // Inner cavity
        translate([wall_thickness, wall_thickness, wall_thickness])
            cube([length-2*wall_thickness, width-2*wall_thickness, height]);
        // Cable slots
        for(i=[0:cable_slots-1]) {
            translate([length/(cable_slots+1)*(i+1), 0, height*0.7])
                rotate([-90,0,0])
                    cylinder(h=wall_thickness*2, d=10);
        }
    }
}
cable_box();
                """,
                "difficulty_level": 1,
                "estimated_print_time": 90,
                "tags": "organization,cable,management,desk"
            },
            {
                "name": "Plant Pot with Drainage",
                "category": "garden",
                "description": "Self-watering plant pot with integrated drainage system",
                "parameters": json.dumps({
                    "diameter": {"min": 80, "max": 300, "default": 150, "unit": "mm"},
                    "height": {"min": 60, "max": 250, "default": 120, "unit": "mm"},
                    "drainage_holes": {"min": 3, "max": 12, "default": 6},
                    "water_reservoir": {"type": "boolean", "default": True}
                }),
                "openscad_code": """
// Plant Pot with Drainage
module plant_pot(diameter=150, height=120, drainage_holes=6, water_reservoir=true) {
    wall_thickness = 3;
    reservoir_height = water_reservoir ? height*0.2 : 0;
    
    difference() {
        // Outer pot
        cylinder(h=height, d=diameter);
        // Inner cavity
        translate([0,0,wall_thickness])
            cylinder(h=height, d=diameter-2*wall_thickness);
        // Drainage holes
        if(water_reservoir) {
            for(i=[0:drainage_holes-1]) {
                rotate([0,0,360/drainage_holes*i])
                    translate([diameter/4,0,reservoir_height+wall_thickness])
                        cylinder(h=wall_thickness*2, d=5);
            }
        } else {
            for(i=[0:drainage_holes-1]) {
                rotate([0,0,360/drainage_holes*i])
                    translate([diameter/4,0,0])
                        cylinder(h=wall_thickness*2, d=5);
            }
        }
    }
    
    // Water reservoir separator
    if(water_reservoir) {
        translate([0,0,reservoir_height])
            difference() {
                cylinder(h=wall_thickness, d=diameter-2*wall_thickness);
                for(i=[0:drainage_holes-1]) {
                    rotate([0,0,360/drainage_holes*i])
                        translate([diameter/4,0,0])
                            cylinder(h=wall_thickness*2, d=5, center=true);
                }
            }
    }
}
plant_pot();
                """,
                "difficulty_level": 2,
                "estimated_print_time": 180,
                "tags": "garden,plant,pot,drainage,self-watering"
            },
            {
                "name": "Modular Storage Drawer",
                "category": "furniture",
                "description": "Stackable drawer system for custom storage solutions",
                "parameters": json.dumps({
                    "width": {"min": 100, "max": 400, "default": 200, "unit": "mm"},
                    "depth": {"min": 100, "max": 400, "default": 150, "unit": "mm"},
                    "height": {"min": 50, "max": 200, "default": 80, "unit": "mm"},
                    "handle_style": {"options": ["cutout", "knob", "rail"], "default": "cutout"}
                }),
                "openscad_code": """
// Modular Storage Drawer
module storage_drawer(width=200, depth=150, height=80, handle_style="cutout") {
    wall_thickness = 2;
    
    difference() {
        // Main drawer body
        cube([width, depth, height]);
        // Inner cavity
        translate([wall_thickness, wall_thickness, wall_thickness])
            cube([width-2*wall_thickness, depth-2*wall_thickness, height]);
        
        // Handle
        if(handle_style == "cutout") {
            translate([width/2, 0, height*0.6])
                rotate([-90,0,0])
                    hull() {
                        cylinder(h=wall_thickness*2, d=15);
                        translate([30,0,0])
                            cylinder(h=wall_thickness*2, d=15);
                    }
        }
    }
    
    // Handle knob
    if(handle_style == "knob") {
        translate([width/2, -5, height*0.6])
            rotate([-90,0,0])
                cylinder(h=8, d=20);
    }
    
    // Handle rail
    if(handle_style == "rail") {
        translate([width*0.2, -3, height*0.6])
            cube([width*0.6, 6, 8]);
    }
}
storage_drawer();
                """,
                "difficulty_level": 3,
                "estimated_print_time": 240,
                "tags": "furniture,storage,drawer,modular,stackable"
            }
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for template in default_templates:
            cursor.execute('''
                INSERT OR IGNORE INTO design_templates 
                (name, category, description, parameters, openscad_code, difficulty_level, estimated_print_time, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                template["name"], template["category"], template["description"],
                template["parameters"], template["openscad_code"],
                template["difficulty_level"], template["estimated_print_time"], template["tags"]
            ))
        
        conn.commit()
        conn.close()
    
    def add_printer_profile(self, name: str, brand: str, model: str, 
                          build_volume: Tuple[float, float, float],
                          nozzle_diameter: float = 0.4,
                          layer_height_range: Tuple[float, float] = (0.1, 0.3),
                          supported_materials: List[str] = None,
                          connection_type: str = "USB",
                          ip_address: str = None,
                          api_key: str = None) -> int:
        """Add a new 3D printer profile"""
        if supported_materials is None:
            supported_materials = ["PLA", "PETG", "ABS"]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO printer_profiles 
            (name, brand, model, build_volume_x, build_volume_y, build_volume_z,
             nozzle_diameter, layer_height_min, layer_height_max, supported_materials,
             connection_type, ip_address, api_key)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            name, brand, model, build_volume[0], build_volume[1], build_volume[2],
            nozzle_diameter, layer_height_range[0], layer_height_range[1],
            json.dumps(supported_materials), connection_type, ip_address, api_key
        ))
        
        printer_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return printer_id
    
    def generate_custom_design(self, template_name: str, parameters: Dict) -> Dict:
        """Generate a custom design based on template and parameters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM design_templates WHERE name = ?', (template_name,))
        template = cursor.fetchone()
        conn.close()
        
        if not template:
            return {"error": "Template not found"}
        
        # Parse template parameters
        template_params = json.loads(template[3])  # parameters column
        openscad_code = template[4]  # openscad_code column
        
        # Validate and apply parameters
        validated_params = {}
        for param_name, param_config in template_params.items():
            if param_name in parameters:
                value = parameters[param_name]
                
                # Validate ranges
                if "min" in param_config and value < param_config["min"]:
                    value = param_config["min"]
                elif "max" in param_config and value > param_config["max"]:
                    value = param_config["max"]
                
                validated_params[param_name] = value
            else:
                validated_params[param_name] = param_config.get("default", 100)
        
        # Generate OpenSCAD file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        design_name = f"{template_name.replace(' ', '_')}_{timestamp}"
        
        # Create design directory
        design_dir = f"/tmp/designs/{design_name}"
        os.makedirs(design_dir, exist_ok=True)
        
        # Write OpenSCAD file with parameters
        scad_file = f"{design_dir}/{design_name}.scad"
        with open(scad_file, 'w') as f:
            # Write parameters
            for param_name, value in validated_params.items():
                f.write(f"{param_name} = {value};\n")
            f.write("\n")
            f.write(openscad_code)
        
        # Generate STL file using OpenSCAD (if available)
        stl_file = f"{design_dir}/{design_name}.stl"
        try:
            subprocess.run([
                "openscad", "-o", stl_file, scad_file
            ], check=True, capture_output=True)
            stl_generated = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            stl_generated = False
            stl_file = None
        
        # Calculate estimated print time and material usage
        estimated_time, estimated_weight, estimated_cost = self._estimate_print_metrics(
            validated_params, template[6]  # base estimated_print_time
        )
        
        return {
            "design_name": design_name,
            "template_name": template_name,
            "parameters": validated_params,
            "scad_file": scad_file,
            "stl_file": stl_file if stl_generated else None,
            "estimated_print_time": estimated_time,
            "estimated_weight": estimated_weight,
            "estimated_cost": estimated_cost,
            "stl_generated": stl_generated
        }
    
    def _estimate_print_metrics(self, parameters: Dict, base_time: int) -> Tuple[int, float, float]:
        """Estimate print time, material weight, and cost based on parameters"""
        # Simple estimation based on volume scaling
        volume_factor = 1.0
        
        # Calculate volume factor from common parameters
        if "width" in parameters and "height" in parameters and "depth" in parameters:
            volume = parameters["width"] * parameters["height"] * parameters["depth"]
            # Normalize to base volume (150mm x 100mm x 50mm = 750,000 mm³)
            base_volume = 750000
            volume_factor = volume / base_volume
        elif "diameter" in parameters and "height" in parameters:
            radius = parameters["diameter"] / 2
            volume = math.pi * radius * radius * parameters["height"]
            # Normalize to base volume (cylinder: 75mm radius, 100mm height)
            base_volume = math.pi * 75 * 75 * 100
            volume_factor = volume / base_volume
        
        # Estimate print time (minutes)
        estimated_time = int(base_time * volume_factor)
        
        # Estimate material weight (grams) - assuming 20% infill, 1.24g/cm³ PLA density
        estimated_weight = volume_factor * 50  # Base 50g for reference object
        
        # Estimate cost (£) - assuming £25/kg PLA filament
        estimated_cost = (estimated_weight / 1000) * 25
        
        return estimated_time, estimated_weight, estimated_cost
    
    def optimize_for_printer(self, design_params: Dict, printer_id: int) -> Dict:
        """Optimize design parameters for specific printer capabilities"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM printer_profiles WHERE id = ?', (printer_id,))
        printer = cursor.fetchone()
        conn.close()
        
        if not printer:
            return {"error": "Printer not found"}
        
        optimizations = []
        optimized_params = design_params.copy()
        
        # Check build volume constraints
        build_x, build_y, build_z = printer[4], printer[5], printer[6]
        
        if "width" in design_params and design_params["width"] > build_x:
            optimized_params["width"] = build_x - 10  # 10mm margin
            optimizations.append(f"Reduced width to fit printer build volume ({build_x}mm)")
        
        if "depth" in design_params and design_params["depth"] > build_y:
            optimized_params["depth"] = build_y - 10
            optimizations.append(f"Reduced depth to fit printer build volume ({build_y}mm)")
        
        if "height" in design_params and design_params["height"] > build_z:
            optimized_params["height"] = build_z - 10
            optimizations.append(f"Reduced height to fit printer build volume ({build_z}mm)")
        
        # Optimize layer height
        layer_min, layer_max = printer[8], printer[9]
        if "layer_height" not in optimized_params:
            # Choose optimal layer height based on object size
            if "height" in optimized_params:
                if optimized_params["height"] < 50:
                    optimized_params["layer_height"] = max(0.15, layer_min)
                else:
                    optimized_params["layer_height"] = min(0.25, layer_max)
            else:
                optimized_params["layer_height"] = 0.2
        
        # Suggest optimal infill
        if "infill_percentage" not in optimized_params:
            # Functional parts get higher infill
            if any(keyword in design_params.get("category", "").lower() 
                   for keyword in ["bracket", "structural", "mechanical"]):
                optimized_params["infill_percentage"] = 30
            else:
                optimized_params["infill_percentage"] = 15
        
        return {
            "optimized_parameters": optimized_params,
            "optimizations_applied": optimizations,
            "printer_name": printer[1],
            "recommended_material": json.loads(printer[10])[0] if printer[10] else "PLA"
        }
    
    def create_print_project(self, name: str, design_data: Dict, printer_id: int,
                           material_type: str = "PLA") -> int:
        """Create a new print project"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO print_projects 
            (name, description, category, stl_file_path, printer_id, material_type,
             estimated_print_time, estimated_material_cost, estimated_filament_weight,
             infill_percentage, layer_height, print_speed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            name,
            f"Custom {design_data.get('template_name', 'design')} project",
            design_data.get('template_name', 'custom'),
            design_data.get('stl_file'),
            printer_id,
            material_type,
            design_data.get('estimated_print_time', 60),
            design_data.get('estimated_cost', 1.0),
            design_data.get('estimated_weight', 20.0),
            design_data.get('parameters', {}).get('infill_percentage', 15),
            design_data.get('parameters', {}).get('layer_height', 0.2),
            60  # Default print speed mm/s
        ))
        
        project_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return project_id
    
    def add_to_print_queue(self, project_id: int, printer_id: int, 
                          priority: int = 5, scheduled_start: datetime = None) -> int:
        """Add project to print queue"""
        if scheduled_start is None:
            scheduled_start = datetime.now()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO print_queue (project_id, printer_id, priority, scheduled_start)
            VALUES (?, ?, ?, ?)
        ''', (project_id, printer_id, priority, scheduled_start))
        
        queue_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return queue_id
    
    def get_material_cost_estimate(self, material_type: str, weight_grams: float) -> float:
        """Get cost estimate for material usage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT AVG(cost_per_kg) FROM material_inventory 
            WHERE material_type = ? AND weight_remaining > 0
        ''', (material_type,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            cost_per_kg = result[0]
        else:
            # Default costs for common materials
            default_costs = {
                "PLA": 25.0,
                "PETG": 30.0,
                "ABS": 28.0,
                "TPU": 45.0,
                "WOOD": 35.0
            }
            cost_per_kg = default_costs.get(material_type, 30.0)
        
        return (weight_grams / 1000) * cost_per_kg
    
    def suggest_furniture_projects(self, room_type: str, budget: float, 
                                 available_materials: List[str] = None) -> List[Dict]:
        """Suggest furniture projects based on room type and budget"""
        if available_materials is None:
            available_materials = ["PLA", "PETG"]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get templates suitable for the room type
        cursor.execute('''
            SELECT * FROM design_templates 
            WHERE category = 'furniture' OR tags LIKE ?
            ORDER BY difficulty_level, estimated_print_time
        ''', (f'%{room_type}%',))
        
        templates = cursor.fetchall()
        conn.close()
        
        suggestions = []
        
        for template in templates:
            # Estimate cost for default parameters
            default_params = json.loads(template[3])
            default_values = {k: v.get("default", 100) for k, v in default_params.items()}
            
            _, weight, cost = self._estimate_print_metrics(default_values, template[6])
            
            if cost <= budget:
                suggestions.append({
                    "name": template[1],
                    "description": template[2],
                    "category": template[3],
                    "difficulty": template[6],
                    "estimated_time_hours": template[6] / 60,
                    "estimated_cost": round(cost, 2),
                    "estimated_weight": round(weight, 1),
                    "parameters": default_params,
                    "tags": template[8].split(',') if template[8] else []
                })
        
        return suggestions[:10]  # Return top 10 suggestions
    
    def get_print_status(self, project_id: int) -> Dict:
        """Get current status of a print project"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.*, pr.name as printer_name, q.status as queue_status
            FROM print_projects p
            LEFT JOIN printer_profiles pr ON p.printer_id = pr.id
            LEFT JOIN print_queue q ON p.id = q.project_id
            WHERE p.id = ?
        ''', (project_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return {"error": "Project not found"}
        
        return {
            "project_id": result[0],
            "name": result[1],
            "status": result[13],
            "printer_name": result[15],
            "estimated_time": result[7],
            "estimated_cost": result[8],
            "queue_status": result[16] if result[16] else "not_queued",
            "created_at": result[14],
            "started_at": result[15],
            "completed_at": result[16]
        }
    
    def get_all_templates(self) -> List[Dict]:
        """Get all available design templates"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM design_templates ORDER BY category, name')
        templates = cursor.fetchall()
        conn.close()
        
        result = []
        for template in templates:
            result.append({
                "id": template[0],
                "name": template[1],
                "category": template[2],
                "description": template[3],
                "parameters": json.loads(template[4]),
                "difficulty_level": template[6],
                "estimated_print_time": template[7],
                "tags": template[8].split(',') if template[8] else []
            })
        
        return result
    
    def search_cheap_filament(self, material_type: str, quantity_kg: float = 1.0) -> List[Dict]:
        """Search for cheap filament deals online"""
        # This would integrate with web scraping to find deals
        # For now, return mock data with realistic UK prices
        
        deals = [
            {
                "supplier": "Amazon UK",
                "brand": "SUNLU",
                "material": material_type,
                "price_per_kg": 22.99,
                "quantity_kg": 1.0,
                "color_options": ["Black", "White", "Red", "Blue", "Green"],
                "rating": 4.3,
                "delivery_days": 1,
                "url": f"https://amazon.co.uk/search?k={material_type}+filament"
            },
            {
                "supplier": "3D Filaprint",
                "brand": "3D Filaprint",
                "material": material_type,
                "price_per_kg": 19.99,
                "quantity_kg": 1.0,
                "color_options": ["Natural", "Black", "White", "Grey"],
                "rating": 4.5,
                "delivery_days": 2,
                "url": "https://3dfilaprint.com"
            },
            {
                "supplier": "Technology Outlet",
                "brand": "Tecbears",
                "material": material_type,
                "price_per_kg": 18.50,
                "quantity_kg": 1.0,
                "color_options": ["Black", "White", "Transparent"],
                "rating": 4.1,
                "delivery_days": 3,
                "url": "https://technologyoutlet.co.uk"
            }
        ]
        
        # Sort by price per kg
        deals.sort(key=lambda x: x["price_per_kg"])
        
        return deals

