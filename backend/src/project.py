from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)
    cost = db.Column(db.Float, nullable=False)
    duration = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    tags = db.Column(db.Text, nullable=False)  # JSON string
    rating = db.Column(db.Float, default=0.0)
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    components = db.Column(db.Text, nullable=False)  # JSON string
    skills = db.Column(db.Text, nullable=False)  # JSON string
    code_content = db.Column(db.Text)
    instructions = db.Column(db.Text)
    circuit_diagram = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'difficulty': self.difficulty,
            'cost': self.cost,
            'duration': self.duration,
            'category': self.category,
            'tags': json.loads(self.tags) if self.tags else [],
            'rating': self.rating,
            'views': self.views,
            'likes': self.likes,
            'components': json.loads(self.components) if self.components else [],
            'skills': json.loads(self.skills) if self.skills else [],
            'code_content': self.code_content,
            'instructions': self.instructions,
            'circuit_diagram': self.circuit_diagram,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class LearningActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    activity_type = db.Column(db.String(50), nullable=False)  # discovery, merge, price, feedback, generation
    description = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    activity_metadata = db.Column(db.Text)  # JSON string for additional data
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.activity_type,
            'activity': self.description,
            'time': self.timestamp.strftime('%d minutes ago') if self.timestamp else 'Unknown',
            'metadata': json.loads(self.activity_metadata) if self.activity_metadata else {}
        }

class CommunityPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    user_avatar = db.Column(db.String(10), nullable=False)
    content = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user_name,
            'avatar': self.user_avatar,
            'content': self.content,
            'likes': self.likes,
            'comments': self.comments,
            'time': self.timestamp.strftime('%d hours ago') if self.timestamp else 'Unknown'
        }

