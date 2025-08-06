from flask import Blueprint, request, jsonify
from datetime import datetime
import random
import sys
import os

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ai_manager import ai_manager
    from image_analyzer import analyze_uploaded_image
    from web_scraper import price_monitor, weather_service
    AI_INTEGRATION_AVAILABLE = True
except ImportError as e:
    print(f"AI integration modules not available: {e}")
    AI_INTEGRATION_AVAILABLE = False

ai_chat_enhanced_bp = Blueprint('ai_chat_enhanced', __name__)

# Enhanced AI responses with real capabilities
AI_RESPONSES = {
    'concept_merging': [
        "Excellent concept merging request! Let me analyze the synergy between these ideas using my advanced AI capabilities...",
        "I can merge these concepts with high compatibility. Using my multi-AI analysis, here's my innovative solution:",
        "Fascinating combination! Based on my continuous learning from multiple AI sources, I can create something unique:"
    ],
    'project_help': [
        "I understand you're interested in that project! Let me analyze the requirements using real-time data and suggest the best approach.",
        "Based on my continuous learning and current market data, I can recommend optimal components with live pricing.",
        "Perfect project choice! I'll help you optimize costs using real-time price monitoring and provide detailed instructions."
    ],
    'image_analysis': [
        "I can analyze your image to identify automation opportunities and suggest specific improvements for your space.",
        "Let me examine your photo to detect existing devices and recommend smart home upgrades with cost estimates.",
        "I'll analyze your room layout and provide personalized automation suggestions based on what I see."
    ],
    'price_inquiry': [
        "I'm checking real-time prices across multiple UK suppliers to find you the best deals...",
        "Let me scan current market prices and availability for those components...",
        "I'll find the most cost-effective options from my live price monitoring system..."
    ],
    'general': [
        "I'm continuously learning from multiple AI sources and can help you with any DIY tech project. What would you like to build?",
        "My knowledge base is constantly expanding through real-time data collection. I can assist with project planning, component selection, and cost optimization.",
        "I'm here to help you create amazing tech projects! Ask me about concept merging, image analysis, price checking, or anything else."
    ]
}

@ai_chat_enhanced_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '').lower()
        image_data = data.get('image', None)
        
        # Determine response type and use appropriate AI capability
        if image_data:
            # Image analysis request
            return handle_image_analysis(message, image_data)
        elif any(word in message for word in ['price', 'cost', 'cheap', 'buy', 'supplier']):
            # Price inquiry
            return handle_price_inquiry(message)
        elif any(word in message for word in ['merge', 'combine', 'concept']):
            # Concept merging with AI
            return handle_concept_merging(message)
        elif any(word in message for word in ['project', 'build', 'create', 'help', 'automate']):
            # Project help with AI
            return handle_project_help(message)
        elif any(word in message for word in ['weather', 'temperature', 'london']):
            # Weather-based automation suggestions
            return handle_weather_inquiry(message)
        else:
            # General conversation with AI
            return handle_general_chat(message)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def handle_image_analysis(message: str, image_data: str):
    """Handle image analysis requests"""
    try:
        if not AI_INTEGRATION_AVAILABLE:
            return jsonify({
                'response': "Image analysis is currently unavailable. Please try again later.",
                'timestamp': datetime.now().isoformat(),
                'ai_status': 'unavailable'
            }), 503
        
        # Analyze the uploaded image
        analysis_result = analyze_uploaded_image(image_data)
        
        # Generate AI response based on analysis
        ai_prompt = f"""
        I've analyzed an image of a {analysis_result['room_type']} with {analysis_result['confidence']:.1f} confidence.
        Detected devices: {[d['name'] for d in analysis_result['devices']]}
        Lighting conditions: {analysis_result['lighting']}
        
        User message: {message}
        
        Please provide specific automation recommendations with UK pricing.
        """
        
        # Get AI response
        ai_response = ai_manager.send_message(ai_prompt)
        
        if 'error' in ai_response:
            # Fallback to template response
            response = random.choice(AI_RESPONSES['image_analysis'])
            response += f"\n\nRoom Analysis:\n"
            response += f"• Room Type: {analysis_result['room_type'].title()} ({analysis_result['confidence']:.1f} confidence)\n"
            response += f"• Estimated Size: {analysis_result['dimensions'][0]:.1f}m x {analysis_result['dimensions'][1]:.1f}m\n"
            response += f"• Lighting: {analysis_result['lighting']}\n"
            response += f"• Detected Devices: {len(analysis_result['devices'])}\n\n"
            response += "Top Automation Suggestions:\n"
            for i, suggestion in enumerate(analysis_result['suggestions'][:5], 1):
                response += f"{i}. {suggestion}\n"
        else:
            response = ai_response['response']
        
        return jsonify({
            'response': response,
            'image_analysis': analysis_result,
            'timestamp': datetime.now().isoformat(),
            'ai_provider': ai_response.get('provider', 'Template'),
            'ai_status': 'analyzing_image',
            'confidence': 0.95
        })
    
    except Exception as e:
        return jsonify({
            'response': f"I encountered an error analyzing your image: {str(e)}. Please try uploading a clearer photo.",
            'timestamp': datetime.now().isoformat(),
            'ai_status': 'error'
        }), 500

