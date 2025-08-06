from flask import Blueprint, jsonify, request
from src.models.project import db, LearningActivity
from datetime import datetime, timedelta
import json
import random

learning_bp = Blueprint('learning', __name__)

# Sample learning activities to populate the database
SAMPLE_ACTIVITIES = [
    {
        'activity_type': 'discovery',
        'description': 'Discovered new IoT sensor technology with 40% better accuracy',
        'timestamp': datetime.now() - timedelta(minutes=2)
    },
    {
        'activity_type': 'merge',
        'description': "Merged concepts: 'smart lighting' + 'motion detection'",
        'timestamp': datetime.now() - timedelta(minutes=5)
    },
    {
        'activity_type': 'price',
        'description': 'Updated component prices from 3 suppliers',
        'timestamp': datetime.now() - timedelta(minutes=10)
    },
    {
        'activity_type': 'feedback',
        'description': 'Learned from user feedback on drone project',
        'timestamp': datetime.now() - timedelta(minutes=15)
    },
    {
        'activity_type': 'generation',
        'description': 'Generated new project: Smart Plant Watering System',
        'timestamp': datetime.now() - timedelta(minutes=20)
    },
    {
        'activity_type': 'discovery',
        'description': 'Found 25% cheaper alternative for Arduino-compatible boards',
        'timestamp': datetime.now() - timedelta(minutes=25)
    },
    {
        'activity_type': 'merge',
        'description': "Successfully merged 'plant care' + 'AI vision' = Smart Garden Monitor",
        'timestamp': datetime.now() - timedelta(minutes=30)
    }
]

