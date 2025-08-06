"""
IoT Integration and Device Control System
Manages smart home devices and automation rules for TechCraft Genius AI
"""

import json
import time
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import threading
import schedule

class DeviceType(Enum):
    LIGHT = "light"
    THERMOSTAT = "thermostat"
    CAMERA = "camera"
    SENSOR = "sensor"
    SWITCH = "switch"
    PLUG = "plug"
    LOCK = "lock"
    SPEAKER = "speaker"
    DISPLAY = "display"
    VACUUM = "vacuum"

class DeviceStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    UPDATING = "updating"

@dataclass
class SmartDevice:
    id: str
    name: str
    device_type: DeviceType
    brand: str
    model: str
    ip_address: str
    mac_address: str
    room: str
    status: DeviceStatus
    capabilities: List[str]
    current_state: Dict[str, Any]
    last_seen: datetime
    energy_usage: float  # watts
    automation_potential: str
    setup_instructions: str

@dataclass
class AutomationRule:
    id: str
    name: str
    description: str
    trigger_type: str  # time, sensor, manual, weather
    trigger_conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    enabled: bool
    created_date: datetime
    last_executed: Optional[datetime]
    execution_count: int

@dataclass
class EnergyData:
    device_id: str
    timestamp: datetime
    power_consumption: float  # watts
    daily_cost: float  # pounds
    efficiency_score: float  # 0-100

