"""
Enhanced Human-AI Collaboration Interface
Creates a more natural, Jarvis-like interaction experience with advanced conversational AI,
multi-modal input processing, and contextual understanding for the ultimate lazy genius experience.
"""

import json
import sqlite3
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import base64
import io
from PIL import Image
import speech_recognition as sr
import pyttsx3
import threading
import queue
import time
import re
from dataclasses import dataclass
from enum import Enum

class InteractionMode(Enum):
    TEXT = "text"
    VOICE = "voice"
    IMAGE = "image"
    MULTIMODAL = "multimodal"

class ConversationContext(Enum):
    GENERAL = "general"
    PROJECT_DESIGN = "project_design"
    HOME_AUTOMATION = "home_automation"
    PROBLEM_SOLVING = "problem_solving"
    SHOPPING = "shopping"
    MAINTENANCE = "maintenance"

@dataclass
class UserIntent:
    primary_intent: str
    confidence: float
    entities: Dict[str, Any]
    context: ConversationContext
    urgency: int  # 1-5 scale

class HumanAICollaborationInterface:
    def __init__(self, db_path: str = "collaboration.db"):
        self.db_path = db_path
        self.init_database()
        
        # Voice interaction setup
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.voice_enabled = True
        
        # Conversation state
        self.conversation_history = []
        self.current_context = ConversationContext.GENERAL
        self.user_preferences = {}
        self.active_projects = []
        
        # Multi-modal processing
        self.image_analysis_enabled = True
        self.voice_commands_enabled = True
        
        # Jarvis-like personality settings
        self.personality_traits = {
            "formality": "casual",  # casual, professional, friendly
            "verbosity": "concise",  # brief, concise, detailed
            "humor": "subtle",      # none, subtle, witty
            "proactivity": "high"   # low, medium, high
        }
        
    def init_database(self):
        """Initialize the collaboration interface database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversation history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                user_input TEXT,
                user_input_type TEXT,
                ai_response TEXT,
                context_type TEXT,
                intent_detected TEXT,
                confidence_score REAL,
                response_time_ms INTEGER,
                user_satisfaction INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                preference_category TEXT NOT NULL,
                preference_key TEXT NOT NULL,
                preference_value TEXT,
                confidence_level REAL DEFAULT 0.5,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(preference_category, preference_key)
            )
        ''')
        
        # Intent patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS intent_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intent_name TEXT NOT NULL,
                pattern_text TEXT NOT NULL,
                pattern_type TEXT DEFAULT 'keyword',
                confidence_weight REAL DEFAULT 1.0,
                context_applicable TEXT,
                example_phrases TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Contextual responses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contextual_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                context_type TEXT NOT NULL,
                intent_type TEXT NOT NULL,
                response_template TEXT NOT NULL,
                personality_variant TEXT,
                success_rate REAL DEFAULT 0.0,
                usage_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Multi-modal interactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS multimodal_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                interaction_type TEXT,
                input_modalities TEXT,
                image_data BLOB,
                audio_data BLOB,
                text_input TEXT,
                analysis_results TEXT,
                ai_interpretation TEXT,
                response_generated TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Learning feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interaction_id INTEGER,
                feedback_type TEXT,
                feedback_value TEXT,
                improvement_suggestion TEXT,
                user_rating INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Populate with default patterns and responses
        self._populate_default_patterns()
    
    def _populate_default_patterns(self):
        """Populate database with default intent patterns and responses"""
        default_patterns = [
            {
                "intent_name": "project_request",
                "patterns": [
                    "I want to build", "Can you help me create", "How do I make",
                    "Design a", "I need a project for", "Build me a"
                ],
                "context": "project_design"
            },
            {
                "intent_name": "home_automation",
                "patterns": [
                    "automate my", "control my", "smart home", "turn on", "turn off",
                    "schedule", "optimize energy", "heating", "lighting"
                ],
                "context": "home_automation"
            },
            {
                "intent_name": "problem_solving",
                "patterns": [
                    "I have a problem", "something is broken", "not working",
                    "fix", "repair", "troubleshoot", "issue with"
                ],
                "context": "problem_solving"
            },
            {
                "intent_name": "shopping_assistance",
                "patterns": [
                    "find me", "where can I buy", "cheapest", "best price",
                    "compare prices", "order", "purchase"
                ],
                "context": "shopping"
            },
            {
                "intent_name": "information_request",
                "patterns": [
                    "what is", "how does", "explain", "tell me about",
                    "information on", "details about"
                ],
                "context": "general"
            }
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for intent_group in default_patterns:
            for pattern in intent_group["patterns"]:
                cursor.execute('''
                    INSERT OR IGNORE INTO intent_patterns 
                    (intent_name, pattern_text, context_applicable)
                    VALUES (?, ?, ?)
                ''', (intent_group["intent_name"], pattern, intent_group["context"]))
        
        # Default contextual responses
        default_responses = [
            {
                "context": "project_design",
                "intent": "project_request",
                "template": "I'd be delighted to help you build that! Let me analyze your requirements and design the perfect solution. What's your budget and skill level?",
                "personality": "enthusiastic"
            },
            {
                "context": "home_automation",
                "intent": "home_automation",
                "template": "Excellent choice! I can optimize that for maximum laziness and efficiency. Let me check your current setup and suggest the best approach.",
                "personality": "confident"
            },
            {
                "context": "problem_solving",
                "intent": "problem_solving",
                "template": "Don't worry, I'll help you fix that right away. Let me run diagnostics and find the most cost-effective solution.",
                "personality": "reassuring"
            },
            {
                "context": "shopping",
                "intent": "shopping_assistance",
                "template": "I'm already scanning for the best deals! Give me a moment to find you the cheapest options with the best quality.",
                "personality": "efficient"
            }
        ]
        
        for response in default_responses:
            cursor.execute('''
                INSERT OR IGNORE INTO contextual_responses 
                (context_type, intent_type, response_template, personality_variant)
                VALUES (?, ?, ?, ?)
            ''', (response["context"], response["intent"], response["template"], response["personality"]))
        
        conn.commit()
        conn.close()
    
    def process_user_input(self, input_text: str = None, image_data: bytes = None,
                          audio_data: bytes = None, session_id: str = None) -> Dict:
        """Process multi-modal user input and generate appropriate response"""
        start_time = time.time()
        
        if not session_id:
            session_id = f"session_{int(time.time())}"
        
        # Determine input modalities
        modalities = []
        if input_text:
            modalities.append("text")
        if image_data:
            modalities.append("image")
        if audio_data:
            modalities.append("audio")
        
        interaction_type = "multimodal" if len(modalities) > 1 else modalities[0] if modalities else "unknown"
        
        # Process each modality
        processed_input = {
            "text": input_text,
            "image_analysis": None,
            "audio_transcription": None
        }
        
        if image_data:
            processed_input["image_analysis"] = self._analyze_image(image_data)
        
        if audio_data:
            processed_input["audio_transcription"] = self._transcribe_audio(audio_data)
        
        # Combine all inputs for comprehensive understanding
        combined_input = self._combine_multimodal_input(processed_input)
        
        # Detect user intent
        intent = self._detect_user_intent(combined_input)
        
        # Generate contextual response
        response = self._generate_contextual_response(intent, combined_input, session_id)
        
        # Calculate response time
        response_time = int((time.time() - start_time) * 1000)
        
        # Store interaction in database
        self._store_interaction(session_id, combined_input, response, intent, response_time, modalities)
        
        return {
            "response": response,
            "intent": intent.__dict__ if hasattr(intent, '__dict__') else str(intent),
            "context": self.current_context.value,
            "response_time_ms": response_time,
            "session_id": session_id,
            "suggestions": self._generate_follow_up_suggestions(intent),
            "voice_response": self._should_use_voice_response(intent)
        }
    
    def _analyze_image(self, image_data: bytes) -> Dict:
        """Analyze uploaded image for context and content"""
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Basic image analysis (in real implementation, use computer vision APIs)
            analysis = {
                "dimensions": image.size,
                "format": image.format,
                "mode": image.mode,
                "detected_objects": [],
                "scene_type": "unknown",
                "text_detected": "",
                "technical_elements": []
            }
            
            # Simulate object detection based on image characteristics
            width, height = image.size
            
            if width > height:
                analysis["scene_type"] = "landscape_or_room"
                analysis["detected_objects"] = ["furniture", "electronics", "room_layout"]
            else:
                analysis["scene_type"] = "portrait_or_component"
                analysis["detected_objects"] = ["electronic_component", "device", "tool"]
            
            # Simulate text detection
            analysis["text_detected"] = "Sample text detected in image"
            
            # Technical element detection
            analysis["technical_elements"] = ["wires", "circuits", "mechanical_parts"]
            
            return analysis
            
        except Exception as e:
            return {"error": f"Image analysis failed: {str(e)}"}
    
    def _transcribe_audio(self, audio_data: bytes) -> Dict:
        """Transcribe audio input to text"""
        try:
            # In real implementation, use speech recognition APIs
            # This is a simulation
            transcription = {
                "text": "Simulated audio transcription",
                "confidence": 0.85,
                "language": "en-GB",
                "duration_seconds": 3.5,
                "speaker_emotion": "neutral",
                "background_noise": "low"
            }
            
            return transcription
            
        except Exception as e:
            return {"error": f"Audio transcription failed: {str(e)}"}
    
    def _combine_multimodal_input(self, processed_input: Dict) -> str:
        """Combine all input modalities into a comprehensive understanding"""
        combined_text = ""
        
        # Start with direct text input
        if processed_input["text"]:
            combined_text += processed_input["text"]
        
        # Add image context
        if processed_input["image_analysis"]:
            img_analysis = processed_input["image_analysis"]
            if "detected_objects" in img_analysis:
                combined_text += f" [Image shows: {', '.join(img_analysis['detected_objects'])}]"
            if "scene_type" in img_analysis:
                combined_text += f" [Scene type: {img_analysis['scene_type']}]"
        
        # Add audio transcription
        if processed_input["audio_transcription"]:
            audio_text = processed_input["audio_transcription"].get("text", "")
            if audio_text and audio_text != "Simulated audio transcription":
                combined_text += f" [Voice: {audio_text}]"
        
        return combined_text.strip()
    
    def _detect_user_intent(self, input_text: str) -> UserIntent:
        """Detect user intent from combined input"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all intent patterns
        cursor.execute('SELECT * FROM intent_patterns')
        patterns = cursor.fetchall()
        
        intent_scores = {}
        detected_entities = {}
        
        input_lower = input_text.lower()
        
        for pattern in patterns:
            intent_name = pattern[1]
            pattern_text = pattern[2].lower()
            confidence_weight = pattern[4]
            
            if pattern_text in input_lower:
                if intent_name not in intent_scores:
                    intent_scores[intent_name] = 0
                intent_scores[intent_name] += confidence_weight
        
        # Determine primary intent
        if intent_scores:
            primary_intent = max(intent_scores, key=intent_scores.get)
            confidence = min(intent_scores[primary_intent] / 3.0, 1.0)  # Normalize
        else:
            primary_intent = "general_inquiry"
            confidence = 0.5
        
        # Extract entities (simplified)
        entities = self._extract_entities(input_text)
        
        # Determine context
        context = self._determine_context(primary_intent, entities)
        
        # Assess urgency
        urgency = self._assess_urgency(input_text, primary_intent)
        
        conn.close()
        
        return UserIntent(
            primary_intent=primary_intent,
            confidence=confidence,
            entities=entities,
            context=context,
            urgency=urgency
        )
    
    def _extract_entities(self, input_text: str) -> Dict[str, Any]:
        """Extract entities from user input"""
        entities = {}
        
        # Budget detection
        budget_pattern = r'£(\d+(?:,\d{3})*(?:\.\d{2})?)'
        budget_matches = re.findall(budget_pattern, input_text)
        if budget_matches:
            entities["budget"] = float(budget_matches[0].replace(',', ''))
        
        # Time detection
        time_patterns = [
            (r'(\d+)\s*days?', 'days'),
            (r'(\d+)\s*weeks?', 'weeks'),
            (r'(\d+)\s*months?', 'months'),
            (r'urgent|asap|immediately', 'urgent'),
            (r'when\s+possible|eventually', 'flexible')
        ]
        
        for pattern, time_type in time_patterns:
            if re.search(pattern, input_text.lower()):
                entities["timeline"] = time_type
                break
        
        # Room/location detection
        rooms = ['kitchen', 'bedroom', 'living room', 'bathroom', 'garden', 'garage', 'office']
        for room in rooms:
            if room in input_text.lower():
                entities["location"] = room
                break
        
        # Skill level detection
        skill_indicators = {
            'beginner': ['new to', 'never done', 'first time', 'beginner'],
            'intermediate': ['some experience', 'done before', 'intermediate'],
            'advanced': ['experienced', 'expert', 'advanced', 'professional']
        }
        
        for level, indicators in skill_indicators.items():
            if any(indicator in input_text.lower() for indicator in indicators):
                entities["skill_level"] = level
                break
        
        return entities
    
    def _determine_context(self, intent: str, entities: Dict) -> ConversationContext:
        """Determine conversation context based on intent and entities"""
        context_mapping = {
            "project_request": ConversationContext.PROJECT_DESIGN,
            "home_automation": ConversationContext.HOME_AUTOMATION,
            "problem_solving": ConversationContext.PROBLEM_SOLVING,
            "shopping_assistance": ConversationContext.SHOPPING,
            "maintenance_request": ConversationContext.MAINTENANCE
        }
        
        return context_mapping.get(intent, ConversationContext.GENERAL)
    
    def _assess_urgency(self, input_text: str, intent: str) -> int:
        """Assess urgency level from 1-5"""
        urgent_keywords = ['urgent', 'asap', 'immediately', 'emergency', 'broken', 'not working']
        high_keywords = ['soon', 'quickly', 'fast', 'today']
        low_keywords = ['eventually', 'when possible', 'no rush', 'sometime']
        
        input_lower = input_text.lower()
        
        if any(keyword in input_lower for keyword in urgent_keywords):
            return 5
        elif any(keyword in input_lower for keyword in high_keywords):
            return 4
        elif intent in ['problem_solving', 'maintenance_request']:
            return 3
        elif any(keyword in input_lower for keyword in low_keywords):
            return 1
        else:
            return 2
    
    def _generate_contextual_response(self, intent: UserIntent, input_text: str, session_id: str) -> str:
        """Generate contextual response based on intent and conversation history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get appropriate response template
        cursor.execute('''
            SELECT response_template, personality_variant FROM contextual_responses 
            WHERE context_type = ? AND intent_type = ?
            ORDER BY success_rate DESC, usage_count ASC
            LIMIT 1
        ''', (intent.context.value, intent.primary_intent))
        
        response_data = cursor.fetchone()
        
        if response_data:
            base_response = response_data[0]
            personality = response_data[1]
        else:
            base_response = "I understand what you're looking for. Let me help you with that."
            personality = "helpful"
        
        # Customize response based on entities and context
        customized_response = self._customize_response(base_response, intent, input_text)
        
        # Add personality touches
        final_response = self._add_personality_touches(customized_response, personality, intent)
        
        # Update response usage statistics
        if response_data:
            cursor.execute('''
                UPDATE contextual_responses 
                SET usage_count = usage_count + 1
                WHERE context_type = ? AND intent_type = ?
            ''', (intent.context.value, intent.primary_intent))
        
        conn.commit()
        conn.close()
        
        return final_response
    
    def _customize_response(self, base_response: str, intent: UserIntent, input_text: str) -> str:
        """Customize response based on specific user entities and context"""
        response = base_response
        
        # Add budget-specific information
        if "budget" in intent.entities:
            budget = intent.entities["budget"]
            if budget < 50:
                response += f" With your £{budget} budget, I'll focus on ultra-low-cost solutions and free alternatives."
            elif budget < 200:
                response += f" Your £{budget} budget gives us good options for quality DIY solutions."
            else:
                response += f" With £{budget} to work with, we can create something really impressive!"
        
        # Add timeline considerations
        if "timeline" in intent.entities:
            timeline = intent.entities["timeline"]
            if timeline == "urgent":
                response += " I'll prioritize quick solutions that you can implement immediately."
            elif timeline in ["days", "weeks"]:
                response += f" I'll design something achievable within your {timeline} timeframe."
        
        # Add location-specific advice
        if "location" in intent.entities:
            location = intent.entities["location"]
            response += f" For your {location}, I'll consider the specific requirements and constraints of that space."
        
        # Add skill level adjustments
        if "skill_level" in intent.entities:
            skill = intent.entities["skill_level"]
            if skill == "beginner":
                response += " I'll provide detailed step-by-step instructions perfect for beginners."
            elif skill == "advanced":
                response += " I can suggest more sophisticated approaches given your experience level."
        
        return response
    
    def _add_personality_touches(self, response: str, personality: str, intent: UserIntent) -> str:
        """Add personality-specific touches to the response"""
        if self.personality_traits["humor"] == "witty" and intent.urgency < 4:
            witty_additions = [
                " (Don't worry, I won't judge your previous DIY attempts!)",
                " (Time to make Tony Stark jealous!)",
                " (Your neighbors are going to be so confused... and impressed!)"
            ]
            import random
            if random.random() < 0.3:  # 30% chance of humor
                response += random.choice(witty_additions)
        
        if self.personality_traits["proactivity"] == "high":
            proactive_additions = [
                " I'm already scanning for the best component prices while we chat.",
                " I'll start monitoring for deals on the parts you'll need.",
                " I'm also checking if there are any similar projects you might be interested in."
            ]
            import random
            response += " " + random.choice(proactive_additions)
        
        if personality == "enthusiastic":
            response = response.replace("I can", "I'd love to")
            response = response.replace("Let me", "Let me absolutely")
        
        return response
    
    def _generate_follow_up_suggestions(self, intent: UserIntent) -> List[str]:
        """Generate follow-up suggestions based on intent"""
        suggestions = []
        
        if intent.context == ConversationContext.PROJECT_DESIGN:
            suggestions = [
                "Would you like me to show you similar projects for inspiration?",
                "Should I check for any tools you might need to borrow or buy?",
                "Want me to create a shopping list with the cheapest suppliers?",
                "Interested in seeing a 3D model of the finished project?"
            ]
        
        elif intent.context == ConversationContext.HOME_AUTOMATION:
            suggestions = [
                "Should I check your current energy usage for optimization opportunities?",
                "Want me to create an automation schedule based on your routine?",
                "Interested in seeing how much money this could save you monthly?",
                "Should I look for compatible devices you already own?"
            ]
        
        elif intent.context == ConversationContext.SHOPPING:
            suggestions = [
                "Want me to set up price alerts for when items go on sale?",
                "Should I check second-hand markets for better deals?",
                "Interested in bulk buying options to save more?",
                "Want me to find alternative brands with similar quality?"
            ]
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    def _should_use_voice_response(self, intent: UserIntent) -> bool:
        """Determine if voice response should be used"""
        if not self.voice_enabled:
            return False
        
        # Use voice for urgent matters or when specifically requested
        if intent.urgency >= 4:
            return True
        
        # Use voice for confirmations and quick responses
        if intent.primary_intent in ["confirmation", "quick_question"]:
            return True
        
        return False
    
    def _store_interaction(self, session_id: str, input_data: str, response: str,
                          intent: UserIntent, response_time: int, modalities: List[str]):
        """Store interaction in database for learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversation_history 
            (session_id, user_input, user_input_type, ai_response, context_type,
             intent_detected, confidence_score, response_time_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id, input_data, ",".join(modalities), response,
            intent.context.value, intent.primary_intent, intent.confidence, response_time
        ))
        
        conn.commit()
        conn.close()
    
    def learn_from_feedback(self, interaction_id: int, feedback_type: str,
                           feedback_value: str, user_rating: int = None):
        """Learn from user feedback to improve responses"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Store feedback
        cursor.execute('''
            INSERT INTO learning_feedback 
            (interaction_id, feedback_type, feedback_value, user_rating)
            VALUES (?, ?, ?, ?)
        ''', (interaction_id, feedback_type, feedback_value, user_rating))
        
        # Update response success rates based on feedback
        if user_rating is not None:
            cursor.execute('''
                SELECT context_type, intent_detected FROM conversation_history 
                WHERE id = ?
            ''', (interaction_id,))
            
            interaction_data = cursor.fetchone()
            if interaction_data:
                context_type, intent_detected = interaction_data
                
                # Update success rate for this response type
                cursor.execute('''
                    UPDATE contextual_responses 
                    SET success_rate = (success_rate * usage_count + ?) / (usage_count + 1)
                    WHERE context_type = ? AND intent_type = ?
                ''', (user_rating * 20, context_type, intent_detected))  # Convert 1-5 to 0-100
        
        conn.commit()
        conn.close()
    
    def get_conversation_analytics(self, session_id: str = None, days: int = 7) -> Dict:
        """Get analytics about conversation patterns and performance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since_date = datetime.now() - timedelta(days=days)
        
        # Base query conditions
        base_conditions = "WHERE created_at > ?"
        params = [since_date]
        
        if session_id:
            base_conditions += " AND session_id = ?"
            params.append(session_id)
        
        # Get conversation statistics
        cursor.execute(f'''
            SELECT 
                COUNT(*) as total_interactions,
                AVG(response_time_ms) as avg_response_time,
                AVG(confidence_score) as avg_confidence,
                COUNT(DISTINCT session_id) as unique_sessions
            FROM conversation_history {base_conditions}
        ''', params)
        
        stats = cursor.fetchone()
        
        # Get intent distribution
        cursor.execute(f'''
            SELECT intent_detected, COUNT(*) as count
            FROM conversation_history {base_conditions}
            GROUP BY intent_detected
            ORDER BY count DESC
        ''', params)
        
        intent_distribution = dict(cursor.fetchall())
        
        # Get context distribution
        cursor.execute(f'''
            SELECT context_type, COUNT(*) as count
            FROM conversation_history {base_conditions}
            GROUP BY context_type
            ORDER BY count DESC
        ''', params)
        
        context_distribution = dict(cursor.fetchall())
        
        # Get user satisfaction (from feedback)
        cursor.execute(f'''
            SELECT AVG(user_rating) as avg_rating, COUNT(*) as feedback_count
            FROM learning_feedback lf
            JOIN conversation_history ch ON lf.interaction_id = ch.id
            {base_conditions.replace('WHERE', 'WHERE ch.')}
        ''', params)
        
        satisfaction_data = cursor.fetchone()
        
        conn.close()
        
        return {
            "period_days": days,
            "total_interactions": stats[0] if stats else 0,
            "average_response_time_ms": round(stats[1], 2) if stats and stats[1] else 0,
            "average_confidence": round(stats[2], 3) if stats and stats[2] else 0,
            "unique_sessions": stats[3] if stats else 0,
            "intent_distribution": intent_distribution,
            "context_distribution": context_distribution,
            "user_satisfaction": {
                "average_rating": round(satisfaction_data[0], 2) if satisfaction_data and satisfaction_data[0] else None,
                "feedback_count": satisfaction_data[1] if satisfaction_data else 0
            }
        }
    
    def update_personality_settings(self, formality: str = None, verbosity: str = None,
                                  humor: str = None, proactivity: str = None):
        """Update AI personality settings"""
        if formality in ["casual", "professional", "friendly"]:
            self.personality_traits["formality"] = formality
        
        if verbosity in ["brief", "concise", "detailed"]:
            self.personality_traits["verbosity"] = verbosity
        
        if humor in ["none", "subtle", "witty"]:
            self.personality_traits["humor"] = humor
        
        if proactivity in ["low", "medium", "high"]:
            self.personality_traits["proactivity"] = proactivity
        
        return {"status": "updated", "current_settings": self.personality_traits}
    
    def simulate_jarvis_interaction(self, user_input: str) -> Dict:
        """Simulate a Jarvis-like interaction with enhanced personality"""
        # Add Jarvis-specific personality touches
        original_traits = self.personality_traits.copy()
        
        # Temporarily adjust for Jarvis-like behavior
        self.personality_traits.update({
            "formality": "casual",
            "verbosity": "concise",
            "humor": "subtle",
            "proactivity": "high"
        })
        
        # Process the input
        response = self.process_user_input(input_text=user_input)
        
        # Add Jarvis-specific enhancements
        jarvis_response = response["response"]
        
        # Add proactive suggestions
        if "project" in user_input.lower():
            jarvis_response += " I'm also running cost optimizations and checking for any bulk purchase opportunities."
        
        if "automate" in user_input.lower():
            jarvis_response += " I'll monitor the implementation and suggest improvements as I learn your patterns."
        
        # Restore original personality
        self.personality_traits = original_traits
        
        response["response"] = jarvis_response
        response["jarvis_mode"] = True
        
        return response

