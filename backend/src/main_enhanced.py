import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS 
from datetime import datetime
from src.models.project import db
from src.routes.projects import projects_bp
from src.routes.ai_chat import ai_chat_bp
from src.routes.learning import learning_bp
from src.routes.community import community_bp

# Import enhanced modules
try:
    from src.routes.ai_chat_enhanced import ai_chat_enhanced_bp
    from src.ai_manager import ai_manager, initialize_ai_providers
    from src.web_scraper import price_monitor, news_monitor, weather_service, run_daily_data_collection
    from src.image_analyzer import image_analyzer
    from src.iot_controller import iot_controller, initialize_sample_devices
    ENHANCED_FEATURES_AVAILABLE = True
    print("Enhanced features loaded successfully")
except ImportError as e:
    print(f"Enhanced features not available: {e}")
    ENHANCED_FEATURES_AVAILABLE = False

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'techcraft_genius_ai_enhanced_secret_key_2024'

# Enable CORS for all routes
CORS(app)

# Register blueprints
app.register_blueprint(projects_bp, url_prefix='/api')
app.register_blueprint(ai_chat_bp, url_prefix='/api')
app.register_blueprint(learning_bp, url_prefix='/api')
app.register_blueprint(community_bp, url_prefix='/api')

# Register enhanced blueprint if available
if ENHANCED_FEATURES_AVAILABLE:
    app.register_blueprint(ai_chat_enhanced_bp, url_prefix='/api/enhanced')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

# Enhanced API endpoints
@app.route('/api/system/status', methods=['GET'])
def get_system_status():
    """Get comprehensive system status"""
    status = {
        'timestamp': datetime.now().isoformat(),
        'enhanced_features': ENHANCED_FEATURES_AVAILABLE,
        'version': '2.0.0-enhanced',
        'components': {
            'ai_manager': False,
            'price_monitor': False,
            'image_analyzer': False,
            'iot_controller': False,
            'weather_service': False
        }
    }
    
    if ENHANCED_FEATURES_AVAILABLE:
        try:
            # Check AI manager status
            ai_status = ai_manager.get_provider_status()
            status['components']['ai_manager'] = len(ai_status) > 0
            status['ai_providers'] = ai_status
        except Exception as e:
            print(f"AI manager check failed: {e}")
        
        try:
            # Check IoT controller status
            device_status = iot_controller.get_device_status()
            status['components']['iot_controller'] = True
            status['iot_devices'] = device_status['total_devices']
            status['iot_online'] = device_status['online_devices']
        except Exception as e:
            print(f"IoT controller check failed: {e}")
        
        try:
            # Check weather service
            weather_data = weather_service.get_london_weather()
            status['components']['weather_service'] = len(weather_data) > 0
            status['current_weather'] = weather_data
        except Exception as e:
            print(f"Weather service check failed: {e}")
        
        status['components']['price_monitor'] = True
        status['components']['image_analyzer'] = True
    
    return jsonify(status)

