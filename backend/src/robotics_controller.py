"""
Advanced Robotics Integration & DIY Robot Builder Assistant
Physical task automation and custom robot design system
"""

import json
import time
import logging
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
from collections import defaultdict
import requests

class RobotType(Enum):
    VACUUM = "vacuum"
    WINDOW_CLEANER = "window_cleaner"
    GARDEN_CARE = "garden_care"
    DELIVERY = "delivery"
    SECURITY = "security"
    CUSTOM = "custom"

class TaskType(Enum):
    CLEANING = "cleaning"
    MAINTENANCE = "maintenance"
    MONITORING = "monitoring"
    DELIVERY = "delivery"
    GARDENING = "gardening"
    SECURITY = "security"

class RobotStatus(Enum):
    IDLE = "idle"
    WORKING = "working"
    CHARGING = "charging"
    ERROR = "error"
    MAINTENANCE = "maintenance"

@dataclass
class Robot:
    id: str
    name: str
    robot_type: RobotType
    status: RobotStatus
    current_task: Optional[str]
    battery_level: float  # 0-100
    location: Dict[str, float]  # x, y coordinates
    capabilities: List[str]
    last_maintenance: datetime
    total_runtime_hours: float
    error_count: int
    efficiency_score: float  # 0-100
    cost_gbp: float
    manufacturer: str
    model: str
    firmware_version: str
    connectivity: str  # wifi, bluetooth, etc.

@dataclass
class RobotTask:
    id: str
    robot_id: str
    task_type: TaskType
    description: str
    priority: int  # 1-10
    scheduled_time: datetime
    estimated_duration: int  # minutes
    required_tools: List[str]
    target_location: Dict[str, float]
    completion_criteria: Dict[str, Any]
    status: str  # pending, in_progress, completed, failed
    actual_duration: Optional[int]
    success_rate: Optional[float]
    energy_consumed: Optional[float]
    created_date: datetime

@dataclass
class CustomRobotDesign:
    id: str
    name: str
    purpose: str
    target_tasks: List[str]
    required_components: List[Dict[str, Any]]
    estimated_cost: float
    difficulty_level: str  # beginner, intermediate, advanced
    build_time_hours: int
    required_tools: List[str]
    required_skills: List[str]
    design_files: List[str]  # 3D models, schematics
    assembly_instructions: List[Dict[str, str]]
    programming_requirements: Dict[str, Any]
    testing_procedures: List[str]
    maintenance_schedule: Dict[str, str]
    upgrade_potential: List[str]
    created_date: datetime

@dataclass
class RobotCoordination:
    id: str
    participating_robots: List[str]
    coordination_type: str  # sequential, parallel, collaborative
    task_distribution: Dict[str, List[str]]
    communication_protocol: str
    synchronization_points: List[Dict[str, Any]]
    efficiency_multiplier: float
    estimated_completion_time: int
    status: str