class IoTController:
    def __init__(self, db_path: str = "iot_devices.db"):
        self.db_path = db_path
        self.devices: Dict[str, SmartDevice] = {}
        self.automation_rules: Dict[str, AutomationRule] = {}
        self.energy_data: List[EnergyData] = []
        self.init_database()
        self.load_devices()
        self.load_automation_rules()
        self.start_automation_scheduler()
    
    def init_database(self):
        """Initialize SQLite database for IoT devices and automation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                device_type TEXT NOT NULL,
                brand TEXT,
                model TEXT,
                ip_address TEXT,
                mac_address TEXT,
                room TEXT,
                status TEXT,
                capabilities TEXT,
                current_state TEXT,
                last_seen TIMESTAMP,
                energy_usage REAL,
                automation_potential TEXT,
                setup_instructions TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS automation_rules (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                trigger_type TEXT,
                trigger_conditions TEXT,
                actions TEXT,
                enabled BOOLEAN,
                created_date TIMESTAMP,
                last_executed TIMESTAMP,
                execution_count INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS energy_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT,
                timestamp TIMESTAMP,
                power_consumption REAL,
                daily_cost REAL,
                efficiency_score REAL,
                FOREIGN KEY (device_id) REFERENCES devices (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def discover_devices(self) -> List[SmartDevice]:
        """Discover smart devices on the network"""
        discovered_devices = []
        
        # Simulate device discovery with common smart home devices
        sample_devices = [
            {
                'id': 'philips_hue_001',
                'name': 'Living Room Light',
                'device_type': DeviceType.LIGHT,
                'brand': 'Philips',
                'model': 'Hue White',
                'ip_address': '192.168.1.100',
                'mac_address': '00:17:88:01:02:03',
                'room': 'Living Room',
                'capabilities': ['brightness', 'color_temperature', 'scheduling'],
                'current_state': {'on': True, 'brightness': 80, 'color_temp': 3000},
                'energy_usage': 9.5,
                'automation_potential': 'High - Motion sensing, scheduling, mood lighting',
                'setup_instructions': 'Connect to Philips Hue Bridge, use Hue app for initial setup'
            },
            {
                'id': 'nest_thermostat_001',
                'name': 'Main Thermostat',
                'device_type': DeviceType.THERMOSTAT,
                'brand': 'Google',
                'model': 'Nest Learning Thermostat',
                'ip_address': '192.168.1.101',
                'mac_address': '00:17:88:01:02:04',
                'room': 'Hallway',
                'capabilities': ['temperature_control', 'scheduling', 'learning', 'geofencing'],
                'current_state': {'temperature': 21, 'target': 22, 'mode': 'heat'},
                'energy_usage': 3.5,
                'automation_potential': 'Very High - Learning patterns, weather integration, presence detection',
                'setup_instructions': 'Install on wall, connect to WiFi via Nest app, set up schedules'
            },
            {
                'id': 'ring_doorbell_001',
                'name': 'Front Door Camera',
                'device_type': DeviceType.CAMERA,
                'brand': 'Ring',
                'model': 'Video Doorbell Pro',
                'ip_address': '192.168.1.102',
                'mac_address': '00:17:88:01:02:05',
                'room': 'Front Door',
                'capabilities': ['video_recording', 'motion_detection', 'two_way_audio', 'night_vision'],
                'current_state': {'recording': True, 'motion_alerts': True, 'battery': 85},
                'energy_usage': 4.2,
                'automation_potential': 'High - Motion alerts, visitor recognition, package detection',
                'setup_instructions': 'Mount on door frame, connect to Ring app, set motion zones'
            },
            {
                'id': 'amazon_echo_001',
                'name': 'Kitchen Echo',
                'device_type': DeviceType.SPEAKER,
                'brand': 'Amazon',
                'model': 'Echo Dot (4th Gen)',
                'ip_address': '192.168.1.103',
                'mac_address': '00:17:88:01:02:06',
                'room': 'Kitchen',
                'capabilities': ['voice_control', 'music_streaming', 'smart_home_hub', 'timers'],
                'current_state': {'volume': 6, 'muted': False, 'playing': False},
                'energy_usage': 2.1,
                'automation_potential': 'Very High - Voice control hub, routine automation, announcements',
                'setup_instructions': 'Plug in, use Alexa app to connect WiFi and set up skills'
            },
            {
                'id': 'tp_link_plug_001',
                'name': 'Coffee Machine Plug',
                'device_type': DeviceType.PLUG,
                'brand': 'TP-Link',
                'model': 'Kasa Smart Plug',
                'ip_address': '192.168.1.104',
                'mac_address': '00:17:88:01:02:07',
                'room': 'Kitchen',
                'capabilities': ['remote_control', 'scheduling', 'energy_monitoring', 'voice_control'],
                'current_state': {'on': False, 'power': 0, 'today_usage': 0.8},
                'energy_usage': 0.5,
                'automation_potential': 'Medium - Schedule coffee brewing, energy monitoring',
                'setup_instructions': 'Plug in, use Kasa app to connect WiFi and set schedules'
            }
        ]
        
        for device_data in sample_devices:
            device = SmartDevice(
                id=device_data['id'],
                name=device_data['name'],
                device_type=device_data['device_type'],
                brand=device_data['brand'],
                model=device_data['model'],
                ip_address=device_data['ip_address'],
                mac_address=device_data['mac_address'],
                room=device_data['room'],
                status=DeviceStatus.ONLINE,
                capabilities=device_data['capabilities'],
                current_state=device_data['current_state'],
                last_seen=datetime.now(),
                energy_usage=device_data['energy_usage'],
                automation_potential=device_data['automation_potential'],
                setup_instructions=device_data['setup_instructions']
            )
            discovered_devices.append(device)
        
        return discovered_devices
    
    def add_device(self, device: SmartDevice) -> bool:
        """Add a new device to the system"""
        try:
            self.devices[device.id] = device
            self.save_device(device)
            logging.info(f"Added device: {device.name} ({device.id})")
            return True
        except Exception as e:
            logging.error(f"Error adding device {device.id}: {e}")
            return False
    
    def save_device(self, device: SmartDevice):
        """Save device to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO devices 
            (id, name, device_type, brand, model, ip_address, mac_address, room, 
             status, capabilities, current_state, last_seen, energy_usage, 
             automation_potential, setup_instructions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            device.id, device.name, device.device_type.value, device.brand, device.model,
            device.ip_address, device.mac_address, device.room, device.status.value,
            json.dumps(device.capabilities), json.dumps(device.current_state),
            device.last_seen, device.energy_usage, device.automation_potential,
            device.setup_instructions
        ))
        
        conn.commit()
        conn.close()
    
    def load_devices(self):
        """Load devices from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM devices')
        rows = cursor.fetchall()
        
        for row in rows:
            device = SmartDevice(
                id=row[0],
                name=row[1],
                device_type=DeviceType(row[2]),
                brand=row[3],
                model=row[4],
                ip_address=row[5],
                mac_address=row[6],
                room=row[7],
                status=DeviceStatus(row[8]),
                capabilities=json.loads(row[9]) if row[9] else [],
                current_state=json.loads(row[10]) if row[10] else {},
                last_seen=datetime.fromisoformat(row[11]) if row[11] else datetime.now(),
                energy_usage=row[12] or 0.0,
                automation_potential=row[13] or "",
                setup_instructions=row[14] or ""
            )
            self.devices[device.id] = device
        
        conn.close()
        logging.info(f"Loaded {len(self.devices)} devices from database")
    
    def control_device(self, device_id: str, action: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Control a smart device"""
        if device_id not in self.devices:
            return {'error': f'Device {device_id} not found'}
        
        device = self.devices[device_id]
        parameters = parameters or {}
        
        try:
            # Simulate device control based on device type and action
            if device.device_type == DeviceType.LIGHT:
                return self._control_light(device, action, parameters)
            elif device.device_type == DeviceType.THERMOSTAT:
                return self._control_thermostat(device, action, parameters)
            elif device.device_type == DeviceType.PLUG:
                return self._control_plug(device, action, parameters)
            elif device.device_type == DeviceType.CAMERA:
                return self._control_camera(device, action, parameters)
            else:
                return {'error': f'Device type {device.device_type} not supported'}
        
        except Exception as e:
            logging.error(f"Error controlling device {device_id}: {e}")
            return {'error': str(e)}
    
    def _control_light(self, device: SmartDevice, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Control light device"""
        if action == 'turn_on':
            device.current_state['on'] = True
            brightness = parameters.get('brightness', device.current_state.get('brightness', 100))
            device.current_state['brightness'] = brightness
            device.energy_usage = device.energy_usage * (brightness / 100)
            return {'success': True, 'state': device.current_state}
        
        elif action == 'turn_off':
            device.current_state['on'] = False
            device.energy_usage = 0.5  # Standby power
            return {'success': True, 'state': device.current_state}
        
        elif action == 'set_brightness':
            brightness = parameters.get('brightness', 50)
            device.current_state['brightness'] = max(0, min(100, brightness))
            if device.current_state.get('on', False):
                device.energy_usage = 9.5 * (brightness / 100)
            return {'success': True, 'state': device.current_state}
        
        elif action == 'set_color_temperature':
            color_temp = parameters.get('color_temperature', 3000)
            device.current_state['color_temp'] = max(2000, min(6500, color_temp))
            return {'success': True, 'state': device.current_state}
        
        else:
            return {'error': f'Unknown action: {action}'}
    
    def _control_thermostat(self, device: SmartDevice, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Control thermostat device"""
        if action == 'set_temperature':
            target_temp = parameters.get('temperature', 20)
            device.current_state['target'] = max(10, min(30, target_temp))
            device.current_state['mode'] = parameters.get('mode', 'heat')
            return {'success': True, 'state': device.current_state}
        
        elif action == 'set_mode':
            mode = parameters.get('mode', 'heat')
            if mode in ['heat', 'cool', 'auto', 'off']:
                device.current_state['mode'] = mode
                return {'success': True, 'state': device.current_state}
            else:
                return {'error': f'Invalid mode: {mode}'}
        
        elif action == 'get_temperature':
            return {'success': True, 'temperature': device.current_state.get('temperature', 20)}
        
        else:
            return {'error': f'Unknown action: {action}'}
    
    def _control_plug(self, device: SmartDevice, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Control smart plug device"""
        if action == 'turn_on':
            device.current_state['on'] = True
            device.current_state['power'] = parameters.get('power', 100)  # Watts
            device.energy_usage = device.current_state['power']
            return {'success': True, 'state': device.current_state}
        
        elif action == 'turn_off':
            device.current_state['on'] = False
            device.current_state['power'] = 0
            device.energy_usage = 0.5  # Standby power
            return {'success': True, 'state': device.current_state}
        
        elif action == 'get_energy_usage':
            return {
                'success': True, 
                'current_power': device.current_state.get('power', 0),
                'today_usage': device.current_state.get('today_usage', 0)
            }
        
        else:
            return {'error': f'Unknown action: {action}'}
    
    def _control_camera(self, device: SmartDevice, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Control camera device"""
        if action == 'start_recording':
            device.current_state['recording'] = True
            return {'success': True, 'state': device.current_state}
        
        elif action == 'stop_recording':
            device.current_state['recording'] = False
            return {'success': True, 'state': device.current_state}
        
        elif action == 'enable_motion_alerts':
            device.current_state['motion_alerts'] = True
            return {'success': True, 'state': device.current_state}
        
        elif action == 'disable_motion_alerts':
            device.current_state['motion_alerts'] = False
            return {'success': True, 'state': device.current_state}
        
        else:
            return {'error': f'Unknown action: {action}'}
    
    def create_automation_rule(self, rule: AutomationRule) -> bool:
        """Create a new automation rule"""
        try:
            self.automation_rules[rule.id] = rule
            self.save_automation_rule(rule)
            logging.info(f"Created automation rule: {rule.name}")
            return True
        except Exception as e:
            logging.error(f"Error creating automation rule {rule.id}: {e}")
            return False
    
    def save_automation_rule(self, rule: AutomationRule):
        """Save automation rule to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO automation_rules 
            (id, name, description, trigger_type, trigger_conditions, actions, 
             enabled, created_date, last_executed, execution_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            rule.id, rule.name, rule.description, rule.trigger_type,
            json.dumps(rule.trigger_conditions), json.dumps(rule.actions),
            rule.enabled, rule.created_date, rule.last_executed, rule.execution_count
        ))
        
        conn.commit()
        conn.close()
    
    def load_automation_rules(self):
        """Load automation rules from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM automation_rules')
        rows = cursor.fetchall()
        
        for row in rows:
            rule = AutomationRule(
                id=row[0],
                name=row[1],
                description=row[2],
                trigger_type=row[3],
                trigger_conditions=json.loads(row[4]) if row[4] else {},
                actions=json.loads(row[5]) if row[5] else [],
                enabled=bool(row[6]),
                created_date=datetime.fromisoformat(row[7]) if row[7] else datetime.now(),
                last_executed=datetime.fromisoformat(row[8]) if row[8] else None,
                execution_count=row[9] or 0
            )
            self.automation_rules[rule.id] = rule
        
        conn.close()
        logging.info(f"Loaded {len(self.automation_rules)} automation rules from database")
    
    def execute_automation_rule(self, rule_id: str) -> Dict[str, Any]:
        """Execute an automation rule"""
        if rule_id not in self.automation_rules:
            return {'error': f'Automation rule {rule_id} not found'}
        
        rule = self.automation_rules[rule_id]
        if not rule.enabled:
            return {'error': f'Automation rule {rule_id} is disabled'}
        
        try:
            results = []
            for action in rule.actions:
                device_id = action.get('device_id')
                action_type = action.get('action')
                parameters = action.get('parameters', {})
                
                if device_id and action_type:
                    result = self.control_device(device_id, action_type, parameters)
                    results.append({
                        'device_id': device_id,
                        'action': action_type,
                        'result': result
                    })
            
            # Update rule execution stats
            rule.last_executed = datetime.now()
            rule.execution_count += 1
            self.save_automation_rule(rule)
            
            return {'success': True, 'results': results}
        
        except Exception as e:
            logging.error(f"Error executing automation rule {rule_id}: {e}")
            return {'error': str(e)}
    
    def start_automation_scheduler(self):
        """Start the automation scheduler"""
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(1)
        
        # Schedule automation checks
        schedule.every(1).minutes.do(self.check_time_based_automations)
        schedule.every(5).minutes.do(self.check_sensor_based_automations)
        schedule.every(1).hours.do(self.update_energy_data)
        
        # Start scheduler in background thread
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        logging.info("Automation scheduler started")
    
    def check_time_based_automations(self):
        """Check and execute time-based automation rules"""
        current_time = datetime.now()
        
        for rule in self.automation_rules.values():
            if not rule.enabled or rule.trigger_type != 'time':
                continue
            
            trigger_time = rule.trigger_conditions.get('time')
            if trigger_time:
                # Simple time matching (would be more sophisticated in real implementation)
                if current_time.strftime('%H:%M') == trigger_time:
                    self.execute_automation_rule(rule.id)
    
    def check_sensor_based_automations(self):
        """Check and execute sensor-based automation rules"""
        for rule in self.automation_rules.values():
            if not rule.enabled or rule.trigger_type != 'sensor':
                continue
            
            # Check sensor conditions (simplified)
            sensor_id = rule.trigger_conditions.get('sensor_id')
            threshold = rule.trigger_conditions.get('threshold')
            condition = rule.trigger_conditions.get('condition')  # 'above', 'below', 'equals'
            
            if sensor_id and sensor_id in self.devices:
                sensor_device = self.devices[sensor_id]
                sensor_value = sensor_device.current_state.get('value', 0)
                
                should_trigger = False
                if condition == 'above' and sensor_value > threshold:
                    should_trigger = True
                elif condition == 'below' and sensor_value < threshold:
                    should_trigger = True
                elif condition == 'equals' and sensor_value == threshold:
                    should_trigger = True
                
                if should_trigger:
                    self.execute_automation_rule(rule.id)
    
    def update_energy_data(self):
        """Update energy consumption data for all devices"""
        current_time = datetime.now()
        
        for device in self.devices.values():
            if device.status == DeviceStatus.ONLINE:
                # Calculate daily cost (UK average: £0.28 per kWh)
                daily_cost = (device.energy_usage / 1000) * 24 * 0.28
                
                # Calculate efficiency score (simplified)
                efficiency_score = max(0, 100 - (device.energy_usage / 10))
                
                energy_data = EnergyData(
                    device_id=device.id,
                    timestamp=current_time,
                    power_consumption=device.energy_usage,
                    daily_cost=daily_cost,
                    efficiency_score=efficiency_score
                )
                
                self.energy_data.append(energy_data)
                self.save_energy_data(energy_data)
    
    def save_energy_data(self, energy_data: EnergyData):
        """Save energy data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO energy_data 
            (device_id, timestamp, power_consumption, daily_cost, efficiency_score)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            energy_data.device_id, energy_data.timestamp, energy_data.power_consumption,
            energy_data.daily_cost, energy_data.efficiency_score
        ))
        
        conn.commit()
        conn.close()
    
    def get_device_status(self) -> Dict[str, Any]:
        """Get status of all devices"""
        return {
            'total_devices': len(self.devices),
            'online_devices': len([d for d in self.devices.values() if d.status == DeviceStatus.ONLINE]),
            'offline_devices': len([d for d in self.devices.values() if d.status == DeviceStatus.OFFLINE]),
            'total_energy_usage': sum(d.energy_usage for d in self.devices.values()),
            'devices': [asdict(device) for device in self.devices.values()]
        }
    
    def get_automation_status(self) -> Dict[str, Any]:
        """Get status of all automation rules"""
        return {
            'total_rules': len(self.automation_rules),
            'enabled_rules': len([r for r in self.automation_rules.values() if r.enabled]),
            'total_executions': sum(r.execution_count for r in self.automation_rules.values()),
            'rules': [asdict(rule) for rule in self.automation_rules.values()]
        }
    
    def get_energy_report(self, days: int = 7) -> Dict[str, Any]:
        """Get energy consumption report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
            SELECT device_id, AVG(power_consumption), AVG(daily_cost), AVG(efficiency_score)
            FROM energy_data 
            WHERE timestamp >= ?
            GROUP BY device_id
        ''', (start_date,))
        
        results = cursor.fetchall()
        conn.close()
        
        device_reports = []
        total_cost = 0
        
        for row in results:
            device_id, avg_power, avg_cost, avg_efficiency = row
            device_name = self.devices.get(device_id, {}).name if device_id in self.devices else device_id
            
            device_reports.append({
                'device_id': device_id,
                'device_name': device_name,
                'average_power': round(avg_power, 2),
                'average_daily_cost': round(avg_cost, 2),
                'efficiency_score': round(avg_efficiency, 1)
            })
            
            total_cost += avg_cost
        
        return {
            'period_days': days,
            'total_estimated_daily_cost': round(total_cost, 2),
            'total_estimated_monthly_cost': round(total_cost * 30, 2),
            'device_reports': device_reports
        }


# Global IoT controller instance
iot_controller = IoTController()

def initialize_sample_devices():
    """Initialize with sample devices for demonstration"""
    discovered_devices = iot_controller.discover_devices()
    
    for device in discovered_devices:
        iot_controller.add_device(device)
    
    # Create sample automation rules
    sample_rules = [
        AutomationRule(
            id='morning_routine',
            name='Morning Routine',
            description='Turn on lights and start coffee at 7 AM',
            trigger_type='time',
            trigger_conditions={'time': '07:00'},
            actions=[
                {'device_id': 'philips_hue_001', 'action': 'turn_on', 'parameters': {'brightness': 80}},
                {'device_id': 'tp_link_plug_001', 'action': 'turn_on', 'parameters': {}}
            ],
            enabled=True,
            created_date=datetime.now(),
            last_executed=None,
            execution_count=0
        ),
        AutomationRule(
            id='energy_saver',
            name='Energy Saver',
            description='Turn off lights when no motion detected for 30 minutes',
            trigger_type='sensor',
            trigger_conditions={'sensor_id': 'motion_sensor_001', 'condition': 'below', 'threshold': 1},
            actions=[
                {'device_id': 'philips_hue_001', 'action': 'turn_off', 'parameters': {}}
            ],
            enabled=True,
            created_date=datetime.now(),
            last_executed=None,
            execution_count=0
        )
    ]
    
    for rule in sample_rules:
        iot_controller.create_automation_rule(rule)
    
    logging.info("Sample devices and automation rules initialized")

if __name__ == "__main__":
    # Initialize sample devices and rules
    initialize_sample_devices()
    
    # Example usage
    print("IoT Controller initialized")
    print(f"Device status: {iot_controller.get_device_status()}")
    print(f"Automation status: {iot_controller.get_automation_status()}")
    
    # Test device control
    result = iot_controller.control_device('philips_hue_001', 'turn_on', {'brightness': 50})
    print(f"Light control result: {result}")
    
    # Test automation execution
    result = iot_controller.execute_automation_rule('morning_routine')
    print(f"Automation execution result: {result}")