@app.route('/api/enhanced/price-check', methods=['POST'])
def enhanced_price_check():
    """Enhanced price checking with real-time data"""
    if not ENHANCED_FEATURES_AVAILABLE:
        return jsonify({'error': 'Enhanced features not available'}), 503
    
    try:
        data = request.get_json()
        components = data.get('components', [])
        
        if not components:
            return jsonify({'error': 'No components specified'}), 400
        
        # Monitor prices for specified components
        price_data = price_monitor.monitor_component_prices(components)
        
        return jsonify({
            'success': True,
            'price_data': price_data,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/enhanced/iot/devices', methods=['GET'])
def get_iot_devices():
    """Get all IoT devices"""
    if not ENHANCED_FEATURES_AVAILABLE:
        return jsonify({'error': 'Enhanced features not available'}), 503
    
    try:
        device_status = iot_controller.get_device_status()
        return jsonify(device_status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/enhanced/iot/control', methods=['POST'])
def control_iot_device():
    """Control an IoT device"""
    if not ENHANCED_FEATURES_AVAILABLE:
        return jsonify({'error': 'Enhanced features not available'}), 503
    
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        action = data.get('action')
        parameters = data.get('parameters', {})
        
        if not device_id or not action:
            return jsonify({'error': 'device_id and action are required'}), 400
        
        result = iot_controller.control_device(device_id, action, parameters)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/enhanced/iot/automation', methods=['GET'])
def get_automation_rules():
    """Get all automation rules"""
    if not ENHANCED_FEATURES_AVAILABLE:
        return jsonify({'error': 'Enhanced features not available'}), 503
    
    try:
        automation_status = iot_controller.get_automation_status()
        return jsonify(automation_status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/enhanced/iot/energy-report', methods=['GET'])
def get_energy_report():
    """Get energy consumption report"""
    if not ENHANCED_FEATURES_AVAILABLE:
        return jsonify({'error': 'Enhanced features not available'}), 503
    
    try:
        days = request.args.get('days', 7, type=int)
        energy_report = iot_controller.get_energy_report(days)
        return jsonify(energy_report)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/enhanced/news', methods=['GET'])
def get_tech_news():
    """Get relevant tech news"""
    if not ENHANCED_FEATURES_AVAILABLE:
        return jsonify({'error': 'Enhanced features not available'}), 503
    
    try:
        limit = request.args.get('limit', 10, type=int)
        relevant_news = news_monitor.get_relevant_news(limit)
        
        news_data = []
        for news in relevant_news:
            news_data.append({
                'title': news.title,
                'summary': news.summary,
                'url': news.url,
                'source': news.source,
                'published_date': news.published_date.isoformat(),
                'relevance_score': news.relevance_score
            })
        
        return jsonify({
            'news': news_data,
            'total': len(news_data),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/enhanced/data-collection', methods=['POST'])
def trigger_data_collection():
    """Manually trigger data collection"""
    if not ENHANCED_FEATURES_AVAILABLE:
        return jsonify({'error': 'Enhanced features not available'}), 503
    
    try:
        # Run data collection in background
        import threading
        collection_thread = threading.Thread(target=run_daily_data_collection, daemon=True)
        collection_thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Data collection started',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/enhanced/image-analysis', methods=['POST'])
def analyze_image():
    """Analyze uploaded image for automation opportunities"""
    if not ENHANCED_FEATURES_AVAILABLE:
        return jsonify({'error': 'Enhanced features not available'}), 503
    
    try:
        data = request.get_json()
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
        
        from src.image_analyzer import analyze_uploaded_image
        analysis_result = analyze_uploaded_image(image_data)
        
        return jsonify({
            'success': True,
            'analysis': analysis_result,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Serve static files (frontend)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

# Initialize enhanced features on startup
if ENHANCED_FEATURES_AVAILABLE:
    try:
        # Initialize AI providers
        initialize_ai_providers()
        print("✓ AI providers initialized")
    except Exception as e:
        print(f"✗ Failed to initialize AI providers: {e}")
    
    try:
        # Initialize sample IoT devices
        initialize_sample_devices()
        print("✓ Sample IoT devices initialized")
    except Exception as e:
        print(f"✗ Failed to initialize IoT devices: {e}")

if __name__ == '__main__':
    print("🚀 Starting TechCraft Genius AI Enhanced Platform...")
    print(f"📊 Enhanced features available: {ENHANCED_FEATURES_AVAILABLE}")
    if ENHANCED_FEATURES_AVAILABLE:
        print("🔥 Full AI capabilities enabled:")
        print("   • Multi-AI provider cycling")
        print("   • Computer vision & image analysis")
        print("   • Real-time price monitoring")
        print("   • IoT device control")
        print("   • Weather integration")
        print("   • Tech news monitoring")
    else:
        print("⚠️  Running in basic mode - enhanced features disabled")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

