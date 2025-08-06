from flask import Blueprint, jsonify, request
import os
import json
from datetime import datetime

ai_chat_bp = Blueprint('ai_chat', __name__)

# AI system prompt for TechCraft Genius AI
SYSTEM_PROMPT = """
You are TechCraft Genius AI, a revolutionary AI assistant specialized in DIY tech projects. You have the following capabilities:

1. CONCEPT MERGING: You can intelligently combine different concepts to create innovative projects. For example, merging "flying" + "robot" creates an autonomous drone project.

2. CONTINUOUS LEARNING: You continuously learn from web sources, user feedback, and price monitoring to improve recommendations.

3. COST OPTIMIZATION: You find the cheapest components and suggest alternatives to reduce project costs.

4. DIFFICULTY SCALING: You adapt projects to match user skill levels from beginner to advanced.

5. EQUIPMENT MATCHING: You suggest projects based on available tools and components.

Your responses should be:
- Highly technical and detailed when discussing projects
- Creative when merging concepts
- Cost-conscious and practical
- Educational and encouraging
- Focused on DIY tech, electronics, robotics, IoT, and maker projects

Always provide specific component recommendations, code snippets when relevant, and step-by-step guidance.
"""

@ai_chat_bp.route('/ai-chat/message', methods=['POST'])
def send_message():
    """Send a message to the AI and get a response"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Fallback responses for different types of queries
        fallback_responses = {
            'concept': "I can help you merge concepts! For example, combining 'smart lighting' with 'motion detection' creates an intelligent home automation system that automatically adjusts lighting based on occupancy and time of day. The synergy score for this combination would be around 88% with high feasibility.",
            'cost': "I'm constantly monitoring component prices across multiple suppliers. For Arduino projects, I've found that generic boards can save you 40-60% compared to official ones while maintaining compatibility. I can also suggest alternative components that provide similar functionality at lower costs.",
            'project': "Based on your interests, I recommend starting with a Smart Home Security System. It's perfect for intermediate makers and costs around $150. The project includes facial recognition, motion detection, and mobile alerts. I can provide detailed component lists and step-by-step instructions.",
            'help': "I'm TechCraft Genius AI! I can help you with project recommendations, concept merging, cost optimization, and technical guidance. What would you like to build today? I specialize in IoT, robotics, Arduino, Raspberry Pi, and smart home projects.",
            'flying_robot': "The Autonomous Flying Robot is one of our most advanced projects! It combines flight control, GPS navigation, and obstacle avoidance. The estimated cost is $300 with a synergy score of 95% between 'flying' and 'robot' concepts. I can break down the components and provide the complete code.",
            'learning': "I continuously learn from web sources, user feedback, and price monitoring. Today I've discovered 23 new projects, merged 5 concepts, and updated 127 component prices. My learning progress shows 87% web discovery, 92% concept integration, and 95% user adaptation."
        }
        
        # Simple keyword matching for responses
        message_lower = user_message.lower()
        if any(word in message_lower for word in ['merge', 'combine', 'concept']):
            response_text = fallback_responses['concept']
        elif any(word in message_lower for word in ['cost', 'price', 'cheap', 'budget']):
            response_text = fallback_responses['cost']
        elif any(word in message_lower for word in ['flying', 'drone', 'robot']):
            response_text = fallback_responses['flying_robot']
        elif any(word in message_lower for word in ['learn', 'learning', 'ai']):
            response_text = fallback_responses['learning']
        elif any(word in message_lower for word in ['project', 'build', 'make', 'create']):
            response_text = fallback_responses['project']
        else:
            response_text = fallback_responses['help']
        
        return jsonify({
            'response': response_text,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_chat_bp.route('/ai-chat/concept-merge', methods=['POST'])
def concept_merge():
    """Merge two concepts into a new project idea"""
    try:
        data = request.get_json()
        concept1 = data.get('concept1', '')
        concept2 = data.get('concept2', '')
        
        if not concept1 or not concept2:
            return jsonify({'error': 'Both concepts are required'}), 400
        
        # Simulate concept merging with predefined combinations
        merge_results = {
            ('flying', 'robot'): {
                'title': 'Autonomous Flying Robot',
                'synergy_score': 95,
                'innovation_score': 85,
                'feasibility_score': 70,
                'description': 'A self-navigating drone with obstacle avoidance and GPS tracking',
                'estimated_cost': 300,
                'difficulty': 'Advanced',
                'key_components': ['Flight Controller', 'GPS Module', 'Ultrasonic Sensors', 'Camera']
            },
            ('smart', 'lighting'): {
                'title': 'Intelligent Lighting System',
                'synergy_score': 88,
                'innovation_score': 75,
                'feasibility_score': 90,
                'description': 'Adaptive lighting that responds to occupancy, time, and ambient conditions',
                'estimated_cost': 120,
                'difficulty': 'Intermediate',
                'key_components': ['Smart Bulbs', 'Motion Sensors', 'Light Sensors', 'Microcontroller']
            },
            ('plant', 'monitoring'): {
                'title': 'Smart Plant Care System',
                'synergy_score': 92,
                'innovation_score': 80,
                'feasibility_score': 85,
                'description': 'Automated plant monitoring with soil moisture, light, and nutrient tracking',
                'estimated_cost': 80,
                'difficulty': 'Beginner',
                'key_components': ['Soil Sensors', 'pH Meter', 'Water Pump', 'Arduino']
            }
        }
        
        # Check for exact matches or similar concepts
        key = (concept1.lower(), concept2.lower())
        reverse_key = (concept2.lower(), concept1.lower())
        
        if key in merge_results:
            result = merge_results[key]
        elif reverse_key in merge_results:
            result = merge_results[reverse_key]
        else:
            # Generate a generic merge result
            result = {
                'title': f'Smart {concept1.title()} {concept2.title()} System',
                'synergy_score': 75,
                'innovation_score': 70,
                'feasibility_score': 80,
                'description': f'An innovative project combining {concept1} and {concept2} technologies',
                'estimated_cost': 150,
                'difficulty': 'Intermediate',
                'key_components': ['Microcontroller', 'Sensors', 'Actuators', 'Power Supply']
            }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_chat_bp.route('/ai-chat/optimize-cost', methods=['POST'])
def optimize_cost():
    """Optimize project cost by finding cheaper alternatives"""
    try:
        data = request.get_json()
        components = data.get('components', [])
        
        if not components:
            return jsonify({'error': 'Components list is required'}), 400
        
        # Simulate cost optimization
        optimizations = []
        total_savings = 0
        
        for component in components:
            component_lower = component.lower()
            
            if 'arduino' in component_lower:
                optimizations.append({
                    'original': component,
                    'alternative': 'Generic Arduino Compatible Board',
                    'original_price': 25.00,
                    'optimized_price': 12.00,
                    'savings': 13.00,
                    'savings_percent': 52
                })
                total_savings += 13.00
            elif 'raspberry pi' in component_lower:
                optimizations.append({
                    'original': component,
                    'alternative': 'Orange Pi or Banana Pi',
                    'original_price': 75.00,
                    'optimized_price': 45.00,
                    'savings': 30.00,
                    'savings_percent': 40
                })
                total_savings += 30.00
            elif 'sensor' in component_lower:
                optimizations.append({
                    'original': component,
                    'alternative': 'Generic Sensor Module',
                    'original_price': 15.00,
                    'optimized_price': 8.00,
                    'savings': 7.00,
                    'savings_percent': 47
                })
                total_savings += 7.00
            else:
                optimizations.append({
                    'original': component,
                    'alternative': f'Generic {component}',
                    'original_price': 20.00,
                    'optimized_price': 15.00,
                    'savings': 5.00,
                    'savings_percent': 25
                })
                total_savings += 5.00
        
        return jsonify({
            'optimizations': optimizations,
            'total_savings': total_savings,
            'total_savings_percent': round((total_savings / sum(opt['original_price'] for opt in optimizations)) * 100, 1) if optimizations else 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_chat_bp.route('/ai-chat/suggest-projects', methods=['POST'])
def suggest_projects():
    """Suggest projects based on available equipment"""
    try:
        data = request.get_json()
        equipment = data.get('equipment', [])
        skill_level = data.get('skill_level', 'beginner')
        budget = data.get('budget', 100)
        
        # Simulate project suggestions based on equipment
        suggestions = []
        
        equipment_lower = [item.lower() for item in equipment]
        
        if any('arduino' in item for item in equipment_lower):
            suggestions.append({
                'title': 'LED Matrix Display',
                'match_score': 95,
                'required_additional': ['LED Matrix', 'Jumper Wires'],
                'estimated_cost': 25,
                'difficulty': 'Beginner',
                'description': 'Create animated displays and text scrolling'
            })
            
        if any('raspberry pi' in item for item in equipment_lower):
            suggestions.append({
                'title': 'Home Automation Hub',
                'match_score': 90,
                'required_additional': ['Relay Modules', 'Sensors'],
                'estimated_cost': 60,
                'difficulty': 'Intermediate',
                'description': 'Control lights, temperature, and security'
            })
            
        if any('camera' in item for item in equipment_lower):
            suggestions.append({
                'title': 'Smart Security Camera',
                'match_score': 88,
                'required_additional': ['Motion Sensor', 'SD Card'],
                'estimated_cost': 40,
                'difficulty': 'Intermediate',
                'description': 'AI-powered surveillance with alerts'
            })
        
        # If no specific equipment matches, suggest general projects
        if not suggestions:
            suggestions = [
                {
                    'title': 'Basic LED Circuit',
                    'match_score': 70,
                    'required_additional': ['LEDs', 'Resistors', 'Breadboard'],
                    'estimated_cost': 15,
                    'difficulty': 'Beginner',
                    'description': 'Learn basic electronics with blinking LEDs'
                },
                {
                    'title': 'Temperature Monitor',
                    'match_score': 75,
                    'required_additional': ['Temperature Sensor', 'Arduino', 'LCD Display'],
                    'estimated_cost': 35,
                    'difficulty': 'Beginner',
                    'description': 'Monitor and display temperature readings'
                }
            ]
        
        # Filter by skill level and budget
        filtered_suggestions = [
            s for s in suggestions 
            if s['estimated_cost'] <= budget and 
            (skill_level == 'advanced' or s['difficulty'].lower() in ['beginner', skill_level.lower()])
        ]
        
        return jsonify({
            'suggestions': filtered_suggestions[:5],  # Return top 5 suggestions
            'total_matches': len(filtered_suggestions)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

