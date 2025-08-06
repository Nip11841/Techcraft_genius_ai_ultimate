from flask import Blueprint, jsonify, request
from src.models.project import db, Project
import json

projects_bp = Blueprint('projects', __name__)

# Sample project data to populate the database
SAMPLE_PROJECTS = [
    {
        'title': 'Smart Home Security System',
        'description': 'Build an AI-powered security system with facial recognition and mobile alerts. This comprehensive project includes camera integration, motion detection, and real-time notifications.',
        'difficulty': 'Intermediate',
        'cost': 150.0,
        'duration': '2-3 days',
        'category': 'Security',
        'tags': ['AI', 'IoT', 'Security', 'Raspberry Pi'],
        'rating': 4.8,
        'views': 1250,
        'likes': 89,
        'components': ['Raspberry Pi 4', 'Camera Module', 'PIR Sensor', 'Buzzer', 'SD Card', 'Power Supply'],
        'skills': ['Python', 'OpenCV', 'Electronics', 'Linux'],
        'code_content': '''
# Smart Home Security System - Main Code
import cv2
import numpy as np
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

class SecuritySystem:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
    def detect_motion(self):
        ret, frame = self.camera.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            return len(faces) > 0
        return False
        
    def send_alert(self, message):
        # Send email alert
        print(f"ALERT: {message} at {datetime.now()}")
        
    def run(self):
        while True:
            if self.detect_motion():
                self.send_alert("Motion detected!")
                
if __name__ == "__main__":
    system = SecuritySystem()
    system.run()
        ''',
        'instructions': '''
Step 1: Hardware Setup
- Connect Raspberry Pi Camera Module to CSI port
- Connect PIR sensor to GPIO pin 18
- Connect buzzer to GPIO pin 12
- Ensure all connections are secure

Step 2: Software Installation
- Install OpenCV: pip install opencv-python
- Install required libraries: pip install numpy smtplib

Step 3: Configuration
- Enable camera interface in raspi-config
- Configure email settings for alerts
- Test camera functionality

Step 4: Deployment
- Run the main script
- Monitor system logs
- Set up automatic startup on boot
        '''
    },
    {
        'title': 'Autonomous Flying Robot',
        'description': 'Create a self-navigating drone with obstacle avoidance and GPS tracking. Features advanced flight control algorithms and real-time path planning.',
        'difficulty': 'Advanced',
        'cost': 300.0,
        'duration': '1 week',
        'category': 'Robotics',
        'tags': ['Drone', 'AI', 'GPS', 'Sensors', 'Flight Control'],
        'rating': 4.9,
        'views': 2100,
        'likes': 156,
        'components': ['Flight Controller', 'GPS Module', 'Ultrasonic Sensors', 'Camera', 'ESCs', 'Motors', 'Propellers', 'Battery'],
        'skills': ['C++', 'Flight Control', 'Electronics', 'PID Control'],
        'code_content': '''
// Autonomous Flying Robot - Flight Controller Code
#include <Servo.h>
#include <SoftwareSerial.h>

class FlightController {
private:
    Servo motor1, motor2, motor3, motor4;
    float pitch, roll, yaw;
    float target_altitude;
    
public:
    void initialize() {
        motor1.attach(3);
        motor2.attach(5);
        motor3.attach(6);
        motor4.attach(9);
        
        // Initialize sensors
        Serial.begin(9600);
        Serial.println("Flight Controller Initialized");
    }
    
    void readSensors() {
        // Read IMU data
        // Read GPS data
        // Read ultrasonic sensors
    }
    
    void calculatePID() {
        // PID control for stability
        float error_pitch = 0 - pitch;
        float error_roll = 0 - roll;
        
        // Apply PID corrections
    }
    
    void updateMotors() {
        // Update motor speeds based on PID output
        motor1.writeMicroseconds(1500);
        motor2.writeMicroseconds(1500);
        motor3.writeMicroseconds(1500);
        motor4.writeMicroseconds(1500);
    }
    
    void autonomousNavigation() {
        // Implement obstacle avoidance
        // GPS waypoint navigation
        // Path planning algorithms
    }
};

FlightController drone;

void setup() {
    drone.initialize();
}

void loop() {
    drone.readSensors();
    drone.calculatePID();
    drone.updateMotors();
    drone.autonomousNavigation();
    delay(20);
}
        ''',
        'instructions': '''
Step 1: Frame Assembly
- Assemble quadcopter frame
- Mount flight controller in center
- Install motors and ESCs
- Balance propellers

Step 2: Electronics Integration
- Connect GPS module to UART
- Install ultrasonic sensors for obstacle detection
- Connect camera for FPV
- Wire power distribution

Step 3: Software Configuration
- Flash flight controller firmware
- Calibrate IMU and compass
- Configure GPS settings
- Test motor responses

Step 4: Flight Testing
- Start with manual control
- Test autonomous hover
- Implement waypoint navigation
- Add obstacle avoidance
        '''
    },
    {
        'title': 'Voice-Controlled LED Matrix',
        'description': 'Build a smart LED display that responds to voice commands and shows animations. Perfect for beginners learning Arduino and voice recognition.',
        'difficulty': 'Beginner',
        'cost': 75.0,
        'duration': '1 day',
        'category': 'Display',
        'tags': ['Voice Control', 'LED', 'Arduino', 'Audio', 'Display'],
        'rating': 4.6,
        'views': 890,
        'likes': 67,
        'components': ['Arduino Uno', 'LED Matrix 8x8', 'Microphone Module', 'Speaker', 'Jumper Wires', 'Breadboard'],
        'skills': ['Arduino', 'Basic Electronics', 'C Programming'],
        'code_content': '''
// Voice-Controlled LED Matrix
#include <LedControl.h>

LedControl lc = LedControl(12, 11, 10, 1);
int micPin = A0;
int threshold = 512;

// LED patterns
byte heart[8] = {
  B00000000,
  B01100110,
  B11111111,
  B11111111,
  B01111110,
  B00111100,
  B00011000,
  B00000000
};

byte smile[8] = {
  B00111100,
  B01000010,
  B10100101,
  B10000001,
  B10100101,
  B10011001,
  B01000010,
  B00111100
};

void setup() {
  Serial.begin(9600);
  lc.shutdown(0, false);
  lc.setIntensity(0, 8);
  lc.clearDisplay(0);
  
  Serial.println("Voice LED Matrix Ready!");
}

void loop() {
  int soundLevel = analogRead(micPin);
  
  if (soundLevel > threshold) {
    Serial.println("Voice detected!");
    
    // Simple voice pattern recognition
    if (soundLevel > 600) {
      displayPattern(heart);
      Serial.println("Showing heart pattern");
    } else {
      displayPattern(smile);
      Serial.println("Showing smile pattern");
    }
    
    delay(2000);
    lc.clearDisplay(0);
  }
  
  delay(100);
}

void displayPattern(byte pattern[]) {
  for (int row = 0; row < 8; row++) {
    lc.setRow(0, row, pattern[row]);
  }
}

void scrollText(String text) {
  // Implement text scrolling
  for (int i = 0; i < text.length(); i++) {
    // Display character by character
    delay(500);
  }
}
        ''',
        'instructions': '''
Step 1: Circuit Assembly
- Connect LED Matrix to Arduino (DIN=12, CS=10, CLK=11)
- Connect microphone module to analog pin A0
- Connect speaker to digital pin 8
- Add pull-up resistors as needed

Step 2: Library Installation
- Install LedControl library in Arduino IDE
- Install any additional audio libraries
- Verify all connections

Step 3: Code Upload
- Upload the provided code to Arduino
- Open Serial Monitor to see debug output
- Test microphone sensitivity

Step 4: Calibration
- Adjust threshold value for voice detection
- Test different voice commands
- Add more patterns and animations
- Experiment with sound-reactive effects
        '''
    }
]

