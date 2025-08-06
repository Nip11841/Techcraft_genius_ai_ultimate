from flask import Blueprint, jsonify, request
from src.models.project import db, CommunityPost
from datetime import datetime, timedelta
import random

community_bp = Blueprint('community', __name__)

# Sample community posts to populate the database
SAMPLE_POSTS = [
    {
        'user_name': 'Alex Chen',
        'user_avatar': 'AC',
        'content': "Just completed the Smart Home Security System! The AI's component suggestions saved me $50. Here's my build process and some tips for anyone starting this project...",
        'likes': 24,
        'comments': 8,
        'timestamp': datetime.now() - timedelta(hours=2)
    },
    {
        'user_name': 'Sarah Kim',
        'user_avatar': 'SK',
        'content': "The AI suggested merging 'plant monitoring' with 'weather prediction' - resulted in an amazing automated greenhouse system! The concept merging feature is incredible.",
        'likes': 31,
        'comments': 12,
        'timestamp': datetime.now() - timedelta(hours=4)
    },
    {
        'user_name': 'Mike Johnson',
        'user_avatar': 'MJ',
        'content': "Thanks to the cost optimization feature, I built the flying robot for under $200. The AI found cheaper alternatives for every component! Sharing my parts list...",
        'likes': 45,
        'comments': 15,
        'timestamp': datetime.now() - timedelta(hours=6)
    },
    {
        'user_name': 'Emma Davis',
        'user_avatar': 'ED',
        'content': "The learning dashboard is fascinating! Watching the AI discover new technologies in real-time gives me so many project ideas. Just saw it merge 'solar power' + 'IoT sensors'.",
        'likes': 18,
        'comments': 6,
        'timestamp': datetime.now() - timedelta(hours=8)
    },
    {
        'user_name': 'David Wilson',
        'user_avatar': 'DW',
        'content': "Built my first Arduino project using the voice-controlled LED matrix guide. The step-by-step instructions were perfect for a beginner like me. Now planning something more advanced!",
        'likes': 22,
        'comments': 9,
        'timestamp': datetime.now() - timedelta(hours=12)
    }
]