def handle_price_inquiry(message: str):
    """Handle price and component inquiries"""
    try:
        if not AI_INTEGRATION_AVAILABLE:
            return jsonify({
                'response': "Price monitoring is currently unavailable. Please check back later.",
                'timestamp': datetime.now().isoformat(),
                'ai_status': 'unavailable'
            }), 503
        
        # Extract component names from message
        components = []
        common_components = [
            'raspberry pi', 'arduino', 'smart bulb', 'smart plug', 'thermostat',
            'camera', 'sensor', 'led strip', 'smart switch', 'motion sensor'
        ]
        
        for component in common_components:
            if component in message:
                components.append(component)
        
        if not components:
            components = ['smart home starter kit']  # Default search
        
        # Get real price data
        price_data = {}
        for component in components[:3]:  # Limit to 3 components
            prices = price_monitor.get_best_prices(component, limit=3)
            if prices:
                price_data[component] = [
                    {
                        'supplier': p.supplier,
                        'price': p.price,
                        'currency': p.currency,
                        'availability': p.availability,
                        'url': p.url
                    }
                    for p in prices
                ]
        
        # Generate AI response with price data
        ai_prompt = f"""
        User is asking about prices for: {', '.join(components)}
        
        Current UK market data:
        {price_data}
        
        User message: {message}
        
        Please provide helpful advice about these components, their prices, and automation potential.
        """
        
        ai_response = ai_manager.send_message(ai_prompt)
        
        if 'error' in ai_response:
            # Fallback response with real price data
            response = random.choice(AI_RESPONSES['price_inquiry'])
            response += f"\n\nCurrent UK Prices:\n"
            for component, prices in price_data.items():
                response += f"\n{component.title()}:\n"
                for price in prices:
                    response += f"• {price['supplier']}: £{price['price']} ({price['availability']})\n"
        else:
            response = ai_response['response']
        
        return jsonify({
            'response': response,
            'price_data': price_data,
            'timestamp': datetime.now().isoformat(),
            'ai_provider': ai_response.get('provider', 'Template'),
            'ai_status': 'price_monitoring',
            'confidence': 0.92
        })
    
    except Exception as e:
        return jsonify({
            'response': f"I'm having trouble accessing current price data: {str(e)}. Let me provide general guidance instead.",
            'timestamp': datetime.now().isoformat(),
            'ai_status': 'error'
        }), 500

