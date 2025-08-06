"""
Autonomous Home Management & Self-Healing Systems
Enables the TechCraft Genius AI to manage the home autonomously, predict and prevent issues,
and implement self-healing mechanisms for maximum laziness and efficiency.
"""

import json
import sqlite3
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import threading
import time
import logging
from dataclasses import dataclass
from enum import Enum
import math

class SystemStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    FAILED = "failed"
    MAINTENANCE = "maintenance"

class ActionPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

@dataclass
class SystemAlert:
    system_name: str
    alert_type: str
    severity: SystemStatus
    message: str
    timestamp: datetime
    auto_fixable: bool
    estimated_fix_time: int  # minutes
    cost_estimate: float

class AutonomousHomeManager:
    def __init__(self, db_path: str = "autonomous_home.db"):
        self.db_path = db_path
        self.init_database()
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # London-specific data
        self.london_weather_api = "http://api.openweathermap.org/data/2.5"
        self.london_coords = {"lat": 51.5074, "lon": -0.1278}
        
        # System monitoring intervals (seconds)
        self.monitoring_intervals = {
            "energy": 300,      # 5 minutes
            "security": 60,     # 1 minute
            "climate": 180,     # 3 minutes
            "water": 600,       # 10 minutes
            "appliances": 900,  # 15 minutes
            "network": 120      # 2 minutes
        }
        
    def init_database(self):
        """Initialize the autonomous home management database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Home systems table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS home_systems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                system_name TEXT NOT NULL UNIQUE,
                system_type TEXT NOT NULL,
                location TEXT,
                device_id TEXT,
                ip_address TEXT,
                api_endpoint TEXT,
                status TEXT DEFAULT 'unknown',
                last_check TIMESTAMP,
                health_score REAL DEFAULT 100.0,
                maintenance_due DATE,
                warranty_expires DATE,
                installation_date DATE,
                expected_lifespan_years INTEGER,
                replacement_cost REAL,
                energy_consumption_watts REAL,
                is_critical BOOLEAN DEFAULT 0,
                auto_healing_enabled BOOLEAN DEFAULT 1,
                monitoring_enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # System alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                system_id INTEGER,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                details TEXT,
                auto_fixable BOOLEAN DEFAULT 0,
                fix_attempted BOOLEAN DEFAULT 0,
                fix_successful BOOLEAN DEFAULT 0,
                estimated_fix_time INTEGER,
                actual_fix_time INTEGER,
                cost_estimate REAL,
                actual_cost REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                FOREIGN KEY (system_id) REFERENCES home_systems (id)
            )
        ''')
        
        # Automated actions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS automated_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                system_id INTEGER,
                action_type TEXT NOT NULL,
                action_description TEXT,
                trigger_condition TEXT,
                priority INTEGER DEFAULT 2,
                schedule_type TEXT,
                schedule_value TEXT,
                last_executed TIMESTAMP,
                execution_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 100.0,
                average_duration INTEGER,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (system_id) REFERENCES home_systems (id)
            )
        ''')
        
        # Resource management table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resource_management (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_type TEXT NOT NULL,
                current_level REAL,
                optimal_level REAL,
                minimum_level REAL,
                maximum_level REAL,
                unit TEXT,
                cost_per_unit REAL,
                supplier TEXT,
                auto_reorder_enabled BOOLEAN DEFAULT 1,
                reorder_threshold REAL,
                reorder_quantity REAL,
                last_reorder_date DATE,
                next_delivery_date DATE,
                monthly_consumption REAL,
                seasonal_adjustment REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Environmental conditions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS environmental_conditions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location TEXT NOT NULL,
                temperature REAL,
                humidity REAL,
                air_quality_index INTEGER,
                light_level REAL,
                noise_level REAL,
                co2_level REAL,
                pressure REAL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Predictive maintenance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictive_maintenance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                system_id INTEGER,
                prediction_type TEXT NOT NULL,
                predicted_failure_date DATE,
                confidence_level REAL,
                recommended_action TEXT,
                estimated_cost REAL,
                urgency_level INTEGER,
                parts_needed TEXT,
                service_provider TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                action_taken BOOLEAN DEFAULT 0,
                FOREIGN KEY (system_id) REFERENCES home_systems (id)
            )
        ''')
        
        # Self-healing actions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS self_healing_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                system_id INTEGER,
                problem_detected TEXT,
                healing_action TEXT,
                success_probability REAL,
                execution_time INTEGER,
                backup_plan TEXT,
                executed_at TIMESTAMP,
                success BOOLEAN,
                error_message TEXT,
                FOREIGN KEY (system_id) REFERENCES home_systems (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Initialize with common home systems
        self._populate_default_systems()
    
    def _populate_default_systems(self):
        """Populate database with common home systems"""
        default_systems = [
            {
                "system_name": "Central Heating",
                "system_type": "HVAC",
                "location": "Utility Room",
                "is_critical": True,
                "expected_lifespan_years": 15,
                "replacement_cost": 3500.0,
                "energy_consumption_watts": 2000
            },
            {
                "system_name": "Hot Water System",
                "system_type": "Water",
                "location": "Utility Room",
                "is_critical": True,
                "expected_lifespan_years": 12,
                "replacement_cost": 1200.0,
                "energy_consumption_watts": 3000
            },
            {
                "system_name": "Main Electrical Panel",
                "system_type": "Electrical",
                "location": "Utility Room",
                "is_critical": True,
                "expected_lifespan_years": 25,
                "replacement_cost": 800.0,
                "energy_consumption_watts": 0
            },
            {
                "system_name": "WiFi Router",
                "system_type": "Network",
                "location": "Living Room",
                "is_critical": False,
                "expected_lifespan_years": 5,
                "replacement_cost": 150.0,
                "energy_consumption_watts": 20
            },
            {
                "system_name": "Security System",
                "system_type": "Security",
                "location": "Multiple",
                "is_critical": False,
                "expected_lifespan_years": 8,
                "replacement_cost": 600.0,
                "energy_consumption_watts": 50
            },
            {
                "system_name": "Washing Machine",
                "system_type": "Appliance",
                "location": "Utility Room",
                "is_critical": False,
                "expected_lifespan_years": 10,
                "replacement_cost": 500.0,
                "energy_consumption_watts": 2100
            },
            {
                "system_name": "Refrigerator",
                "system_type": "Appliance",
                "location": "Kitchen",
                "is_critical": False,
                "expected_lifespan_years": 12,
                "replacement_cost": 700.0,
                "energy_consumption_watts": 150
            }
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for system in default_systems:
            cursor.execute('''
                INSERT OR IGNORE INTO home_systems 
                (system_name, system_type, location, is_critical, expected_lifespan_years,
                 replacement_cost, energy_consumption_watts)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                system["system_name"], system["system_type"], system["location"],
                system["is_critical"], system["expected_lifespan_years"],
                system["replacement_cost"], system["energy_consumption_watts"]
            ))
        
        conn.commit()
        conn.close()
        
        # Initialize resource management
        self._initialize_resource_management()
    
    def _initialize_resource_management(self):
        """Initialize resource management for common household resources"""
        resources = [
            {
                "resource_type": "Electricity",
                "unit": "kWh",
                "cost_per_unit": 0.28,  # UK average
                "optimal_level": 500,
                "minimum_level": 0,
                "maximum_level": 1000,
                "reorder_threshold": 100,
                "monthly_consumption": 350
            },
            {
                "resource_type": "Gas",
                "unit": "kWh",
                "cost_per_unit": 0.07,  # UK average
                "optimal_level": 1000,
                "minimum_level": 0,
                "maximum_level": 2000,
                "reorder_threshold": 200,
                "monthly_consumption": 800
            },
            {
                "resource_type": "Water",
                "unit": "Litres",
                "cost_per_unit": 0.002,  # UK average
                "optimal_level": 10000,
                "minimum_level": 1000,
                "maximum_level": 20000,
                "monthly_consumption": 8000
            },
            {
                "resource_type": "Internet Data",
                "unit": "GB",
                "cost_per_unit": 0.05,
                "optimal_level": 500,
                "minimum_level": 50,
                "maximum_level": 1000,
                "monthly_consumption": 300
            }
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for resource in resources:
            cursor.execute('''
                INSERT OR IGNORE INTO resource_management 
                (resource_type, unit, cost_per_unit, optimal_level, minimum_level,
                 maximum_level, reorder_threshold, monthly_consumption)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                resource["resource_type"], resource["unit"], resource["cost_per_unit"],
                resource["optimal_level"], resource["minimum_level"], resource["maximum_level"],
                resource["reorder_threshold"], resource["monthly_consumption"]
            ))
        
        conn.commit()
        conn.close()
    
    def start_autonomous_monitoring(self):
        """Start the autonomous monitoring system"""
        if self.monitoring_active:
            return {"status": "already_running"}
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        return {"status": "started", "message": "Autonomous monitoring system activated"}
    
    def stop_autonomous_monitoring(self):
        """Stop the autonomous monitoring system"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        return {"status": "stopped", "message": "Autonomous monitoring system deactivated"}
    
    def _monitoring_loop(self):
        """Main monitoring loop that runs continuously"""
        last_checks = {system: datetime.min for system in self.monitoring_intervals.keys()}
        
        while self.monitoring_active:
            try:
                current_time = datetime.now()
                
                for system_type, interval in self.monitoring_intervals.items():
                    if (current_time - last_checks[system_type]).total_seconds() >= interval:
                        self._check_system_type(system_type)
                        last_checks[system_type] = current_time
                
                # Check for predictive maintenance opportunities
                self._run_predictive_analysis()
                
                # Execute scheduled automated actions
                self._execute_scheduled_actions()
                
                # Monitor resource levels
                self._monitor_resources()
                
                # Sleep for a short interval before next check
                time.sleep(30)
                
            except Exception as e:
                logging.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(60)  # Wait longer on error
    
    def _check_system_type(self, system_type: str):
        """Check all systems of a specific type"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM home_systems 
            WHERE system_type = ? AND monitoring_enabled = 1
        ''', (system_type.upper(),))
        
        systems = cursor.fetchall()
        conn.close()
        
        for system in systems:
            self._check_individual_system(system)
    
    def _check_individual_system(self, system: Tuple):
        """Check an individual system's health"""
        system_id = system[0]
        system_name = system[1]
        system_type = system[2]
        
        # Simulate system health check (in real implementation, this would query actual devices)
        health_data = self._simulate_system_health_check(system_name, system_type)
        
        # Update system status
        self._update_system_status(system_id, health_data)
        
        # Check for issues and trigger self-healing if needed
        if health_data["status"] != SystemStatus.HEALTHY:
            self._trigger_self_healing(system_id, health_data)
    
    def _simulate_system_health_check(self, system_name: str, system_type: str) -> Dict:
        """Simulate a system health check (replace with real device queries)"""
        import random
        
        # Simulate different health scenarios
        health_score = random.uniform(70, 100)
        
        if health_score > 95:
            status = SystemStatus.HEALTHY
            issues = []
        elif health_score > 85:
            status = SystemStatus.WARNING
            issues = ["Minor performance degradation detected"]
        elif health_score > 70:
            status = SystemStatus.CRITICAL
            issues = ["Significant performance issues", "Maintenance required"]
        else:
            status = SystemStatus.FAILED
            issues = ["System failure detected", "Immediate attention required"]
        
        # System-specific checks
        specific_data = {}
        if system_type == "HVAC":
            specific_data = {
                "temperature_accuracy": random.uniform(0.5, 2.0),
                "filter_condition": random.choice(["clean", "dirty", "very_dirty"]),
                "energy_efficiency": random.uniform(80, 100)
            }
        elif system_type == "Water":
            specific_data = {
                "pressure": random.uniform(1.5, 3.0),
                "temperature_stability": random.uniform(85, 100),
                "leak_detected": random.choice([True, False])
            }
        elif system_type == "Network":
            specific_data = {
                "signal_strength": random.uniform(70, 100),
                "connection_stability": random.uniform(90, 100),
                "bandwidth_utilization": random.uniform(20, 80)
            }
        
        return {
            "status": status,
            "health_score": health_score,
            "issues": issues,
            "specific_data": specific_data,
            "timestamp": datetime.now()
        }
    
    def _update_system_status(self, system_id: int, health_data: Dict):
        """Update system status in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE home_systems 
            SET status = ?, health_score = ?, last_check = ?
            WHERE id = ?
        ''', (
            health_data["status"].value,
            health_data["health_score"],
            health_data["timestamp"],
            system_id
        ))
        
        # Log any issues as alerts
        for issue in health_data["issues"]:
            cursor.execute('''
                INSERT INTO system_alerts 
                (system_id, alert_type, severity, message, auto_fixable)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                system_id, "health_check", health_data["status"].value,
                issue, health_data["status"] in [SystemStatus.WARNING, SystemStatus.CRITICAL]
            ))
        
        conn.commit()
        conn.close()
    
    def _trigger_self_healing(self, system_id: int, health_data: Dict):
        """Trigger self-healing actions for a system"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get system details
        cursor.execute('SELECT * FROM home_systems WHERE id = ?', (system_id,))
        system = cursor.fetchone()
        
        if not system or not system[17]:  # auto_healing_enabled
            conn.close()
            return
        
        system_name = system[1]
        system_type = system[2]
        
        # Determine appropriate healing actions
        healing_actions = self._get_healing_actions(system_type, health_data)
        
        for action in healing_actions:
            # Record the healing attempt
            cursor.execute('''
                INSERT INTO self_healing_actions 
                (system_id, problem_detected, healing_action, success_probability, executed_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                system_id, json.dumps(health_data["issues"]),
                action["description"], action["success_probability"], datetime.now()
            ))
            
            # Execute the healing action
            success = self._execute_healing_action(system_id, action)
            
            # Update the record with results
            healing_id = cursor.lastrowid
            cursor.execute('''
                UPDATE self_healing_actions 
                SET success = ?, execution_time = ?
                WHERE id = ?
            ''', (success, action.get("execution_time", 60), healing_id))
        
        conn.commit()
        conn.close()
    
    def _get_healing_actions(self, system_type: str, health_data: Dict) -> List[Dict]:
        """Get appropriate healing actions for a system type and health condition"""
        actions = []
        
        if system_type == "HVAC":
            if "filter" in str(health_data["issues"]).lower():
                actions.append({
                    "description": "Schedule filter replacement",
                    "success_probability": 0.9,
                    "execution_time": 30,
                    "action_type": "maintenance_schedule"
                })
            if health_data["health_score"] < 85:
                actions.append({
                    "description": "Optimize heating schedule",
                    "success_probability": 0.8,
                    "execution_time": 5,
                    "action_type": "parameter_adjustment"
                })
        
        elif system_type == "Network":
            if health_data["health_score"] < 90:
                actions.append({
                    "description": "Restart router",
                    "success_probability": 0.7,
                    "execution_time": 3,
                    "action_type": "device_restart"
                })
                actions.append({
                    "description": "Optimize WiFi channels",
                    "success_probability": 0.6,
                    "execution_time": 10,
                    "action_type": "configuration_update"
                })
        
        elif system_type == "Water":
            if "pressure" in str(health_data["issues"]).lower():
                actions.append({
                    "description": "Adjust water pressure settings",
                    "success_probability": 0.8,
                    "execution_time": 15,
                    "action_type": "parameter_adjustment"
                })
        
        return actions
    
    def _execute_healing_action(self, system_id: int, action: Dict) -> bool:
        """Execute a specific healing action"""
        # This is a simulation - in real implementation, this would control actual devices
        import random
        
        action_type = action["action_type"]
        success_probability = action["success_probability"]
        
        # Simulate action execution
        time.sleep(1)  # Simulate execution time
        
        # Determine success based on probability
        success = random.random() < success_probability
        
        if success:
            logging.info(f"Healing action successful: {action['description']}")
        else:
            logging.warning(f"Healing action failed: {action['description']}")
        
        return success
    
    def _run_predictive_analysis(self):
        """Run predictive analysis for maintenance scheduling"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all systems for analysis
        cursor.execute('SELECT * FROM home_systems WHERE monitoring_enabled = 1')
        systems = cursor.fetchall()
        
        for system in systems:
            system_id = system[0]
            installation_date = system[12]
            expected_lifespan = system[13]
            health_score = system[7]
            
            if installation_date and expected_lifespan:
                # Calculate predicted failure date based on health degradation
                install_date = datetime.strptime(installation_date, '%Y-%m-%d')
                expected_end = install_date + timedelta(days=expected_lifespan * 365)
                
                # Adjust based on current health score
                health_factor = health_score / 100.0
                adjusted_lifespan = expected_lifespan * health_factor
                predicted_failure = install_date + timedelta(days=adjusted_lifespan * 365)
                
                # If failure is predicted within 6 months, create maintenance recommendation
                if predicted_failure < datetime.now() + timedelta(days=180):
                    confidence = max(0.6, 1.0 - (health_score / 100.0))
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO predictive_maintenance 
                        (system_id, prediction_type, predicted_failure_date, confidence_level,
                         recommended_action, estimated_cost, urgency_level)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        system_id, "component_failure", predicted_failure.date(),
                        confidence, "Schedule preventive maintenance",
                        system[14] * 0.1, 3  # 10% of replacement cost
                    ))
        
        conn.commit()
        conn.close()
    
    def _execute_scheduled_actions(self):
        """Execute scheduled automated actions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        current_time = datetime.now()
        
        # Get actions that are due for execution
        cursor.execute('''
            SELECT * FROM automated_actions 
            WHERE is_active = 1 AND (
                last_executed IS NULL OR 
                datetime(last_executed, '+' || schedule_value || ' ' || schedule_type) <= ?
            )
        ''', (current_time,))
        
        actions = cursor.fetchall()
        
        for action in actions:
            action_id = action[0]
            system_id = action[1]
            action_type = action[2]
            description = action[3]
            
            # Execute the action
            success = self._execute_automated_action(action_type, description)
            
            # Update execution record
            cursor.execute('''
                UPDATE automated_actions 
                SET last_executed = ?, execution_count = execution_count + 1
                WHERE id = ?
            ''', (current_time, action_id))
            
            # Update success rate
            if success:
                cursor.execute('''
                    UPDATE automated_actions 
                    SET success_rate = (success_rate * execution_count + 100) / (execution_count + 1)
                    WHERE id = ?
                ''', (action_id,))
        
        conn.commit()
        conn.close()
    
    def _execute_automated_action(self, action_type: str, description: str) -> bool:
        """Execute an automated action"""
        # Simulation of action execution
        import random
        
        success_rates = {
            "energy_optimization": 0.95,
            "security_check": 0.98,
            "backup_creation": 0.90,
            "system_update": 0.85,
            "resource_reorder": 0.99
        }
        
        success_rate = success_rates.get(action_type, 0.80)
        return random.random() < success_rate
    
    def _monitor_resources(self):
        """Monitor resource levels and trigger reorders if needed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM resource_management WHERE auto_reorder_enabled = 1')
        resources = cursor.fetchall()
        
        for resource in resources:
            resource_id = resource[0]
            resource_type = resource[1]
            current_level = resource[2]
            reorder_threshold = resource[9]
            reorder_quantity = resource[10]
            
            if current_level <= reorder_threshold:
                # Trigger automatic reorder
                self._trigger_resource_reorder(resource_id, resource_type, reorder_quantity)
        
        conn.close()
    
    def _trigger_resource_reorder(self, resource_id: int, resource_type: str, quantity: float):
        """Trigger automatic resource reordering"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update last reorder date and next delivery
        next_delivery = datetime.now() + timedelta(days=3)  # Assume 3-day delivery
        
        cursor.execute('''
            UPDATE resource_management 
            SET last_reorder_date = ?, next_delivery_date = ?
            WHERE id = ?
        ''', (datetime.now().date(), next_delivery.date(), resource_id))
        
        # Log the reorder action
        cursor.execute('''
            INSERT INTO automated_actions 
            (system_id, action_type, action_description, last_executed)
            VALUES (?, ?, ?, ?)
        ''', (
            None, "resource_reorder",
            f"Automatic reorder of {quantity} units of {resource_type}",
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
        
        logging.info(f"Triggered automatic reorder: {quantity} units of {resource_type}")
    
    def get_system_health_overview(self) -> Dict:
        """Get overall system health overview"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get system counts by status
        cursor.execute('''
            SELECT status, COUNT(*) FROM home_systems 
            GROUP BY status
        ''')
        status_counts = dict(cursor.fetchall())
        
        # Get average health score
        cursor.execute('SELECT AVG(health_score) FROM home_systems')
        avg_health = cursor.fetchone()[0] or 0
        
        # Get recent alerts
        cursor.execute('''
            SELECT COUNT(*) FROM system_alerts 
            WHERE created_at > datetime('now', '-24 hours')
        ''')
        recent_alerts = cursor.fetchone()[0]
        
        # Get critical systems status
        cursor.execute('''
            SELECT system_name, status, health_score FROM home_systems 
            WHERE is_critical = 1
        ''')
        critical_systems = cursor.fetchall()
        
        # Get upcoming maintenance
        cursor.execute('''
            SELECT COUNT(*) FROM predictive_maintenance 
            WHERE predicted_failure_date <= date('now', '+30 days')
        ''')
        upcoming_maintenance = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "overall_health": round(avg_health, 1),
            "system_status_counts": status_counts,
            "recent_alerts_24h": recent_alerts,
            "critical_systems": [
                {
                    "name": sys[0],
                    "status": sys[1],
                    "health_score": sys[2]
                } for sys in critical_systems
            ],
            "upcoming_maintenance_30d": upcoming_maintenance,
            "monitoring_active": self.monitoring_active
        }
    
    def get_energy_optimization_suggestions(self) -> List[Dict]:
        """Get energy optimization suggestions based on current usage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get systems with high energy consumption
        cursor.execute('''
            SELECT system_name, energy_consumption_watts, health_score 
            FROM home_systems 
            WHERE energy_consumption_watts > 100
            ORDER BY energy_consumption_watts DESC
        ''')
        
        high_consumption_systems = cursor.fetchall()
        conn.close()
        
        suggestions = []
        
        for system in high_consumption_systems:
            name, consumption, health = system
            
            if health < 90:
                suggestions.append({
                    "system": name,
                    "suggestion": "Optimize system performance to reduce energy consumption",
                    "potential_savings_watts": consumption * 0.15,
                    "potential_savings_monthly": consumption * 0.15 * 24 * 30 * 0.28 / 1000,
                    "implementation": "Schedule maintenance and performance tuning"
                })
            
            if consumption > 1000:
                suggestions.append({
                    "system": name,
                    "suggestion": "Consider upgrading to more energy-efficient model",
                    "potential_savings_watts": consumption * 0.30,
                    "potential_savings_monthly": consumption * 0.30 * 24 * 30 * 0.28 / 1000,
                    "implementation": "Research and plan system upgrade"
                })
        
        return suggestions
    
    def create_automated_action(self, system_name: str, action_type: str,
                              description: str, schedule_type: str,
                              schedule_value: str, priority: int = 2) -> int:
        """Create a new automated action"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get system ID
        cursor.execute('SELECT id FROM home_systems WHERE system_name = ?', (system_name,))
        system_result = cursor.fetchone()
        
        if not system_result:
            conn.close()
            raise ValueError(f"System '{system_name}' not found")
        
        system_id = system_result[0]
        
        cursor.execute('''
            INSERT INTO automated_actions 
            (system_id, action_type, action_description, schedule_type, schedule_value, priority)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (system_id, action_type, description, schedule_type, schedule_value, priority))
        
        action_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return action_id
    
    def get_maintenance_calendar(self, days_ahead: int = 30) -> List[Dict]:
        """Get maintenance calendar for the next specified days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        end_date = datetime.now() + timedelta(days=days_ahead)
        
        cursor.execute('''
            SELECT pm.*, hs.system_name 
            FROM predictive_maintenance pm
            JOIN home_systems hs ON pm.system_id = hs.id
            WHERE pm.predicted_failure_date <= ? AND pm.action_taken = 0
            ORDER BY pm.predicted_failure_date, pm.urgency_level DESC
        ''', (end_date.date(),))
        
        maintenance_items = cursor.fetchall()
        conn.close()
        
        calendar = []
        for item in maintenance_items:
            calendar.append({
                "date": item[3],  # predicted_failure_date
                "system": item[11],  # system_name
                "action": item[5],  # recommended_action
                "urgency": item[7],  # urgency_level
                "estimated_cost": item[6],  # estimated_cost
                "confidence": item[4],  # confidence_level
                "parts_needed": item[8] if item[8] else "TBD"
            })
        
        return calendar
    
    def simulate_london_weather_integration(self) -> Dict:
        """Simulate integration with London weather for home optimization"""
        # Mock London weather data
        weather_data = {
            "temperature": 12.5,
            "humidity": 78,
            "pressure": 1013.2,
            "wind_speed": 15.3,
            "conditions": "overcast",
            "forecast_24h": [
                {"hour": 0, "temp": 11, "rain_probability": 20},
                {"hour": 6, "temp": 9, "rain_probability": 40},
                {"hour": 12, "temp": 14, "rain_probability": 60},
                {"hour": 18, "temp": 13, "rain_probability": 30}
            ]
        }
        
        # Generate optimization suggestions based on weather
        optimizations = []
        
        if weather_data["temperature"] < 15:
            optimizations.append({
                "system": "Central Heating",
                "action": "Increase heating schedule efficiency",
                "reason": "Cold weather expected",
                "energy_impact": "10% increase expected"
            })
        
        if weather_data["humidity"] > 70:
            optimizations.append({
                "system": "Ventilation",
                "action": "Increase ventilation to reduce humidity",
                "reason": "High humidity detected",
                "energy_impact": "5% increase in fan usage"
            })
        
        if any(h["rain_probability"] > 50 for h in weather_data["forecast_24h"]):
            optimizations.append({
                "system": "Garden Irrigation",
                "action": "Skip scheduled watering",
                "reason": "Rain expected",
                "energy_impact": "Water and energy savings"
            })
        
        return {
            "current_weather": weather_data,
            "optimizations": optimizations,
            "last_updated": datetime.now().isoformat()
        }