@projects_bp.route('/projects', methods=['GET'])
def get_projects():
    """Get all projects with optional filtering"""
    try:
        # Initialize database with sample data if empty
        if Project.query.count() == 0:
            for project_data in SAMPLE_PROJECTS:
                project = Project(
                    title=project_data['title'],
                    description=project_data['description'],
                    difficulty=project_data['difficulty'],
                    cost=project_data['cost'],
                    duration=project_data['duration'],
                    category=project_data['category'],
                    tags=json.dumps(project_data['tags']),
                    rating=project_data['rating'],
                    views=project_data['views'],
                    likes=project_data['likes'],
                    components=json.dumps(project_data['components']),
                    skills=json.dumps(project_data['skills']),
                    code_content=project_data['code_content'],
                    instructions=project_data['instructions']
                )
                db.session.add(project)
            db.session.commit()
        
        # Get query parameters for filtering
        difficulty = request.args.get('difficulty')
        category = request.args.get('category')
        min_cost = request.args.get('min_cost', type=float)
        max_cost = request.args.get('max_cost', type=float)
        search = request.args.get('search')
        
        # Build query
        query = Project.query
        
        if difficulty:
            query = query.filter(Project.difficulty.ilike(f'%{difficulty}%'))
        if category:
            query = query.filter(Project.category.ilike(f'%{category}%'))
        if min_cost is not None:
            query = query.filter(Project.cost >= min_cost)
        if max_cost is not None:
            query = query.filter(Project.cost <= max_cost)
        if search:
            query = query.filter(
                db.or_(
                    Project.title.ilike(f'%{search}%'),
                    Project.description.ilike(f'%{search}%'),
                    Project.tags.ilike(f'%{search}%')
                )
            )
        
        projects = query.all()
        return jsonify([project.to_dict() for project in projects])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """Get a specific project by ID"""
    try:
        project = Project.query.get_or_404(project_id)
        
        # Increment view count
        project.views += 1
        db.session.commit()
        
        return jsonify(project.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/projects/<int:project_id>/like', methods=['POST'])
def like_project(project_id):
    """Like a project"""
    try:
        project = Project.query.get_or_404(project_id)
        project.likes += 1
        db.session.commit()
        
        return jsonify({'likes': project.likes})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/projects/categories', methods=['GET'])
def get_categories():
    """Get all available project categories"""
    try:
        categories = db.session.query(Project.category).distinct().all()
        return jsonify([cat[0] for cat in categories])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/projects/stats', methods=['GET'])
def get_project_stats():
    """Get project statistics"""
    try:
        total_projects = Project.query.count()
        total_views = db.session.query(db.func.sum(Project.views)).scalar() or 0
        total_likes = db.session.query(db.func.sum(Project.likes)).scalar() or 0
        avg_rating = db.session.query(db.func.avg(Project.rating)).scalar() or 0
        
        return jsonify({
            'total_projects': total_projects,
            'total_views': total_views,
            'total_likes': total_likes,
            'average_rating': round(avg_rating, 2)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