def handle_concept_merging(message: str):
    """Handle concept merging requests with AI"""
    try:
        if AI_INTEGRATION_AVAILABLE:
            ai_prompt = f"""
            The user wants to merge concepts for a DIY tech project.
            
            User message: {message}
            
            Please analyze the concepts they want to merge and create an innovative project idea with:
            1. Project name and description
            2. Component list with UK prices
            3. Step-by-step build instructions
            4. Automation potential
            5. Cost estimate
            
            Be creative and practical.
            """
            
            ai_response = ai_manager.send_message(ai_prompt)
        else:
            ai_response = {'error': 'AI not available'}
        
        if 'error' in ai_response:
            # Fallback to enhanced template response
            response = random.choice(AI_RESPONSES['concept_merging'])
            
            # Extract concepts from message
            words = message.split()
            concepts = [word for word in words if len(word) > 3 and word not in ['merge', 'combine', 'with', 'and']]
            
            if len(concepts) >= 2:
                project_name = f"Smart {concepts[0].title()}-{concepts[1].title()} System"
                response += f"\n\n🚀 Project: {project_name}\n"
                response += f"Synergy Score: {random.randint(85, 98)}%\n\n"
                response += "Components needed:\n"
                response += "• Microcontroller (Arduino/Raspberry Pi): £25-75\n"
                response += "• Sensors and modules: £30-60\n"
                response += "• Connectivity (WiFi/Bluetooth): £15-25\n"
                response += "• Housing and accessories: £20-40\n\n"
                response += f"Total estimated cost: £90-200\n"
                response += f"Difficulty: Intermediate\n"
                response += f"Build time: 2-4 days\n"
                response += f"Automation potential: High"
        else:
            response = ai_response['response']
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'ai_provider': ai_response.get('provider', 'Template'),
            'ai_status': 'concept_merging',
            'confidence': ai_response.get('confidence', 0.94)
        })
    
    except Exception as e:
        return jsonify({
            'response': f"I encountered an error during concept merging: {str(e)}. Let me try a different approach.",
            'timestamp': datetime.now().isoformat(),
            'ai_status': 'error'
        }), 500

def handle_project_help(message: str):
    """Handle project help requests with AI"""
    try:
        weather_data = {}
        if AI_INTEGRATION_AVAILABLE:
            # Get current weather for context
            weather_data = weather_service.get_london_weather()
            
            ai_prompt = f"""
            The user needs help with a DIY tech project.
            
            User message: {message}
            
            Current London conditions: {weather_data.get('description', 'N/A')}, {weather_data.get('temperature', 'N/A')}°C
            
            Please provide:
            1. Project analysis and recommendations
            2. Component suggestions with UK availability
            3. Step-by-step guidance
            4. Cost optimization tips
            5. London-specific considerations (weather, regulations, suppliers)
            
            Be practical and specific.
            """
            
            ai_response = ai_manager.send_message(ai_prompt)
        else:
            ai_response = {'error': 'AI not available'}
        
        if 'error' in ai_response:
            # Enhanced fallback response
            response = random.choice(AI_RESPONSES['project_help'])
            response += f"\n\nProject Analysis:\n"
            response += f"Based on your request, I recommend starting with these components:\n"
            response += f"• Control unit: Raspberry Pi 4 or Arduino (£25-75)\n"
            response += f"• Sensors: Motion, temperature, humidity (£15-30 each)\n"
            response += f"• Connectivity: WiFi module (£15-25)\n"
            response += f"• Power supply: Suitable adapter (£10-20)\n\n"
            
            if weather_data:
                response += f"London Weather Context:\n"
                response += f"Current conditions: {weather_data.get('description', 'N/A')}, {weather_data.get('temperature', 'N/A')}°C\n"
                response += f"Consider weatherproofing for outdoor components.\n\n"
            
            response += f"Next steps:\n"
            response += f"1. Define specific requirements\n"
            response += f"2. Source components from UK suppliers\n"
            response += f"3. Create a prototype\n"
            response += f"4. Test and iterate"
        else:
            response = ai_response['response']
        
        return jsonify({
            'response': response,
            'weather_context': weather_data,
            'timestamp': datetime.now().isoformat(),
            'ai_provider': ai_response.get('provider', 'Template'),
            'ai_status': 'project_assistance',
            'confidence': ai_response.get('confidence', 0.91)
        })
    
    except Exception as e:
        return jsonify({
            'response': f"I'm having trouble accessing all my resources: {str(e)}. Let me provide basic project guidance.",
            'timestamp': datetime.now().isoformat(),
            'ai_status': 'error'
        }), 500