@community_bp.route('/community/posts', methods=['GET'])
def get_community_posts():
    """Get community posts"""
    try:
        # Initialize database with sample data if empty
        if CommunityPost.query.count() == 0:
            for post_data in SAMPLE_POSTS:
                post = CommunityPost(
                    user_name=post_data['user_name'],
                    user_avatar=post_data['user_avatar'],
                    content=post_data['content'],
                    likes=post_data['likes'],
                    comments=post_data['comments'],
                    timestamp=post_data['timestamp']
                )
                db.session.add(post)
            db.session.commit()
        
        # Get posts with pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        posts = CommunityPost.query.order_by(CommunityPost.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Format posts with relative time
        formatted_posts = []
        for post in posts.items:
            time_diff = datetime.now() - post.timestamp
            
            if time_diff.total_seconds() < 3600:
                time_str = f"{int(time_diff.total_seconds() / 60)} minutes ago"
            elif time_diff.total_seconds() < 86400:
                time_str = f"{int(time_diff.total_seconds() / 3600)} hours ago"
            else:
                time_str = f"{int(time_diff.total_seconds() / 86400)} days ago"
            
            formatted_posts.append({
                'id': post.id,
                'user': post.user_name,
                'avatar': post.user_avatar,
                'content': post.content,
                'likes': post.likes,
                'comments': post.comments,
                'time': time_str
            })
        
        return jsonify({
            'posts': formatted_posts,
            'total': posts.total,
            'pages': posts.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@community_bp.route('/community/stats', methods=['GET'])
def get_community_stats():
    """Get community statistics"""
    try:
        # Simulate community stats with some randomness
        base_stats = {
            'active_members': 12847,
            'projects_shared': 3291,
            'success_stories': 1156,
            'ai_improvements': 847
        }
        
        # Add slight variations to simulate real-time updates
        stats = {
            'active_members': base_stats['active_members'] + random.randint(0, 10),
            'projects_shared': base_stats['projects_shared'] + random.randint(0, 5),
            'success_stories': base_stats['success_stories'] + random.randint(0, 3),
            'ai_improvements': base_stats['ai_improvements'] + random.randint(0, 2)
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@community_bp.route('/community/top-contributors', methods=['GET'])
def get_top_contributors():
    """Get top community contributors"""
    try:
        contributors = [
            {
                'name': 'Alex Chen',
                'avatar': 'AC',
                'projects': 23,
                'contributions': 45,
                'reputation': 892,
                'badge': 'Expert Maker'
            },
            {
                'name': 'Sarah Kim',
                'avatar': 'SK',
                'projects': 19,
                'contributions': 38,
                'reputation': 756,
                'badge': 'AI Enthusiast'
            },
            {
                'name': 'Mike Johnson',
                'avatar': 'MJ',
                'projects': 17,
                'contributions': 32,
                'reputation': 689,
                'badge': 'Robotics Pro'
            },
            {
                'name': 'Emma Davis',
                'avatar': 'ED',
                'projects': 15,
                'contributions': 28,
                'reputation': 612,
                'badge': 'IoT Specialist'
            },
            {
                'name': 'David Wilson',
                'avatar': 'DW',
                'projects': 12,
                'contributions': 24,
                'reputation': 534,
                'badge': 'Rising Star'
            }
        ]
        
        return jsonify(contributors)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@community_bp.route('/community/posts/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    """Like a community post"""
    try:
        post = CommunityPost.query.get_or_404(post_id)
        post.likes += 1
        db.session.commit()
        
        return jsonify({'likes': post.likes})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@community_bp.route('/community/posts', methods=['POST'])
def create_post():
    """Create a new community post"""
    try:
        data = request.get_json()
        user_name = data.get('user_name', 'Anonymous')
        content = data.get('content', '')
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        # Generate avatar initials
        avatar = ''.join([word[0].upper() for word in user_name.split()[:2]])
        
        post = CommunityPost(
            user_name=user_name,
            user_avatar=avatar,
            content=content,
            likes=0,
            comments=0,
            timestamp=datetime.now()
        )
        
        db.session.add(post)
        db.session.commit()
        
        return jsonify({
            'message': 'Post created successfully',
            'post': post.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@community_bp.route('/community/trending', methods=['GET'])
def get_trending_topics():
    """Get trending topics in the community"""
    try:
        trending_topics = [
            {
                'topic': 'Smart Home Automation',
                'posts': 156,
                'growth': '+23%',
                'category': 'IoT'
            },
            {
                'topic': 'AI-Powered Robotics',
                'posts': 134,
                'growth': '+18%',
                'category': 'Robotics'
            },
            {
                'topic': 'Cost Optimization Tips',
                'posts': 98,
                'growth': '+15%',
                'category': 'Budget'
            },
            {
                'topic': 'Arduino Projects',
                'posts': 89,
                'growth': '+12%',
                'category': 'Hardware'
            },
            {
                'topic': 'Concept Merging Ideas',
                'posts': 76,
                'growth': '+28%',
                'category': 'Innovation'
            }
        ]
        
        return jsonify(trending_topics)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@community_bp.route('/community/challenges', methods=['GET'])
def get_community_challenges():
    """Get current community challenges"""
    try:
        challenges = [
            {
                'id': 1,
                'title': 'Build Under $50 Challenge',
                'description': 'Create an innovative project using components under $50',
                'participants': 234,
                'deadline': '2024-02-15',
                'prize': 'Featured Project + $100 Gift Card',
                'difficulty': 'All Levels'
            },
            {
                'id': 2,
                'title': 'AI Concept Merge Contest',
                'description': 'Use our AI to merge two concepts into a unique project',
                'participants': 189,
                'deadline': '2024-02-28',
                'prize': 'AI Learning Credits + Recognition',
                'difficulty': 'Intermediate'
            },
            {
                'id': 3,
                'title': 'Sustainable Tech Project',
                'description': 'Build an eco-friendly project using renewable energy',
                'participants': 156,
                'deadline': '2024-03-10',
                'prize': 'Solar Panel Kit + Feature Article',
                'difficulty': 'Advanced'
            }
        ]
        
        return jsonify(challenges)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@community_bp.route('/community/events', methods=['GET'])
def get_community_events():
    """Get upcoming community events"""
    try:
        events = [
            {
                'id': 1,
                'title': 'Virtual Maker Meetup',
                'description': 'Monthly online gathering to share projects and ideas',
                'date': '2024-02-10',
                'time': '19:00 UTC',
                'attendees': 145,
                'type': 'Virtual'
            },
            {
                'id': 2,
                'title': 'AI Workshop: Advanced Concept Merging',
                'description': 'Learn advanced techniques for creative project generation',
                'date': '2024-02-17',
                'time': '15:00 UTC',
                'attendees': 89,
                'type': 'Workshop'
            },
            {
                'id': 3,
                'title': 'Robotics Competition Prep',
                'description': 'Prepare for the upcoming robotics challenge',
                'date': '2024-02-24',
                'time': '18:00 UTC',
                'attendees': 67,
                'type': 'Competition'
            }
        ]
        
        return jsonify(events)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

