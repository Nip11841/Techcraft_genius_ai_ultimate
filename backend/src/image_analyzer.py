"""
Computer Vision and Image Analysis System
Analyzes uploaded images for home automation planning and device recognition
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import base64
import io
import json
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import requests
from datetime import datetime

@dataclass
class DetectedDevice:
    name: str
    confidence: float
    bounding_box: Tuple[int, int, int, int]  # x, y, width, height
    device_type: str
    automation_potential: str

@dataclass
class RoomAnalysis:
    room_type: str
    confidence: float
    dimensions_estimate: Tuple[float, float]  # width, height in meters
    lighting_conditions: str
    detected_devices: List[DetectedDevice]
    automation_suggestions: List[str]

class ImageAnalyzer:
    def __init__(self):
        self.device_templates = self._load_device_templates()
        self.room_classifiers = self._load_room_classifiers()
    
    def _load_device_templates(self) -> Dict[str, Any]:
        """Load templates for device recognition"""
        # In a real implementation, these would be trained ML models
        # For now, we'll use basic computer vision techniques
        return {
            'light_switch': {
                'color_range': [(200, 200, 200), (255, 255, 255)],
                'shape': 'rectangular',
                'typical_size': (50, 100),
                'automation_potential': 'High - Can be replaced with smart switch'
            },
            'thermostat': {
                'color_range': [(180, 180, 180), (220, 220, 220)],
                'shape': 'rectangular',
                'typical_size': (80, 80),
                'automation_potential': 'High - Can be upgraded to smart thermostat'
            },
            'electrical_outlet': {
                'color_range': [(240, 240, 240), (255, 255, 255)],
                'shape': 'rectangular',
                'typical_size': (40, 80),
                'automation_potential': 'Medium - Can add smart plugs'
            },
            'window': {
                'color_range': [(100, 150, 200), (200, 250, 255)],
                'shape': 'rectangular',
                'typical_size': (200, 300),
                'automation_potential': 'High - Can add smart blinds/curtains'
            },
            'door': {
                'color_range': [(139, 69, 19), (160, 82, 45)],
                'shape': 'rectangular',
                'typical_size': (200, 400),
                'automation_potential': 'High - Can add smart lock'
            }
        }
    
    def _load_room_classifiers(self) -> Dict[str, Any]:
        """Load room type classifiers"""
        return {
            'kitchen': {
                'keywords': ['stove', 'refrigerator', 'sink', 'cabinet', 'counter'],
                'color_patterns': ['white', 'stainless steel'],
                'automation_focus': ['smart appliances', 'lighting', 'leak detection']
            },
            'living_room': {
                'keywords': ['sofa', 'tv', 'coffee table', 'lamp'],
                'color_patterns': ['warm tones', 'varied'],
                'automation_focus': ['entertainment', 'lighting', 'climate control']
            },
            'bedroom': {
                'keywords': ['bed', 'dresser', 'nightstand', 'closet'],
                'color_patterns': ['soft tones', 'neutral'],
                'automation_focus': ['sleep optimization', 'lighting', 'climate control']
            },
            'bathroom': {
                'keywords': ['toilet', 'sink', 'shower', 'bathtub', 'mirror'],
                'color_patterns': ['white', 'tile'],
                'automation_focus': ['water monitoring', 'ventilation', 'lighting']
            },
            'office': {
                'keywords': ['desk', 'computer', 'chair', 'bookshelf'],
                'color_patterns': ['neutral', 'organized'],
                'automation_focus': ['productivity lighting', 'climate control', 'security']
            }
        }
    
    def analyze_image(self, image_data: str) -> RoomAnalysis:
        """Analyze uploaded image and provide automation recommendations"""
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_data.split(',')[1] if ',' in image_data else image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Analyze room type
            room_type, room_confidence = self._classify_room_type(cv_image)
            
            # Estimate room dimensions
            dimensions = self._estimate_room_dimensions(cv_image)
            
            # Analyze lighting conditions
            lighting = self._analyze_lighting_conditions(cv_image)
            
            # Detect devices and automation opportunities
            detected_devices = self._detect_devices(cv_image)
            
            # Generate automation suggestions
            suggestions = self._generate_automation_suggestions(room_type, detected_devices, lighting)
            
            return RoomAnalysis(
                room_type=room_type,
                confidence=room_confidence,
                dimensions_estimate=dimensions,
                lighting_conditions=lighting,
                detected_devices=detected_devices,
                automation_suggestions=suggestions
            )
        
        except Exception as e:
            logging.error(f"Error analyzing image: {e}")
            return RoomAnalysis(
                room_type="unknown",
                confidence=0.0,
                dimensions_estimate=(0.0, 0.0),
                lighting_conditions="unknown",
                detected_devices=[],
                automation_suggestions=["Unable to analyze image. Please try uploading a clearer photo."]
            )
    
    def _classify_room_type(self, image: np.ndarray) -> Tuple[str, float]:
        """Classify the type of room from the image"""
        # Simple color-based classification
        # In a real implementation, this would use a trained CNN
        
        # Analyze dominant colors
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pixels = image_rgb.reshape(-1, 3)
        
        # Calculate color statistics
        mean_color = np.mean(pixels, axis=0)
        color_variance = np.var(pixels, axis=0)
        
        # Simple heuristics for room classification
        if mean_color[0] > 200 and mean_color[1] > 200 and mean_color[2] > 200:
            # Bright, white-dominated space
            if color_variance.mean() < 500:
                return "bathroom", 0.7
            else:
                return "kitchen", 0.6
        elif mean_color.mean() < 100:
            # Dark space
            return "bedroom", 0.5
        else:
            # Mixed colors
            return "living_room", 0.6
    
    def _estimate_room_dimensions(self, image: np.ndarray) -> Tuple[float, float]:
        """Estimate room dimensions from perspective cues"""
        height, width = image.shape[:2]
        
        # Simple estimation based on image aspect ratio and typical room sizes
        # This is a very basic approximation
        aspect_ratio = width / height
        
        if aspect_ratio > 1.5:
            # Wide room
            estimated_width = 5.0  # meters
            estimated_height = 3.5
        elif aspect_ratio < 0.8:
            # Tall/narrow room
            estimated_width = 3.0
            estimated_height = 4.0
        else:
            # Square-ish room
            estimated_width = 4.0
            estimated_height = 4.0
        
        return (estimated_width, estimated_height)
    
    def _analyze_lighting_conditions(self, image: np.ndarray) -> str:
        """Analyze lighting conditions in the image"""
        # Convert to grayscale for brightness analysis
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)
        
        if mean_brightness > 180:
            return "Very Bright - May benefit from smart blinds"
        elif mean_brightness > 120:
            return "Well Lit - Good for automation"
        elif mean_brightness > 60:
            return "Moderate - Could use additional smart lighting"
        else:
            return "Dark - Needs smart lighting solutions"
    
    def _detect_devices(self, image: np.ndarray) -> List[DetectedDevice]:
        """Detect existing devices and automation opportunities"""
        detected_devices = []
        
        # Convert to different color spaces for better detection
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect rectangular objects (potential switches, outlets, etc.)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            # Filter by area
            area = cv2.contourArea(contour)
            if area < 100 or area > 50000:
                continue
            
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h
            
            # Classify based on size and aspect ratio
            if 0.3 < aspect_ratio < 0.7 and 1000 < area < 5000:
                # Potential light switch
                detected_devices.append(DetectedDevice(
                    name="Light Switch",
                    confidence=0.6,
                    bounding_box=(x, y, w, h),
                    device_type="switch",
                    automation_potential="High - Replace with smart switch (£20-50)"
                ))
            elif 0.8 < aspect_ratio < 1.2 and 2000 < area < 8000:
                # Potential thermostat or control panel
                detected_devices.append(DetectedDevice(
                    name="Control Panel/Thermostat",
                    confidence=0.5,
                    bounding_box=(x, y, w, h),
                    device_type="control",
                    automation_potential="High - Upgrade to smart thermostat (£120-200)"
                ))
            elif aspect_ratio > 2 and area > 10000:
                # Potential window
                detected_devices.append(DetectedDevice(
                    name="Window",
                    confidence=0.4,
                    bounding_box=(x, y, w, h),
                    device_type="window",
                    automation_potential="Medium - Add smart blinds (£150-300)"
                ))
        
        # Limit to most confident detections
        detected_devices.sort(key=lambda x: x.confidence, reverse=True)
        return detected_devices[:5]
    
    def _generate_automation_suggestions(self, room_type: str, devices: List[DetectedDevice], lighting: str) -> List[str]:
        """Generate specific automation suggestions based on analysis"""
        suggestions = []
        
        # Room-specific suggestions
        room_suggestions = {
            'kitchen': [
                "Install smart smoke detector (£30-50)",
                "Add smart leak sensors under sink (£20 each)",
                "Smart coffee maker for morning automation (£150-200)",
                "Smart plugs for appliances (£15 each)"
            ],
            'living_room': [
                "Smart TV integration for entertainment control",
                "Smart speakers for voice control (£50-100)",
                "Smart lighting scenes for different activities",
                "Smart thermostat for comfort optimization (£120-200)"
            ],
            'bedroom': [
                "Smart sleep tracking and environment optimization",
                "Automated blackout curtains (£200-400)",
                "Smart alarm clock with gradual wake lighting",
                "Air quality monitoring (£100-150)"
            ],
            'bathroom': [
                "Smart ventilation fan with humidity control (£80-120)",
                "Leak detection sensors (£20 each)",
                "Smart mirror with lighting (£200-500)",
                "Automated towel warmer (£100-200)"
            ],
            'office': [
                "Smart lighting for productivity (£100-200)",
                "Air quality monitoring for focus (£100-150)",
                "Smart desk setup with automated height adjustment",
                "Security camera for monitoring (£50-150)"
            ]
        }
        
        # Add room-specific suggestions
        if room_type in room_suggestions:
            suggestions.extend(room_suggestions[room_type][:3])
        
        # Add device-specific suggestions
        for device in devices:
            suggestions.append(device.automation_potential)
        
        # Add lighting-specific suggestions
        if "Dark" in lighting:
            suggestions.append("Install smart LED strips for ambient lighting (£30-60)")
        elif "Very Bright" in lighting:
            suggestions.append("Add smart blinds for light control (£150-300)")
        
        # Add general suggestions
        suggestions.extend([
            "Smart motion sensors for automated lighting (£15-25 each)",
            "Smart plugs for energy monitoring (£15 each)",
            "Voice assistant for central control (£30-100)"
        ])
        
        # Remove duplicates and limit
        unique_suggestions = list(dict.fromkeys(suggestions))
        return unique_suggestions[:8]
    
    def create_annotated_image(self, image_data: str, analysis: RoomAnalysis) -> str:
        """Create an annotated version of the image showing detected devices"""
        try:
            # Decode image
            image_bytes = base64.b64decode(image_data.split(',')[1] if ',' in image_data else image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Create drawing context
            draw = ImageDraw.Draw(image)
            
            # Try to load a font, fall back to default if not available
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                font = ImageFont.load_default()
            
            # Draw bounding boxes and labels for detected devices
            colors = ['red', 'blue', 'green', 'orange', 'purple']
            for i, device in enumerate(analysis.detected_devices):
                x, y, w, h = device.bounding_box
                color = colors[i % len(colors)]
                
                # Draw bounding box
                draw.rectangle([x, y, x + w, y + h], outline=color, width=3)
                
                # Draw label
                label = f"{device.name} ({device.confidence:.1f})"
                draw.text((x, y - 20), label, fill=color, font=font)
            
            # Add room type and confidence
            room_label = f"Room: {analysis.room_type.title()} ({analysis.confidence:.1f})"
            draw.text((10, 10), room_label, fill='black', font=font)
            
            # Add dimensions estimate
            dims_label = f"Est. Size: {analysis.dimensions_estimate[0]:.1f}m x {analysis.dimensions_estimate[1]:.1f}m"
            draw.text((10, 35), dims_label, fill='black', font=font)
            
            # Convert back to base64
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            annotated_data = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{annotated_data}"
        
        except Exception as e:
            logging.error(f"Error creating annotated image: {e}")
            return image_data  # Return original if annotation fails


class ProjectVisualizer:
    def __init__(self):
        self.component_images = self._load_component_images()
    
    def _load_component_images(self) -> Dict[str, str]:
        """Load component images for visualization"""
        # In a real implementation, these would be actual component images
        return {
            'raspberry_pi': 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCI+PHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9ImdyZWVuIi8+PC9zdmc+',
            'arduino': 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCI+PHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9ImJsdWUiLz48L3N2Zz4=',
            'sensor': 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCI+PGNpcmNsZSBjeD0iNTAiIGN5PSI1MCIgcj0iNDAiIGZpbGw9InJlZCIvPjwvc3ZnPg==',
            'smart_bulb': 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCI+PGNpcmNsZSBjeD0iNTAiIGN5PSI1MCIgcj0iNDAiIGZpbGw9InllbGxvdyIvPjwvc3ZnPg=='
        }
    
    def create_project_diagram(self, components: List[str], connections: List[Tuple[str, str]]) -> str:
        """Create a visual diagram of project components and connections"""
        # This would create an SVG or image showing how components connect
        # For now, return a simple placeholder
        diagram_svg = f'''
        <svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
            <rect width="400" height="300" fill="#f0f0f0" stroke="#ccc"/>
            <text x="200" y="30" text-anchor="middle" font-size="16" font-weight="bold">Project Diagram</text>
            <text x="200" y="60" text-anchor="middle" font-size="12">Components: {len(components)}</text>
            <text x="200" y="80" text-anchor="middle" font-size="12">Connections: {len(connections)}</text>
        </svg>
        '''
        
        # Convert to base64
        diagram_b64 = base64.b64encode(diagram_svg.encode()).decode()
        return f"data:image/svg+xml;base64,{diagram_b64}"


# Global instances
image_analyzer = ImageAnalyzer()
project_visualizer = ProjectVisualizer()

def analyze_uploaded_image(image_data: str) -> Dict[str, Any]:
    """Main function to analyze uploaded images"""
    analysis = image_analyzer.analyze_image(image_data)
    annotated_image = image_analyzer.create_annotated_image(image_data, analysis)
    
    return {
        'room_type': analysis.room_type,
        'confidence': analysis.confidence,
        'dimensions': analysis.dimensions_estimate,
        'lighting': analysis.lighting_conditions,
        'devices': [
            {
                'name': device.name,
                'confidence': device.confidence,
                'type': device.device_type,
                'automation_potential': device.automation_potential
            }
            for device in analysis.detected_devices
        ],
        'suggestions': analysis.automation_suggestions,
        'annotated_image': annotated_image
    }

if __name__ == "__main__":
    # Test with a sample image (would need actual image data)
    print("Image analyzer initialized and ready for use")
    print("Available device templates:", list(image_analyzer.device_templates.keys()))
    print("Available room classifiers:", list(image_analyzer.room_classifiers.keys()))