@learning_bp.route('/learning/stats', methods=['GET'])
def get_learning_stats():
    """Get AI learning statistics"""
    try:
        # Simulate real-time learning stats
        base_stats = {
            'projects_learned': 1247,
            'concepts_merged': 89,
            'prices_updated': 3421,
            'user_feedback': 156
        }
        
        # Add some randomness to simulate real-time updates
        stats = {
            'projects_learned': base_stats['projects_learned'] + random.randint(0, 5),
            'concepts_merged': base_stats['concepts_merged'] + random.randint(0, 2),
            'prices_updated': base_stats['prices_updated'] + random.randint(0, 50),
            'user_feedback': base_stats['user_feedback'] + random.randint(0, 3)
        }
        
        # Calculate daily increases
        daily_increases = {
            'projects_learned': 23,
            'concepts_merged': 5,
            'prices_updated': 127,
            'user_feedback': 8
        }
        
        return jsonify({
            'stats': stats,
            'daily_increases': daily_increases
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@learning_bp.route('/learning/activities', methods=['GET'])
def get_learning_activities():
    """Get recent learning activities"""
    try:
        # Initialize database with sample data if empty
        if LearningActivity.query.count() == 0:
            for activity_data in SAMPLE_ACTIVITIES:
                activity = LearningActivity(
                    activity_type=activity_data['activity_type'],
                    description=activity_data['description'],
                    timestamp=activity_data['timestamp']
                )
                db.session.add(activity)
            db.session.commit()
        
        # Get recent activities
        activities = LearningActivity.query.order_by(LearningActivity.timestamp.desc()).limit(10).all()
        
        # Format activities with relative time
        formatted_activities = []
        for activity in activities:
            time_diff = datetime.now() - activity.timestamp
            
            if time_diff.total_seconds() < 60:
                time_str = f"{int(time_diff.total_seconds())} seconds ago"
            elif time_diff.total_seconds() < 3600:
                time_str = f"{int(time_diff.total_seconds() / 60)} minutes ago"
            elif time_diff.total_seconds() < 86400:
                time_str = f"{int(time_diff.total_seconds() / 3600)} hours ago"
            else:
                time_str = f"{int(time_diff.total_seconds() / 86400)} days ago"
            
            formatted_activities.append({
                'id': activity.id,
                'type': activity.activity_type,
                'activity': activity.description,
                'time': time_str
            })
        
        return jsonify(formatted_activities)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@learning_bp.route('/learning/progress', methods=['GET'])
def get_learning_progress():
    """Get AI learning progress metrics"""
    try:
        # Simulate learning progress with some randomness
        base_progress = {
            'web_discovery': 87,
            'concept_integration': 92,
            'price_optimization': 78,
            'user_adaptation': 95
        }
        
        # Add slight variations to simulate real-time progress
        progress = {
            key: min(100, value + random.randint(-2, 3))
            for key, value in base_progress.items()
        }
        
        return jsonify(progress)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@learning_bp.route('/learning/discoveries', methods=['GET'])
def get_recent_discoveries():
    """Get recent AI discoveries"""
    try:
        discoveries = [
            {
                'title': 'New IoT Sensor',
                'description': 'Discovered advanced environmental sensor with 40% better accuracy',
                'type': 'discovery',
                'impact': 'high',
                'timestamp': datetime.now() - timedelta(hours=2)
            },
            {
                'title': 'Cost Optimization',
                'description': 'Found 25% cheaper alternative for Arduino-compatible boards',
                'type': 'price',
                'impact': 'medium',
                'timestamp': datetime.now() - timedelta(hours=4)
            },
            {
                'title': 'Concept Merge',
                'description': "Successfully merged 'plant care' + 'AI vision' = Smart Garden Monitor",
                'type': 'merge',
                'impact': 'high',
                'timestamp': datetime.now() - timedelta(hours=6)
            },
            {
                'title': 'New Technology Trend',
                'description': 'Identified emerging trend in edge AI computing for IoT devices',
                'type': 'discovery',
                'impact': 'high',
                'timestamp': datetime.now() - timedelta(hours=8)
            },
            {
                'title': 'Component Alternative',
                'description': 'Found compatible sensor with 30% lower power consumption',
                'type': 'price',
                'impact': 'medium',
                'timestamp': datetime.now() - timedelta(hours=12)
            }
        ]
        
        # Format discoveries
        formatted_discoveries = []
        for discovery in discoveries:
            time_diff = datetime.now() - discovery['timestamp']
            
            if time_diff.total_seconds() < 3600:
                time_str = f"{int(time_diff.total_seconds() / 60)} minutes ago"
            elif time_diff.total_seconds() < 86400:
                time_str = f"{int(time_diff.total_seconds() / 3600)} hours ago"
            else:
                time_str = f"{int(time_diff.total_seconds() / 86400)} days ago"
            
            formatted_discoveries.append({
                'title': discovery['title'],
                'description': discovery['description'],
                'type': discovery['type'],
                'impact': discovery['impact'],
                'time': time_str
            })
        
        return jsonify(formatted_discoveries)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@learning_bp.route('/learning/add-activity', methods=['POST'])
def add_learning_activity():
    """Add a new learning activity"""
    try:
        data = request.get_json()
        activity_type = data.get('type', 'discovery')
        description = data.get('description', '')
        
        if not description:
            return jsonify({'error': 'Description is required'}), 400
        
        activity = LearningActivity(
            activity_type=activity_type,
            description=description,
            timestamp=datetime.now()
        )
        
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({
            'message': 'Learning activity added successfully',
            'activity': activity.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@learning_bp.route('/learning/knowledge-graph', methods=['GET'])
def get_knowledge_graph():
    """Get AI knowledge graph data"""
    try:
        # Simulate knowledge graph with nodes and connections
        knowledge_graph = {
            'nodes': [
                {'id': 'arduino', 'label': 'Arduino', 'category': 'hardware', 'connections': 15},
                {'id': 'raspberry_pi', 'label': 'Raspberry Pi', 'category': 'hardware', 'connections': 12},
                {'id': 'sensors', 'label': 'Sensors', 'category': 'components', 'connections': 20},
                {'id': 'iot', 'label': 'IoT', 'category': 'concept', 'connections': 18},
                {'id': 'ai', 'label': 'Artificial Intelligence', 'category': 'concept', 'connections': 14},
                {'id': 'robotics', 'label': 'Robotics', 'category': 'field', 'connections': 16},
                {'id': 'automation', 'label': 'Home Automation', 'category': 'application', 'connections': 13}
            ],
            'connections': [
                {'source': 'arduino', 'target': 'sensors', 'strength': 0.9},
                {'source': 'raspberry_pi', 'target': 'iot', 'strength': 0.8},
                {'source': 'ai', 'target': 'robotics', 'strength': 0.7},
                {'source': 'sensors', 'target': 'automation', 'strength': 0.8},
                {'source': 'iot', 'target': 'automation', 'strength': 0.9}
            ]
        }
        
        return jsonify(knowledge_graph)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@learning_bp.route('/learning/performance-metrics', methods=['GET'])
def get_performance_metrics():
    """Get AI performance metrics over time"""
    try:
        # Simulate performance metrics
        metrics = {
            'accuracy_trend': [
                {'date': '2024-01-01', 'accuracy': 85.2},
                {'date': '2024-01-02', 'accuracy': 86.1},
                {'date': '2024-01-03', 'accuracy': 87.3},
                {'date': '2024-01-04', 'accuracy': 88.0},
                {'date': '2024-01-05', 'accuracy': 89.2},
                {'date': '2024-01-06', 'accuracy': 90.1},
                {'date': '2024-01-07', 'accuracy': 91.5}
            ],
            'learning_speed': {
                'concepts_per_hour': 12.5,
                'projects_analyzed_per_day': 45,
                'price_updates_per_hour': 8.3
            },
            'user_satisfaction': {
                'current_rating': 4.8,
                'improvement_rate': 0.2,
                'feedback_volume': 156
            }
        }
        
        return jsonify(metrics)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