class RoboticsController:
    def __init__(self, db_path: str = "robotics_data.db"):
        self.db_path = db_path
        self.robots: Dict[str, Robot] = {}
        self.tasks: Dict[str, RobotTask] = {}
        self.custom_designs: Dict[str, CustomRobotDesign] = {}
        self.coordinations: Dict[str, RobotCoordination] = {}
        
        # Component database for robot building
        self.component_database = {}
        self.supplier_database = {}
        
        self.init_database()
        self.load_data()
        self.initialize_sample_robots()
        self.load_component_database()
        self.start_coordination_engine()
    
    def init_database(self):
        """Initialize SQLite database for robotics data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS robots (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                robot_type TEXT NOT NULL,
                status TEXT NOT NULL,
                current_task TEXT,
                battery_level REAL NOT NULL,
                location TEXT NOT NULL,
                capabilities TEXT NOT NULL,
                last_maintenance TIMESTAMP NOT NULL,
                total_runtime_hours REAL NOT NULL,
                error_count INTEGER NOT NULL,
                efficiency_score REAL NOT NULL,
                cost_gbp REAL NOT NULL,
                manufacturer TEXT NOT NULL,
                model TEXT NOT NULL,
                firmware_version TEXT NOT NULL,
                connectivity TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS robot_tasks (
                id TEXT PRIMARY KEY,
                robot_id TEXT NOT NULL,
                task_type TEXT NOT NULL,
                description TEXT NOT NULL,
                priority INTEGER NOT NULL,
                scheduled_time TIMESTAMP NOT NULL,
                estimated_duration INTEGER NOT NULL,
                required_tools TEXT NOT NULL,
                target_location TEXT NOT NULL,
                completion_criteria TEXT NOT NULL,
                status TEXT NOT NULL,
                actual_duration INTEGER,
                success_rate REAL,
                energy_consumed REAL,
                created_date TIMESTAMP NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_robot_designs (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                purpose TEXT NOT NULL,
                target_tasks TEXT NOT NULL,
                required_components TEXT NOT NULL,
                estimated_cost REAL NOT NULL,
                difficulty_level TEXT NOT NULL,
                build_time_hours INTEGER NOT NULL,
                required_tools TEXT NOT NULL,
                required_skills TEXT NOT NULL,
                design_files TEXT NOT NULL,
                assembly_instructions TEXT NOT NULL,
                programming_requirements TEXT NOT NULL,
                testing_procedures TEXT NOT NULL,
                maintenance_schedule TEXT NOT NULL,
                upgrade_potential TEXT NOT NULL,
                created_date TIMESTAMP NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS robot_coordinations (
                id TEXT PRIMARY KEY,
                participating_robots TEXT NOT NULL,
                coordination_type TEXT NOT NULL,
                task_distribution TEXT NOT NULL,
                communication_protocol TEXT NOT NULL,
                synchronization_points TEXT NOT NULL,
                efficiency_multiplier REAL NOT NULL,
                estimated_completion_time INTEGER NOT NULL,
                status TEXT NOT NULL,
                created_date TIMESTAMP NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS robot_performance_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                robot_id TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                task_id TEXT,
                performance_metrics TEXT NOT NULL,
                energy_usage REAL,
                error_details TEXT,
                maintenance_notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def initialize_sample_robots(self):
        """Initialize sample robots for demonstration"""
        sample_robots = [
            Robot(
                id="roomba_i7_001",
                name="Living Room Vacuum",
                robot_type=RobotType.VACUUM,
                status=RobotStatus.IDLE,
                current_task=None,
                battery_level=85.0,
                location={"x": 5.2, "y": 3.1, "floor": 0},
                capabilities=["vacuum", "mop", "mapping", "scheduling", "zone_cleaning"],
                last_maintenance=datetime.now() - timedelta(days=15),
                total_runtime_hours=245.5,
                error_count=2,
                efficiency_score=92.0,
                cost_gbp=599.0,
                manufacturer="iRobot",
                model="Roomba i7+",
                firmware_version="3.12.8",
                connectivity="wifi"
            ),
            Robot(
                id="winbot_x_001",
                name="Window Cleaning Robot",
                robot_type=RobotType.WINDOW_CLEANER,
                status=RobotStatus.CHARGING,
                current_task=None,
                battery_level=100.0,
                location={"x": 0.0, "y": 0.0, "floor": 1, "window": "living_room_south"},
                capabilities=["window_cleaning", "glass_detection", "edge_navigation", "safety_rope"],
                last_maintenance=datetime.now() - timedelta(days=30),
                total_runtime_hours=78.2,
                error_count=0,
                efficiency_score=88.0,
                cost_gbp=299.0,
                manufacturer="Ecovacs",
                model="Winbot X",
                firmware_version="1.4.2",
                connectivity="wifi"
            ),
            Robot(
                id="garden_bot_001",
                name="Garden Care Assistant",
                robot_type=RobotType.GARDEN_CARE,
                status=RobotStatus.IDLE,
                current_task=None,
                battery_level=67.0,
                location={"x": 12.5, "y": 8.3, "zone": "herb_garden"},
                capabilities=["watering", "soil_monitoring", "weed_detection", "harvesting", "weather_monitoring"],
                last_maintenance=datetime.now() - timedelta(days=7),
                total_runtime_hours=156.8,
                error_count=1,
                efficiency_score=85.0,
                cost_gbp=1299.0,
                manufacturer="FarmBot",
                model="Genesis v1.6",
                firmware_version="2.1.0",
                connectivity="wifi"
            )
        ]
        
        for robot in sample_robots:
            self.robots[robot.id] = robot
            self.save_robot(robot)
    
    def load_component_database(self):
        """Load component database for robot building"""
        self.component_database = {
            "microcontrollers": [
                {
                    "name": "Arduino Uno R3",
                    "price_gbp": 22.50,
                    "capabilities": ["digital_io", "analog_input", "pwm", "serial"],
                    "power_consumption": "20mA",
                    "programming": "Arduino IDE",
                    "difficulty": "beginner",
                    "suppliers": ["Arduino Store", "RS Components", "Farnell"]
                },
                {
                    "name": "Raspberry Pi 4 Model B",
                    "price_gbp": 75.00,
                    "capabilities": ["linux", "gpio", "camera", "wifi", "bluetooth", "usb"],
                    "power_consumption": "600mA",
                    "programming": "Python, C++",
                    "difficulty": "intermediate",
                    "suppliers": ["Raspberry Pi Foundation", "RS Components", "Pimoroni"]
                },
                {
                    "name": "ESP32 DevKit",
                    "price_gbp": 8.50,
                    "capabilities": ["wifi", "bluetooth", "dual_core", "low_power"],
                    "power_consumption": "80mA",
                    "programming": "Arduino IDE, MicroPython",
                    "difficulty": "intermediate",
                    "suppliers": ["Espressif", "Adafruit", "SparkFun"]
                }
            ],
            "sensors": [
                {
                    "name": "Ultrasonic Distance Sensor HC-SR04",
                    "price_gbp": 3.50,
                    "range": "2cm-400cm",
                    "accuracy": "3mm",
                    "use_cases": ["obstacle_detection", "distance_measurement"],
                    "difficulty": "beginner"
                },
                {
                    "name": "Camera Module v2",
                    "price_gbp": 25.00,
                    "resolution": "8MP",
                    "video": "1080p30",
                    "use_cases": ["computer_vision", "surveillance", "navigation"],
                    "difficulty": "intermediate"
                },
                {
                    "name": "IMU 9-DOF Sensor",
                    "price_gbp": 15.00,
                    "sensors": ["accelerometer", "gyroscope", "magnetometer"],
                    "use_cases": ["orientation", "motion_detection", "stabilization"],
                    "difficulty": "advanced"
                }
            ],
            "actuators": [
                {
                    "name": "Servo Motor SG90",
                    "price_gbp": 4.50,
                    "torque": "1.8kg/cm",
                    "rotation": "180 degrees",
                    "use_cases": ["arm_movement", "steering", "positioning"],
                    "difficulty": "beginner"
                },
                {
                    "name": "Stepper Motor NEMA 17",
                    "price_gbp": 18.00,
                    "torque": "4.4kg/cm",
                    "precision": "1.8 degrees/step",
                    "use_cases": ["precise_positioning", "3d_printing", "cnc"],
                    "difficulty": "intermediate"
                },
                {
                    "name": "DC Gear Motor 12V",
                    "price_gbp": 12.00,
                    "rpm": "100",
                    "torque": "10kg/cm",
                    "use_cases": ["wheels", "conveyor", "lifting"],
                    "difficulty": "beginner"
                }
            ],
            "power": [
                {
                    "name": "Li-Po Battery 11.1V 2200mAh",
                    "price_gbp": 25.00,
                    "capacity": "2200mAh",
                    "voltage": "11.1V",
                    "weight": "185g",
                    "use_cases": ["mobile_robots", "drones", "portable_devices"],
                    "safety_notes": ["requires_balance_charger", "fire_hazard"]
                },
                {
                    "name": "Power Bank 20000mAh",
                    "price_gbp": 35.00,
                    "capacity": "20000mAh",
                    "output": "5V/2.4A",
                    "use_cases": ["long_duration", "usb_powered", "safe_option"],
                    "difficulty": "beginner"
                }
            ],
            "mechanical": [
                {
                    "name": "Aluminum Extrusion 2020",
                    "price_gbp": 8.50,
                    "length": "1000mm",
                    "profile": "20x20mm",
                    "use_cases": ["frame", "structure", "mounting"],
                    "tools_required": ["saw", "drill"]
                },
                {
                    "name": "3D Printed Parts",
                    "price_gbp": 15.00,
                    "material": "PLA",
                    "use_cases": ["custom_brackets", "gears", "housings"],
                    "requirements": ["3d_printer", "design_files"]
                }
            ]
        }
        
        self.supplier_database = {
            "RS Components": {
                "website": "uk.rs-online.com",
                "delivery_time": "1-2 days",
                "min_order": "0",
                "shipping_cost": "4.95",
                "specialties": ["electronic_components", "industrial"]
            },
            "Farnell": {
                "website": "uk.farnell.com",
                "delivery_time": "1-2 days",
                "min_order": "0",
                "shipping_cost": "4.95",
                "specialties": ["electronic_components", "development_boards"]
            },
            "Pimoroni": {
                "website": "pimoroni.com",
                "delivery_time": "1-3 days",
                "min_order": "0",
                "shipping_cost": "3.95",
                "specialties": ["raspberry_pi", "maker_products"]
            },
            "Adafruit": {
                "website": "adafruit.com",
                "delivery_time": "5-10 days",
                "min_order": "0",
                "shipping_cost": "15.00",
                "specialties": ["sensors", "development_boards", "tutorials"]
            }
        }
    
    def design_custom_robot(self, purpose: str, target_tasks: List[str], 
                           budget_gbp: float, difficulty_preference: str) -> CustomRobotDesign:
        """Design a custom robot based on requirements"""
        design_id = f"custom_robot_{int(time.time())}"
        
        # Analyze requirements and select components
        required_components = self._select_components_for_tasks(target_tasks, budget_gbp, difficulty_preference)
        
        # Calculate total cost
        total_cost = sum(comp.get('price_gbp', 0) for comp in required_components)
        
        # Generate assembly instructions
        assembly_instructions = self._generate_assembly_instructions(required_components, target_tasks)
        
        # Generate programming requirements
        programming_requirements = self._generate_programming_requirements(target_tasks, required_components)
        
        # Estimate build time
        build_time = self._estimate_build_time(required_components, difficulty_preference)
        
        design = CustomRobotDesign(
            id=design_id,
            name=f"Custom {purpose.title()} Robot",
            purpose=purpose,
            target_tasks=target_tasks,
            required_components=required_components,
            estimated_cost=total_cost,
            difficulty_level=difficulty_preference,
            build_time_hours=build_time,
            required_tools=self._get_required_tools(required_components),
            required_skills=self._get_required_skills(difficulty_preference, target_tasks),
            design_files=self._generate_design_files(target_tasks),
            assembly_instructions=assembly_instructions,
            programming_requirements=programming_requirements,
            testing_procedures=self._generate_testing_procedures(target_tasks),
            maintenance_schedule=self._generate_maintenance_schedule(required_components),
            upgrade_potential=self._identify_upgrade_potential(target_tasks),
            created_date=datetime.now()
        )
        
        self.custom_designs[design_id] = design
        self.save_custom_design(design)
        
        return design
    
    def _select_components_for_tasks(self, tasks: List[str], budget: float, difficulty: str) -> List[Dict[str, Any]]:
        """Select appropriate components for given tasks"""
        components = []
        remaining_budget = budget
        
        # Always need a microcontroller
        if difficulty == "beginner":
            microcontroller = next(c for c in self.component_database["microcontrollers"] if c["name"] == "Arduino Uno R3")
        elif difficulty == "intermediate":
            microcontroller = next(c for c in self.component_database["microcontrollers"] if c["name"] == "ESP32 DevKit")
        else:  # advanced
            microcontroller = next(c for c in self.component_database["microcontrollers"] if c["name"] == "Raspberry Pi 4 Model B")
        
        components.append(microcontroller)
        remaining_budget -= microcontroller["price_gbp"]
        
        # Select sensors based on tasks
        for task in tasks:
            task_sensors = self._get_sensors_for_task(task, difficulty, remaining_budget)
            for sensor in task_sensors:
                if sensor["price_gbp"] <= remaining_budget:
                    components.append(sensor)
                    remaining_budget -= sensor["price_gbp"]
        
        # Select actuators based on tasks
        for task in tasks:
            task_actuators = self._get_actuators_for_task(task, difficulty, remaining_budget)
            for actuator in task_actuators:
                if actuator["price_gbp"] <= remaining_budget:
                    components.append(actuator)
                    remaining_budget -= actuator["price_gbp"]
        
        # Add power supply
        if remaining_budget >= 35:
            power = next(c for c in self.component_database["power"] if c["name"] == "Power Bank 20000mAh")
        else:
            power = next(c for c in self.component_database["power"] if c["name"] == "Li-Po Battery 11.1V 2200mAh")
        
        if power["price_gbp"] <= remaining_budget:
            components.append(power)
            remaining_budget -= power["price_gbp"]
        
        # Add mechanical components
        if remaining_budget >= 15:
            mechanical = self.component_database["mechanical"][0]  # Aluminum extrusion
            components.append(mechanical)
            remaining_budget -= mechanical["price_gbp"]
        
        return components
    
    def _get_sensors_for_task(self, task: str, difficulty: str, budget: float) -> List[Dict[str, Any]]:
        """Get appropriate sensors for a specific task"""
        task_sensor_map = {
            "obstacle_avoidance": ["Ultrasonic Distance Sensor HC-SR04"],
            "navigation": ["Camera Module v2", "IMU 9-DOF Sensor"],
            "cleaning": ["Ultrasonic Distance Sensor HC-SR04"],
            "monitoring": ["Camera Module v2"],
            "security": ["Camera Module v2", "IMU 9-DOF Sensor"],
            "gardening": ["Camera Module v2"]
        }
        
        sensors = []
        for sensor_name in task_sensor_map.get(task, []):
            sensor = next((s for s in self.component_database["sensors"] if s["name"] == sensor_name), None)
            if sensor and sensor["price_gbp"] <= budget:
                if difficulty == "beginner" and sensor.get("difficulty") in ["beginner", "intermediate"]:
                    sensors.append(sensor)
                elif difficulty == "intermediate" and sensor.get("difficulty") in ["beginner", "intermediate", "advanced"]:
                    sensors.append(sensor)
                elif difficulty == "advanced":
                    sensors.append(sensor)
        
        return sensors
    
    def _get_actuators_for_task(self, task: str, difficulty: str, budget: float) -> List[Dict[str, Any]]:
        """Get appropriate actuators for a specific task"""
        task_actuator_map = {
            "movement": ["DC Gear Motor 12V"],
            "positioning": ["Servo Motor SG90", "Stepper Motor NEMA 17"],
            "cleaning": ["DC Gear Motor 12V", "Servo Motor SG90"],
            "gardening": ["Servo Motor SG90", "Stepper Motor NEMA 17"],
            "security": ["Servo Motor SG90"]
        }
        
        actuators = []
        for actuator_name in task_actuator_map.get(task, []):
            actuator = next((a for a in self.component_database["actuators"] if a["name"] == actuator_name), None)
            if actuator and actuator["price_gbp"] <= budget:
                if difficulty == "beginner" and actuator.get("difficulty") == "beginner":
                    actuators.append(actuator)
                elif difficulty in ["intermediate", "advanced"]:
                    actuators.append(actuator)
        
        return actuators
    
    def _generate_assembly_instructions(self, components: List[Dict], tasks: List[str]) -> List[Dict[str, str]]:
        """Generate step-by-step assembly instructions"""
        instructions = [
            {
                "step": "1",
                "title": "Prepare Workspace",
                "description": "Set up a clean, well-lit workspace with all tools and components organized",
                "time_minutes": "15",
                "safety_notes": "Ensure anti-static precautions for electronic components"
            },
            {
                "step": "2",
                "title": "Assemble Frame",
                "description": "Build the main structural frame using aluminum extrusion or 3D printed parts",
                "time_minutes": "45",
                "tools_required": "saw, drill, screwdriver"
            },
            {
                "step": "3",
                "title": "Mount Microcontroller",
                "description": "Securely mount the microcontroller to the frame with proper ventilation",
                "time_minutes": "20",
                "safety_notes": "Handle with care to avoid static damage"
            },
            {
                "step": "4",
                "title": "Install Power System",
                "description": "Install battery pack and power distribution, ensuring proper polarity",
                "time_minutes": "30",
                "safety_notes": "Double-check polarity before connecting power"
            },
            {
                "step": "5",
                "title": "Connect Sensors",
                "description": "Wire and mount all sensors according to the wiring diagram",
                "time_minutes": "60",
                "tools_required": "soldering iron, wire strippers, multimeter"
            },
            {
                "step": "6",
                "title": "Install Actuators",
                "description": "Mount and connect motors, servos, and other actuators",
                "time_minutes": "45",
                "safety_notes": "Ensure proper motor driver connections"
            },
            {
                "step": "7",
                "title": "Initial Testing",
                "description": "Perform basic connectivity and power tests before programming",
                "time_minutes": "30",
                "tools_required": "multimeter, oscilloscope (optional)"
            },
            {
                "step": "8",
                "title": "Programming",
                "description": "Upload and test the robot control software",
                "time_minutes": "120",
                "requirements": "Computer with development environment"
            },
            {
                "step": "9",
                "title": "Calibration",
                "description": "Calibrate sensors and fine-tune movement parameters",
                "time_minutes": "60",
                "notes": "May require multiple iterations"
            },
            {
                "step": "10",
                "title": "Final Testing",
                "description": "Comprehensive testing of all functions and safety systems",
                "time_minutes": "90",
                "safety_notes": "Test in controlled environment first"
            }
        ]
        
        return instructions
    
    def _generate_programming_requirements(self, tasks: List[str], components: List[Dict]) -> Dict[str, Any]:
        """Generate programming requirements and code structure"""
        microcontroller = next((c for c in components if c.get("programming")), None)
        
        if not microcontroller:
            return {"error": "No programmable microcontroller found"}
        
        programming_language = microcontroller["programming"].split(",")[0].strip()
        
        code_structure = {
            "main_loop": {
                "description": "Main control loop handling sensor reading and actuator control",
                "functions": ["sensor_reading", "decision_making", "actuator_control", "safety_checks"]
            },
            "sensor_modules": {
                "description": "Individual modules for each sensor type",
                "modules": [comp["name"] for comp in components if comp in self.component_database.get("sensors", [])]
            },
            "actuator_modules": {
                "description": "Control modules for motors and servos",
                "modules": [comp["name"] for comp in components if comp in self.component_database.get("actuators", [])]
            },
            "communication": {
                "description": "WiFi/Bluetooth communication for remote control",
                "protocols": ["HTTP", "MQTT", "WebSocket"]
            },
            "safety_systems": {
                "description": "Emergency stop and error handling",
                "features": ["watchdog_timer", "emergency_stop", "error_recovery"]
            }
        }
        
        libraries_needed = []
        if programming_language == "Arduino IDE":
            libraries_needed = ["WiFi", "Servo", "NewPing", "ArduinoJson"]
        elif programming_language == "Python":
            libraries_needed = ["RPi.GPIO", "opencv-python", "numpy", "requests"]
        
        return {
            "programming_language": programming_language,
            "development_environment": microcontroller["programming"],
            "code_structure": code_structure,
            "required_libraries": libraries_needed,
            "estimated_lines_of_code": len(tasks) * 200 + 500,
            "complexity_level": "intermediate" if len(tasks) > 2 else "beginner"
        }
    
    def _estimate_build_time(self, components: List[Dict], difficulty: str) -> int:
        """Estimate total build time in hours"""
        base_time = 8  # Base assembly time
        
        # Add time based on component count
        component_time = len(components) * 1.5
        
        # Add time based on difficulty
        difficulty_multiplier = {"beginner": 1.5, "intermediate": 1.2, "advanced": 1.0}
        
        total_time = (base_time + component_time) * difficulty_multiplier.get(difficulty, 1.2)
        
        return int(total_time)
    
    def _get_required_tools(self, components: List[Dict]) -> List[str]:
        """Get list of required tools for assembly"""
        basic_tools = [
            "Screwdriver set",
            "Wire strippers",
            "Multimeter",
            "Soldering iron and solder",
            "Heat shrink tubing",
            "Breadboard (for prototyping)",
            "Jumper wires"
        ]
        
        advanced_tools = []
        for component in components:
            if component.get("tools_required"):
                advanced_tools.extend(component["tools_required"])
        
        return basic_tools + list(set(advanced_tools))
    
    def _get_required_skills(self, difficulty: str, tasks: List[str]) -> List[str]:
        """Get list of required skills"""
        skill_map = {
            "beginner": [
                "Basic electronics knowledge",
                "Ability to follow instructions",
                "Basic soldering skills",
                "Computer literacy"
            ],
            "intermediate": [
                "Electronics prototyping",
                "Programming basics",
                "Circuit debugging",
                "Mechanical assembly",
                "3D printing (optional)"
            ],
            "advanced": [
                "Advanced programming",
                "Circuit design",
                "PCB design (optional)",
                "Control systems",
                "Computer vision (if applicable)",
                "Machine learning (if applicable)"
            ]
        }
        
        return skill_map.get(difficulty, skill_map["intermediate"])
    
    def _generate_design_files(self, tasks: List[str]) -> List[str]:
        """Generate list of design files needed"""
        files = [
            "Wiring_Diagram.pdf",
            "Assembly_Instructions.pdf",
            "Parts_List.xlsx",
            "Source_Code.zip"
        ]
        
        if any(task in ["movement", "cleaning", "gardening"] for task in tasks):
            files.extend([
                "Chassis_Design.stl",
                "Mounting_Brackets.stl",
                "Wheel_Assembly.stl"
            ])
        
        if "monitoring" in tasks or "security" in tasks:
            files.extend([
                "Camera_Mount.stl",
                "Sensor_Housing.stl"
            ])
        
        return files
    
    def _generate_testing_procedures(self, tasks: List[str]) -> List[str]:
        """Generate testing procedures for the robot"""
        procedures = [
            "Power system test - Verify all voltages and current draw",
            "Communication test - Verify WiFi/Bluetooth connectivity",
            "Sensor calibration - Calibrate all sensors for accurate readings",
            "Basic movement test - Test forward, backward, turning movements",
            "Safety system test - Verify emergency stop and error handling"
        ]
        
        task_specific_tests = {
            "cleaning": ["Cleaning pattern test", "Obstacle avoidance test", "Return to dock test"],
            "monitoring": ["Camera focus test", "Motion detection test", "Alert system test"],
            "gardening": ["Watering system test", "Plant detection test", "Weather response test"],
            "security": ["Intrusion detection test", "Alert notification test", "Night vision test"]
        }
        
        for task in tasks:
            if task in task_specific_tests:
                procedures.extend(task_specific_tests[task])
        
        return procedures
    
    def _generate_maintenance_schedule(self, components: List[Dict]) -> Dict[str, str]:
        """Generate maintenance schedule"""
        return {
            "daily": "Check battery level, clean sensors",
            "weekly": "Inspect mechanical connections, clean filters",
            "monthly": "Lubricate moving parts, update firmware",
            "quarterly": "Deep clean all components, check wear items",
            "annually": "Replace batteries, comprehensive system check"
        }
    
    def _identify_upgrade_potential(self, tasks: List[str]) -> List[str]:
        """Identify potential future upgrades"""
        upgrades = [
            "Add GPS module for outdoor navigation",
            "Upgrade to more powerful microcontroller",
            "Add machine learning capabilities",
            "Implement voice control",
            "Add solar charging capability"
        ]
        
        task_specific_upgrades = {
            "cleaning": ["Add UV sterilization", "Implement smart mapping"],
            "monitoring": ["Add thermal imaging", "Implement facial recognition"],
            "gardening": ["Add soil analysis sensors", "Implement crop yield optimization"],
            "security": ["Add night vision", "Implement perimeter patrol"]
        }
        
        for task in tasks:
            if task in task_specific_upgrades:
                upgrades.extend(task_specific_upgrades[task])
        
        return upgrades
    
    def coordinate_multiple_robots(self, robot_ids: List[str], task_description: str, 
                                 coordination_type: str = "parallel") -> RobotCoordination:
        """Coordinate multiple robots for complex tasks"""
        coordination_id = f"coord_{int(time.time())}"
        
        # Analyze task and distribute among robots
        task_distribution = self._distribute_tasks(robot_ids, task_description, coordination_type)
        
        # Calculate efficiency multiplier
        efficiency_multiplier = self._calculate_coordination_efficiency(robot_ids, coordination_type)
        
        # Estimate completion time
        estimated_time = self._estimate_coordination_time(robot_ids, task_distribution)
        
        coordination = RobotCoordination(
            id=coordination_id,
            participating_robots=robot_ids,
            coordination_type=coordination_type,
            task_distribution=task_distribution,
            communication_protocol="MQTT",
            synchronization_points=self._generate_sync_points(task_distribution),
            efficiency_multiplier=efficiency_multiplier,
            estimated_completion_time=estimated_time,
            status="planned"
        )
        
        self.coordinations[coordination_id] = coordination
        self.save_coordination(coordination)
        
        return coordination
    
    def _distribute_tasks(self, robot_ids: List[str], task_description: str, 
                         coordination_type: str) -> Dict[str, List[str]]:
        """Distribute tasks among robots based on their capabilities"""
        distribution = {}
        
        # Get robot capabilities
        robot_capabilities = {}
        for robot_id in robot_ids:
            if robot_id in self.robots:
                robot_capabilities[robot_id] = self.robots[robot_id].capabilities
        
        # Simple task distribution logic
        if coordination_type == "parallel":
            # Divide task into parallel subtasks
            if "cleaning" in task_description.lower():
                distribution = {
                    robot_ids[0]: ["vacuum_living_room", "vacuum_kitchen"],
                    robot_ids[1]: ["mop_bathroom", "mop_hallway"] if len(robot_ids) > 1 else []
                }
            elif "monitoring" in task_description.lower():
                distribution = {
                    robot_ids[0]: ["monitor_front_entrance", "patrol_perimeter"],
                    robot_ids[1]: ["monitor_back_garden", "check_windows"] if len(robot_ids) > 1 else []
                }
        elif coordination_type == "sequential":
            # Tasks that must be done in order
            distribution = {
                robot_ids[0]: ["prepare_area", "initial_cleaning"],
                robot_ids[1]: ["deep_cleaning", "final_inspection"] if len(robot_ids) > 1 else []
            }
        elif coordination_type == "collaborative":
            # Tasks requiring cooperation
            distribution = {
                robot_ids[0]: ["hold_object", "provide_lighting"],
                robot_ids[1]: ["manipulate_object", "perform_task"] if len(robot_ids) > 1 else []
            }
        
        return distribution
    
    def _calculate_coordination_efficiency(self, robot_ids: List[str], coordination_type: str) -> float:
        """Calculate efficiency multiplier for coordinated operation"""
        base_efficiency = 1.0
        
        # Get average efficiency of participating robots
        total_efficiency = 0
        for robot_id in robot_ids:
            if robot_id in self.robots:
                total_efficiency += self.robots[robot_id].efficiency_score
        
        avg_efficiency = total_efficiency / len(robot_ids) if robot_ids else 0
        
        # Apply coordination bonuses/penalties
        coordination_multipliers = {
            "parallel": 1.8,      # High efficiency gain
            "sequential": 1.2,    # Moderate efficiency gain
            "collaborative": 2.5  # Highest efficiency for complex tasks
        }
        
        multiplier = coordination_multipliers.get(coordination_type, 1.0)
        
        # Factor in robot compatibility (simplified)
        compatibility_bonus = 0.1 if len(robot_ids) <= 3 else -0.1  # Too many robots can be inefficient
        
        return min(3.0, base_efficiency * multiplier * (avg_efficiency / 100) + compatibility_bonus)
    
    def _estimate_coordination_time(self, robot_ids: List[str], task_distribution: Dict[str, List[str]]) -> int:
        """Estimate total time for coordinated task completion"""
        max_time = 0
        
        for robot_id, tasks in task_distribution.items():
            robot_time = len(tasks) * 30  # 30 minutes per task (simplified)
            
            # Factor in robot efficiency
            if robot_id in self.robots:
                efficiency_factor = self.robots[robot_id].efficiency_score / 100
                robot_time = int(robot_time / efficiency_factor)
            
            max_time = max(max_time, robot_time)
        
        return max_time
    
    def _generate_sync_points(self, task_distribution: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Generate synchronization points for coordinated tasks"""
        sync_points = []
        
        # Start synchronization
        sync_points.append({
            "type": "start",
            "description": "All robots begin their assigned tasks",
            "required_robots": list(task_distribution.keys()),
            "timeout_minutes": 5
        })
        
        # Mid-task synchronization (if needed)
        if len(task_distribution) > 1:
            sync_points.append({
                "type": "checkpoint",
                "description": "Progress check and coordination adjustment",
                "required_robots": list(task_distribution.keys()),
                "timeout_minutes": 10
            })
        
        # Completion synchronization
        sync_points.append({
            "type": "completion",
            "description": "All robots complete their tasks and return to base",
            "required_robots": list(task_distribution.keys()),
            "timeout_minutes": 15
        })
        
        return sync_points
    
    def execute_robot_task(self, robot_id: str, task: RobotTask) -> Dict[str, Any]:
        """Execute a task on a specific robot"""
        if robot_id not in self.robots:
            return {"error": f"Robot {robot_id} not found"}
        
        robot = self.robots[robot_id]
        
        if robot.status != RobotStatus.IDLE:
            return {"error": f"Robot {robot_id} is not available (status: {robot.status.value})"}
        
        # Update robot status
        robot.status = RobotStatus.WORKING
        robot.current_task = task.id
        task.status = "in_progress"
        
        # Simulate task execution (in real implementation, this would interface with actual robots)
        execution_result = self._simulate_task_execution(robot, task)
        
        # Update task and robot status
        task.status = "completed" if execution_result["success"] else "failed"
        task.actual_duration = execution_result["duration"]
        task.success_rate = execution_result["success_rate"]
        task.energy_consumed = execution_result["energy_consumed"]
        
        robot.status = RobotStatus.IDLE
        robot.current_task = None
        robot.battery_level -= execution_result["battery_used"]
        robot.total_runtime_hours += execution_result["duration"] / 60
        
        if not execution_result["success"]:
            robot.error_count += 1
        
        # Save updates
        self.save_robot(robot)
        self.save_task(task)
        
        # Log performance
        self.log_robot_performance(robot_id, task.id, execution_result)
        
        return execution_result
    
    def _simulate_task_execution(self, robot: Robot, task: RobotTask) -> Dict[str, Any]:
        """Simulate robot task execution (replace with real robot interface)"""
        import random
        
        # Simulate execution based on robot capabilities and task requirements
        base_success_rate = robot.efficiency_score / 100
        task_complexity = len(task.required_tools) * 0.1
        
        success_rate = max(0.1, base_success_rate - task_complexity)
        success = random.random() < success_rate
        
        # Simulate duration (with some variance)
        duration_variance = random.uniform(0.8, 1.2)
        actual_duration = int(task.estimated_duration * duration_variance)
        
        # Simulate energy consumption
        energy_consumed = actual_duration * 0.5  # Simplified energy model
        battery_used = energy_consumed / 10  # Convert to battery percentage
        
        return {
            "success": success,
            "duration": actual_duration,
            "success_rate": success_rate,
            "energy_consumed": energy_consumed,
            "battery_used": battery_used,
            "error_message": None if success else "Simulated task failure"
        }
    
    def log_robot_performance(self, robot_id: str, task_id: str, performance_data: Dict[str, Any]):
        """Log robot performance data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO robot_performance_log 
            (robot_id, timestamp, task_id, performance_metrics, energy_usage, error_details)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            robot_id, datetime.now(), task_id, json.dumps(performance_data),
            performance_data.get("energy_consumed"), 
            performance_data.get("error_message")
        ))
        
        conn.commit()
        conn.close()
    
    def get_robot_recommendations(self, budget_gbp: float, tasks: List[str], 
                                space_size: str) -> List[Dict[str, Any]]:
        """Get robot recommendations based on requirements"""
        recommendations = []
        
        # Define robot options with their capabilities and costs
        robot_options = [
            {
                "name": "iRobot Roomba i7+",
                "type": "vacuum",
                "cost": 599,
                "capabilities": ["vacuum", "mapping", "scheduling", "auto_empty"],
                "space_suitability": ["small", "medium", "large"],
                "maintenance_cost_yearly": 50,
                "energy_cost_yearly": 15
            },
            {
                "name": "Ecovacs Winbot X",
                "type": "window_cleaner",
                "cost": 299,
                "capabilities": ["window_cleaning", "safety_rope", "edge_detection"],
                "space_suitability": ["small", "medium", "large"],
                "maintenance_cost_yearly": 30,
                "energy_cost_yearly": 8
            },
            {
                "name": "Husqvarna Automower",
                "type": "lawn_mower",
                "cost": 1299,
                "capabilities": ["grass_cutting", "weather_sensor", "theft_protection"],
                "space_suitability": ["medium", "large"],
                "maintenance_cost_yearly": 100,
                "energy_cost_yearly": 25
            },
            {
                "name": "Custom Security Robot",
                "type": "security",
                "cost": 800,
                "capabilities": ["patrol", "camera", "motion_detection", "alerts"],
                "space_suitability": ["medium", "large"],
                "maintenance_cost_yearly": 75,
                "energy_cost_yearly": 40
            }
        ]
        
        for robot in robot_options:
            if robot["cost"] <= budget_gbp and space_size in robot["space_suitability"]:
                # Calculate task match score
                task_match_score = 0
                for task in tasks:
                    if any(capability in task.lower() for capability in robot["capabilities"]):
                        task_match_score += 1
                
                if task_match_score > 0:
                    # Calculate total cost of ownership (3 years)
                    total_cost_3_years = (
                        robot["cost"] + 
                        robot["maintenance_cost_yearly"] * 3 + 
                        robot["energy_cost_yearly"] * 3
                    )
                    
                    recommendation = {
                        "robot": robot,
                        "task_match_score": task_match_score,
                        "total_cost_3_years": total_cost_3_years,
                        "roi_score": task_match_score / (total_cost_3_years / 1000),  # Simplified ROI
                        "recommendation_reason": f"Matches {task_match_score} of your requirements"
                    }
                    
                    recommendations.append(recommendation)
        
        # Sort by ROI score
        recommendations.sort(key=lambda x: x["roi_score"], reverse=True)
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def start_coordination_engine(self):
        """Start the robot coordination engine"""
        def coordination_monitor():
            while True:
                # Monitor active coordinations
                for coord_id, coordination in self.coordinations.items():
                    if coordination.status == "active":
                        self._monitor_coordination_progress(coordination)
                
                time.sleep(30)  # Check every 30 seconds
        
        # Start coordination monitor in background thread
        coord_thread = threading.Thread(target=coordination_monitor, daemon=True)
        coord_thread.start()
        logging.info("Robot coordination engine started")
    
    def _monitor_coordination_progress(self, coordination: RobotCoordination):
        """Monitor progress of active coordination"""
        # Check if all robots are still active and responding
        active_robots = 0
        for robot_id in coordination.participating_robots:
            if robot_id in self.robots and self.robots[robot_id].status == RobotStatus.WORKING:
                active_robots += 1
        
        # Update coordination status based on robot status
        if active_robots == 0:
            coordination.status = "completed"
            logging.info(f"Coordination {coordination.id} completed")
        elif active_robots < len(coordination.participating_robots):
            coordination.status = "partial_failure"
            logging.warning(f"Coordination {coordination.id} has partial failures")
    
    def save_robot(self, robot: Robot):
        """Save robot to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO robots 
            (id, name, robot_type, status, current_task, battery_level, location, capabilities,
             last_maintenance, total_runtime_hours, error_count, efficiency_score, cost_gbp,
             manufacturer, model, firmware_version, connectivity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            robot.id, robot.name, robot.robot_type.value, robot.status.value,
            robot.current_task, robot.battery_level, json.dumps(robot.location),
            json.dumps(robot.capabilities), robot.last_maintenance, robot.total_runtime_hours,
            robot.error_count, robot.efficiency_score, robot.cost_gbp, robot.manufacturer,
            robot.model, robot.firmware_version, robot.connectivity
        ))
        
        conn.commit()
        conn.close()
    
    def save_task(self, task: RobotTask):
        """Save task to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO robot_tasks 
            (id, robot_id, task_type, description, priority, scheduled_time, estimated_duration,
             required_tools, target_location, completion_criteria, status, actual_duration,
             success_rate, energy_consumed, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task.id, task.robot_id, task.task_type.value, task.description, task.priority,
            task.scheduled_time, task.estimated_duration, json.dumps(task.required_tools),
            json.dumps(task.target_location), json.dumps(task.completion_criteria),
            task.status, task.actual_duration, task.success_rate, task.energy_consumed,
            task.created_date
        ))
        
        conn.commit()
        conn.close()
    
    def save_custom_design(self, design: CustomRobotDesign):
        """Save custom robot design to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO custom_robot_designs 
            (id, name, purpose, target_tasks, required_components, estimated_cost, difficulty_level,
             build_time_hours, required_tools, required_skills, design_files, assembly_instructions,
             programming_requirements, testing_procedures, maintenance_schedule, upgrade_potential, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            design.id, design.name, design.purpose, json.dumps(design.target_tasks),
            json.dumps(design.required_components), design.estimated_cost, design.difficulty_level,
            design.build_time_hours, json.dumps(design.required_tools), json.dumps(design.required_skills),
            json.dumps(design.design_files), json.dumps(design.assembly_instructions),
            json.dumps(design.programming_requirements), json.dumps(design.testing_procedures),
            json.dumps(design.maintenance_schedule), json.dumps(design.upgrade_potential), design.created_date
        ))
        
        conn.commit()
        conn.close()
    
    def save_coordination(self, coordination: RobotCoordination):
        """Save robot coordination to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO robot_coordinations 
            (id, participating_robots, coordination_type, task_distribution, communication_protocol,
             synchronization_points, efficiency_multiplier, estimated_completion_time, status, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            coordination.id, json.dumps(coordination.participating_robots), coordination.coordination_type,
            json.dumps(coordination.task_distribution), coordination.communication_protocol,
            json.dumps(coordination.synchronization_points), coordination.efficiency_multiplier,
            coordination.estimated_completion_time, coordination.status, datetime.now()
        ))
        
        conn.commit()
        conn.close()
    
    def load_data(self):
        """Load existing data from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Load robots
        cursor.execute('SELECT * FROM robots')
        for row in cursor.fetchall():
            robot = Robot(
                id=row[0], name=row[1], robot_type=RobotType(row[2]), status=RobotStatus(row[3]),
                current_task=row[4], battery_level=row[5], location=json.loads(row[6]),
                capabilities=json.loads(row[7]), last_maintenance=datetime.fromisoformat(row[8]),
                total_runtime_hours=row[9], error_count=row[10], efficiency_score=row[11],
                cost_gbp=row[12], manufacturer=row[13], model=row[14], firmware_version=row[15],
                connectivity=row[16]
            )
            self.robots[robot.id] = robot
        
        conn.close()
        logging.info(f"Loaded {len(self.robots)} robots from database")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive robotics dashboard data"""
        total_robots = len(self.robots)
        active_robots = len([r for r in self.robots.values() if r.status == RobotStatus.WORKING])
        avg_battery = sum(r.battery_level for r in self.robots.values()) / total_robots if total_robots > 0 else 0
        
        return {
            "robots": {
                "total": total_robots,
                "active": active_robots,
                "idle": len([r for r in self.robots.values() if r.status == RobotStatus.IDLE]),
                "charging": len([r for r in self.robots.values() if r.status == RobotStatus.CHARGING]),
                "error": len([r for r in self.robots.values() if r.status == RobotStatus.ERROR]),
                "average_battery": round(avg_battery, 1),
                "total_runtime_hours": sum(r.total_runtime_hours for r in self.robots.values())
            },
            "tasks": {
                "total": len(self.tasks),
                "completed": len([t for t in self.tasks.values() if t.status == "completed"]),
                "in_progress": len([t for t in self.tasks.values() if t.status == "in_progress"]),
                "pending": len([t for t in self.tasks.values() if t.status == "pending"])
            },
            "custom_designs": {
                "total": len(self.custom_designs),
                "beginner": len([d for d in self.custom_designs.values() if d.difficulty_level == "beginner"]),
                "intermediate": len([d for d in self.custom_designs.values() if d.difficulty_level == "intermediate"]),
                "advanced": len([d for d in self.custom_designs.values() if d.difficulty_level == "advanced"])
            },
            "coordinations": {
                "total": len(self.coordinations),
                "active": len([c for c in self.coordinations.values() if c.status == "active"]),
                "completed": len([c for c in self.coordinations.values() if c.status == "completed"])
            }
        }


# Global robotics controller instance
robotics_controller = RoboticsController()

def initialize_robotics_system():
    """Initialize the robotics system"""
    logging.info("Robotics system initialized with sample robots and components")

if __name__ == "__main__":
    initialize_robotics_system()
    
    # Example usage
    print("Robotics Controller initialized")
    dashboard_data = robotics_controller.get_dashboard_data()
    print(f"Dashboard data: {dashboard_data}")
    
    # Example: Design a custom cleaning robot
    custom_robot = robotics_controller.design_custom_robot(
        purpose="home cleaning",
        target_tasks=["obstacle_avoidance", "cleaning", "navigation"],
        budget_gbp=500,
        difficulty_preference="intermediate"
    )
    print(f"Custom robot designed: {custom_robot.name} - £{custom_robot.estimated_cost}")