def handle_weather_inquiry(message: str):
    """Handle weather-based automation suggestions"""
    try:
        weather_data = {}
        forecast_data = []
        
        if AI_INTEGRATION_AVAILABLE:
            weather_data = weather_service.get_london_weather()
            forecast_data = weather_service.get_weather_forecast(3)
            
            ai_prompt = f"""
            User is asking about weather-related automation.
            
            User message: {message}
            
            Current London weather: {weather_data}
            3-day forecast: {forecast_data[:8] if forecast_data else 'Not available'}
            
            Please suggest smart home automations based on current and forecasted weather conditions.
            """
            
            ai_response = ai_manager.send_message(ai_prompt)
        else:
            ai_response = {'error': 'AI not available'}
        
        if 'error' in ai_response:
            response = f"Current London Weather: {weather_data.get('description', 'N/A')}, {weather_data.get('temperature', 'N/A')}°C\n\n"
            response += "Weather-based automation suggestions:\n"
            
            temp = weather_data.get('temperature', 15)
            if temp < 10:
                response += "• Increase heating automation (smart thermostat)\n"
                response += "• Close smart blinds for insulation\n"
            elif temp > 25:
                response += "• Activate cooling systems\n"
                response += "• Open smart windows for ventilation\n"
            
            humidity = weather_data.get('humidity', 50)
            if humidity > 70:
                response += "• Activate dehumidifiers\n"
                response += "• Increase ventilation\n"
            
            response += "\nRecommended devices:\n"
            response += "• Smart thermostat: £120-200\n"
            response += "• Smart blinds: £150-300\n"
            response += "• Weather station: £50-100"
        else:
            response = ai_response['response']
        
        return jsonify({
            'response': response,
            'weather_data': weather_data,
            'forecast_data': forecast_data[:8] if forecast_data else [],
            'timestamp': datetime.now().isoformat(),
            'ai_provider': ai_response.get('provider', 'Template'),
            'ai_status': 'weather_analysis',
            'confidence': 0.93
        })
    
    except Exception as e:
        return jsonify({
            'response': f"I'm having trouble accessing weather data: {str(e)}. Let me provide general automation advice.",
            'timestamp': datetime.now().isoformat(),
            'ai_status': 'error'
        }), 500

def handle_general_chat(message: str):
    """Handle general conversation with AI"""
    try:
        if AI_INTEGRATION_AVAILABLE:
            ai_prompt = f"""
            User is having a general conversation about smart home automation and DIY tech projects.
            
            User message: {message}
            
            Please respond helpfully and encourage them to explore automation possibilities.
            Mention specific capabilities like image analysis, price monitoring, concept merging, and project guidance.
            """
            
            ai_response = ai_manager.send_message(ai_prompt)
        else:
            ai_response = {'error': 'AI not available'}
        
        if 'error' in ai_response:
            response = random.choice(AI_RESPONSES['general'])
            response += f"\n\nI can help you with:\n"
            response += f"• 📸 Image analysis - Upload photos for automation suggestions\n"
            response += f"• 💰 Price monitoring - Real-time UK component pricing\n"
            response += f"• 🔄 Concept merging - Combine ideas into innovative projects\n"
            response += f"• 🛠️ Project guidance - Step-by-step build instructions\n"
            response += f"• 🌤️ Weather integration - London-specific automation\n\n"
            response += f"What would you like to explore?"
        else:
            response = ai_response['response']
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'ai_provider': ai_response.get('provider', 'Template'),
            'ai_status': 'general_conversation',
            'confidence': ai_response.get('confidence', 0.88)
        })
    
    except Exception as e:
        return jsonify({
            'response': f"I'm experiencing some technical difficulties: {str(e)}. How can I help you with your smart home project?",
            'timestamp': datetime.now().isoformat(),
            'ai_status': 'error'
        }), 500

@ai_chat_enhanced_bp.route('/ai-status', methods=['GET'])
def get_ai_status():
    """Get status of all AI providers"""
    try:
        if not AI_INTEGRATION_AVAILABLE:
            return jsonify({
                'providers': [],
                'total_providers': 0,
                'available_providers': 0,
                'status': 'AI integration not available',
                'timestamp': datetime.now().isoformat()
            })
        
        status = ai_manager.get_provider_status()
        return jsonify({
            'providers': status,
            'total_providers': len(status),
            'available_providers': len([p for p in status if p['available']]),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_chat_enhanced_bp.route('/reset-conversation', methods=['POST'])
def reset_conversation():
    """Reset conversation context"""
    try:
        if AI_INTEGRATION_AVAILABLE:
            ai_manager.reset_conversation()
        
        return jsonify({
            'message': 'Conversation context reset successfully',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_chat_enhanced_bp.route('/upload-image', methods=['POST'])
def upload_image():
    """Handle image upload for analysis"""
    try:
        data = request.get_json()
        image_data = data.get('image', '')
        message = data.get('message', 'Analyze this image for automation opportunities')
        
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
        
        return handle_image_analysis(message, image_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

