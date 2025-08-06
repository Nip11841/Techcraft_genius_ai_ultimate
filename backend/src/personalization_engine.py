"""
Hyper-Personalization & Contextual Intelligence Engine
Advanced personalization system for individual family members and contextual automation
"""

import json
import time
import logging
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
from collections import defaultdict, deque
import statistics
import hashlib

class PersonalityType(Enum):
    TECH_ENTHUSIAST = "tech_enthusiast"
    COMFORT_SEEKER = "comfort_seeker"
    EFFICIENCY_FOCUSED = "efficiency_focused"
    ENVIRONMENTALIST = "environmentalist"
    MINIMALIST = "minimalist"
    FAMILY_ORIENTED = "family_oriented"

class ContextType(Enum):
    WEATHER = "weather"
    TIME_OF_DAY = "time_of_day"
    SOCIAL = "social"
    WORK = "work"
    HEALTH = "health"
    SEASONAL = "seasonal"
    EMERGENCY = "emergency"

class PreferenceCategory(Enum):
    LIGHTING = "lighting"
    TEMPERATURE = "temperature"
    MUSIC = "music"
    SECURITY = "security"
    ENERGY = "energy"
    COMFORT = "comfort"
    PRODUCTIVITY = "productivity"

@dataclass
class FamilyMember:
    id: str
    name: str
    age: int
    personality_type: PersonalityType
    preferences: Dict[str, Any]
    schedule: Dict[str, Any]
    health_data: Dict[str, Any]
    learning_style: str
    skill_level: str  # beginner, intermediate, advanced
    interests: List[str]
    accessibility_needs: List[str]
    privacy_level: str  # low, medium, high
    automation_comfort: float  # 0-1 scale
    created_date: datetime
    last_updated: datetime

@dataclass
class PersonalPreference:
    id: str
    member_id: str
    category: PreferenceCategory
    preference_data: Dict[str, Any]
    confidence: float  # 0-1
    context_dependent: bool
    seasonal_variation: bool
    time_dependent: bool
    learned_from: str  # manual, observed, inferred
    priority: int  # 1-10
    last_updated: datetime

@dataclass
class ContextualRule:
    id: str
    name: str
    context_type: ContextType
    conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    affected_members: List[str]
    priority: int
    active: bool
    success_rate: float
    created_date: datetime

@dataclass
class PersonalizedRecommendation:
    id: str
    member_id: str
    recommendation_type: str
    title: str
    description: str
    benefits: List[str]
    implementation_steps: List[str]
    estimated_cost: float
    difficulty_level: str
    time_to_implement: int  # hours
    personalization_score: float  # 0-1
    context_relevance: float  # 0-1
    created_date: datetime

@dataclass
class AdaptiveBehavior:
    id: str
    behavior_name: str
    trigger_conditions: Dict[str, Any]
    adaptation_rules: List[Dict[str, Any]]
    learning_rate: float
    confidence: float
    success_count: int
    failure_count: int
    last_executed: datetime

class PersonalizationEngine:
    def __init__(self, db_path: str = "personalization_data.db"):
        self.db_path = db_path
        self.family_members: Dict[str, FamilyMember] = {}
        self.preferences: Dict[str, PersonalPreference] = {}
        self.contextual_rules: Dict[str, ContextualRule] = {}
        self.recommendations: Dict[str, PersonalizedRecommendation] = {}
        self.adaptive_behaviors: Dict[str, AdaptiveBehavior] = {}
        
        # Context tracking
        self.current_context = {}
        self.context_history = deque(maxlen=1000)
        
        # Learning data
        self.interaction_history = defaultdict(deque)
        self.preference_learning_data = defaultdict(list)
        
        self.init_database()
        self.load_data()
        self.initialize_sample_members()
        self.start_personalization_engine()
    
    def init_database(self):
        """Initialize SQLite database for personalization data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS family_members (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                personality_type TEXT NOT NULL,
                preferences TEXT NOT NULL,
                schedule TEXT NOT NULL,
                health_data TEXT NOT NULL,
                learning_style TEXT NOT NULL,
                skill_level TEXT NOT NULL,
                interests TEXT NOT NULL,
                accessibility_needs TEXT NOT NULL,
                privacy_level TEXT NOT NULL,
                automation_comfort REAL NOT NULL,
                created_date TIMESTAMP NOT NULL,
                last_updated TIMESTAMP NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS personal_preferences (
                id TEXT PRIMARY KEY,
                member_id TEXT NOT NULL,
                category TEXT NOT NULL,
                preference_data TEXT NOT NULL,
                confidence REAL NOT NULL,
                context_dependent BOOLEAN NOT NULL,
                seasonal_variation BOOLEAN NOT NULL,
                time_dependent BOOLEAN NOT NULL,
                learned_from TEXT NOT NULL,
                priority INTEGER NOT NULL,
                last_updated TIMESTAMP NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contextual_rules (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                context_type TEXT NOT NULL,
                conditions TEXT NOT NULL,
                actions TEXT NOT NULL,
                affected_members TEXT NOT NULL,
                priority INTEGER NOT NULL,
                active BOOLEAN NOT NULL,
                success_rate REAL NOT NULL,
                created_date TIMESTAMP NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS personalized_recommendations (
                id TEXT PRIMARY KEY,
                member_id TEXT NOT NULL,
                recommendation_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                benefits TEXT NOT NULL,
                implementation_steps TEXT NOT NULL,
                estimated_cost REAL NOT NULL,
                difficulty_level TEXT NOT NULL,
                time_to_implement INTEGER NOT NULL,
                personalization_score REAL NOT NULL,
                context_relevance REAL NOT NULL,
                created_date TIMESTAMP NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS adaptive_behaviors (
                id TEXT PRIMARY KEY,
                behavior_name TEXT NOT NULL,
                trigger_conditions TEXT NOT NULL,
                adaptation_rules TEXT NOT NULL,
                learning_rate REAL NOT NULL,
                confidence REAL NOT NULL,
                success_count INTEGER NOT NULL,
                failure_count INTEGER NOT NULL,
                last_executed TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interaction_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                interaction_type TEXT NOT NULL,
                device_id TEXT,
                action TEXT NOT NULL,
                context TEXT,
                satisfaction_score REAL,
                notes TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS context_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP NOT NULL,
                context_type TEXT NOT NULL,
                context_data TEXT NOT NULL,
                triggered_rules TEXT,
                affected_members TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def initialize_sample_members(self):
        """Initialize sample family members"""
        sample_members = [
            FamilyMember(
                id="member_001",
                name="Alex",
                age=35,
                personality_type=PersonalityType.TECH_ENTHUSIAST,
                preferences={
                    "wake_time": "07:00",
                    "sleep_time": "23:30",
                    "preferred_temperature": 21.0,
                    "lighting_preference": "bright_white",
                    "music_genre": "electronic",
                    "work_environment": "quiet_focused"
                },
                schedule={
                    "work_days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
                    "work_hours": {"start": "09:00", "end": "17:30"},
                    "lunch_time": "12:30",
                    "exercise_time": "18:30",
                    "weekend_routine": "flexible"
                },
                health_data={
                    "fitness_level": "moderate",
                    "sleep_quality_target": 8.0,
                    "stress_indicators": ["late_work", "poor_sleep"],
                    "allergies": [],
                    "medications": []
                },
                learning_style="hands_on",
                skill_level="advanced",
                interests=["smart_home", "programming", "renewable_energy", "automation"],
                accessibility_needs=[],
                privacy_level="medium",
                automation_comfort=0.9,
                created_date=datetime.now(),
                last_updated=datetime.now()
            ),
            FamilyMember(
                id="member_002",
                name="Sam",
                age=32,
                personality_type=PersonalityType.COMFORT_SEEKER,
                preferences={
                    "wake_time": "07:30",
                    "sleep_time": "22:45",
                    "preferred_temperature": 22.5,
                    "lighting_preference": "warm_soft",
                    "music_genre": "ambient",
                    "work_environment": "comfortable_cozy"
                },
                schedule={
                    "work_days": ["monday", "tuesday", "wednesday", "thursday"],
                    "work_hours": {"start": "10:00", "end": "18:00"},
                    "lunch_time": "13:00",
                    "relaxation_time": "19:00",
                    "weekend_routine": "leisurely"
                },
                health_data={
                    "fitness_level": "light",
                    "sleep_quality_target": 8.5,
                    "stress_indicators": ["noise", "bright_lights"],
                    "allergies": ["dust"],
                    "medications": []
                },
                learning_style="visual",
                skill_level="intermediate",
                interests=["cooking", "gardening", "wellness", "interior_design"],
                accessibility_needs=[],
                privacy_level="high",
                automation_comfort=0.7,
                created_date=datetime.now(),
                last_updated=datetime.now()
            ),
            FamilyMember(
                id="member_003",
                name="Jordan",
                age=16,
                personality_type=PersonalityType.EFFICIENCY_FOCUSED,
                preferences={
                    "wake_time": "06:45",
                    "sleep_time": "22:00",
                    "preferred_temperature": 20.0,
                    "lighting_preference": "adaptive",
                    "music_genre": "study_focus",
                    "work_environment": "organized_minimal"
                },
                schedule={
                    "school_days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
                    "school_hours": {"start": "08:30", "end": "15:30"},
                    "study_time": "16:00",
                    "sports_time": "17:30",
                    "weekend_routine": "structured"
                },
                health_data={
                    "fitness_level": "high",
                    "sleep_quality_target": 9.0,
                    "stress_indicators": ["exam_periods", "social_pressure"],
                    "allergies": [],
                    "medications": []
                },
                learning_style="analytical",
                skill_level="intermediate",
                interests=["robotics", "gaming", "sports", "science"],
                accessibility_needs=[],
                privacy_level="medium",
                automation_comfort=0.8,
                created_date=datetime.now(),
                last_updated=datetime.now()
            )
        ]
        
        for member in sample_members:
            self.family_members[member.id] = member
            self.save_family_member(member)
            
            # Generate initial preferences for each member
            self.generate_initial_preferences(member)
    
    def generate_initial_preferences(self, member: FamilyMember):
        """Generate initial preferences based on member profile"""
        preferences = []
        
        # Lighting preferences
        lighting_pref = PersonalPreference(
            id=f"pref_lighting_{member.id}_{int(time.time())}",
            member_id=member.id,
            category=PreferenceCategory.LIGHTING,
            preference_data={
                "morning_brightness": 80 if member.personality_type == PersonalityType.TECH_ENTHUSIAST else 60,
                "evening_brightness": 40 if member.personality_type == PersonalityType.COMFORT_SEEKER else 50,
                "color_temperature": {
                    "morning": 6500 if member.personality_type == PersonalityType.EFFICIENCY_FOCUSED else 4000,
                    "evening": 2700,
                    "night": 2200
                },
                "adaptive_lighting": member.automation_comfort > 0.7,
                "motion_activation": member.automation_comfort > 0.6
            },
            confidence=0.7,
            context_dependent=True,
            seasonal_variation=True,
            time_dependent=True,
            learned_from="profile_based",
            priority=8,
            last_updated=datetime.now()
        )
        preferences.append(lighting_pref)
        
        # Temperature preferences
        temp_pref = PersonalPreference(
            id=f"pref_temp_{member.id}_{int(time.time())}",
            member_id=member.id,
            category=PreferenceCategory.TEMPERATURE,
            preference_data={
                "base_temperature": member.preferences.get("preferred_temperature", 21.0),
                "sleep_offset": -1.5,
                "away_offset": -3.0,
                "humidity_preference": 45 + (member.age - 30) * 0.5,  # Slight age adjustment
                "adaptive_scheduling": member.automation_comfort > 0.6,
                "zone_preferences": {
                    "bedroom": member.preferences.get("preferred_temperature", 21.0) - 1.0,
                    "living_room": member.preferences.get("preferred_temperature", 21.0),
                    "office": member.preferences.get("preferred_temperature", 21.0) + 0.5
                }
            },
            confidence=0.8,
            context_dependent=True,
            seasonal_variation=True,
            time_dependent=True,
            learned_from="profile_based",
            priority=9,
            last_updated=datetime.now()
        )
        preferences.append(temp_pref)
        
        # Music preferences
        music_pref = PersonalPreference(
            id=f"pref_music_{member.id}_{int(time.time())}",
            member_id=member.id,
            category=PreferenceCategory.MUSIC,
            preference_data={
                "genres": [member.preferences.get("music_genre", "ambient")],
                "volume_levels": {
                    "morning": 30,
                    "day": 40,
                    "evening": 25,
                    "night": 15
                },
                "context_playlists": {
                    "work": "focus_instrumental",
                    "exercise": "energetic_beats",
                    "relaxation": "ambient_calm",
                    "cooking": "upbeat_casual"
                },
                "auto_play": member.automation_comfort > 0.5
            },
            confidence=0.6,
            context_dependent=True,
            seasonal_variation=False,
            time_dependent=True,
            learned_from="profile_based",
            priority=5,
            last_updated=datetime.now()
        )
        preferences.append(music_pref)
        
        # Security preferences
        security_pref = PersonalPreference(
            id=f"pref_security_{member.id}_{int(time.time())}",
            member_id=member.id,
            category=PreferenceCategory.SECURITY,
            preference_data={
                "notification_level": "high" if member.privacy_level == "high" else "medium",
                "auto_arm": member.automation_comfort > 0.7,
                "facial_recognition": member.privacy_level != "high",
                "guest_access": member.privacy_level == "low",
                "monitoring_zones": ["entry_points", "common_areas"],
                "alert_methods": ["phone", "email"] if member.age > 25 else ["phone"]
            },
            confidence=0.8,
            context_dependent=True,
            seasonal_variation=False,
            time_dependent=True,
            learned_from="profile_based",
            priority=10,
            last_updated=datetime.now()
        )
        preferences.append(security_pref)
        
        # Save all preferences
        for pref in preferences:
            self.preferences[pref.id] = pref
            self.save_preference(pref)
    
    def analyze_member_behavior(self, member_id: str, interaction_data: List[Dict]) -> Dict[str, Any]:
        """Analyze member behavior patterns for personalization"""
        if member_id not in self.family_members:
            return {"error": "Member not found"}
        
        member = self.family_members[member_id]
        
        # Analyze interaction patterns
        patterns = {
            "device_usage": self._analyze_device_usage_patterns(interaction_data),
            "time_patterns": self._analyze_time_patterns(interaction_data),
            "preference_evolution": self._analyze_preference_evolution(member_id, interaction_data),
            "context_sensitivity": self._analyze_context_sensitivity(interaction_data),
            "automation_acceptance": self._analyze_automation_acceptance(interaction_data)
        }
        
        # Update member profile based on analysis
        self._update_member_profile(member, patterns)
        
        # Generate new personalized recommendations
        recommendations = self.generate_personalized_recommendations(member_id, patterns)
        
        return {
            "member_id": member_id,
            "analysis_date": datetime.now().isoformat(),
            "patterns": patterns,
            "updated_preferences": len([p for p in self.preferences.values() if p.member_id == member_id]),
            "new_recommendations": len(recommendations),
            "personalization_score": self._calculate_personalization_score(member_id)
        }
    
    def _analyze_device_usage_patterns(self, interaction_data: List[Dict]) -> Dict[str, Any]:
        """Analyze device usage patterns"""
        device_usage = defaultdict(list)
        
        for interaction in interaction_data:
            if interaction.get('device_id'):
                device_usage[interaction['device_id']].append(interaction)
        
        patterns = {}
        for device_id, interactions in device_usage.items():
            if len(interactions) < 5:
                continue
            
            # Analyze usage frequency
            usage_times = [i['timestamp'].hour for i in interactions]
            peak_hours = self._find_peak_hours(usage_times)
            
            # Analyze satisfaction scores
            satisfaction_scores = [i.get('satisfaction_score', 0.5) for i in interactions if i.get('satisfaction_score')]
            avg_satisfaction = statistics.mean(satisfaction_scores) if satisfaction_scores else 0.5
            
            patterns[device_id] = {
                'usage_frequency': len(interactions),
                'peak_hours': peak_hours,
                'average_satisfaction': avg_satisfaction,
                'usage_trend': self._calculate_usage_trend(interactions),
                'preferred_settings': self._extract_preferred_settings(interactions)
            }
        
        return patterns
    
    def _analyze_time_patterns(self, interaction_data: List[Dict]) -> Dict[str, Any]:
        """Analyze time-based behavior patterns"""
        hourly_activity = defaultdict(int)
        daily_activity = defaultdict(int)
        
        for interaction in interaction_data:
            timestamp = interaction['timestamp']
            hourly_activity[timestamp.hour] += 1
            daily_activity[timestamp.strftime('%A')] += 1
        
        return {
            'most_active_hours': sorted(hourly_activity.keys(), key=lambda h: hourly_activity[h], reverse=True)[:3],
            'least_active_hours': sorted(hourly_activity.keys(), key=lambda h: hourly_activity[h])[:3],
            'most_active_days': sorted(daily_activity.keys(), key=lambda d: daily_activity[d], reverse=True)[:3],
            'activity_distribution': dict(hourly_activity),
            'weekly_pattern': dict(daily_activity)
        }
    
    def _analyze_preference_evolution(self, member_id: str, interaction_data: List[Dict]) -> Dict[str, Any]:
        """Analyze how preferences have evolved over time"""
        member_preferences = [p for p in self.preferences.values() if p.member_id == member_id]
        
        evolution = {}
        for pref in member_preferences:
            category = pref.category.value
            
            # Analyze confidence changes
            confidence_trend = self._calculate_confidence_trend(pref, interaction_data)
            
            # Analyze preference stability
            stability_score = self._calculate_preference_stability(pref, interaction_data)
            
            evolution[category] = {
                'confidence_trend': confidence_trend,
                'stability_score': stability_score,
                'last_updated': pref.last_updated.isoformat(),
                'learning_source': pref.learned_from
            }
        
        return evolution
    
    def _analyze_context_sensitivity(self, interaction_data: List[Dict]) -> Dict[str, Any]:
        """Analyze sensitivity to different contexts"""
        context_interactions = defaultdict(list)
        
        for interaction in interaction_data:
            context = interaction.get('context', 'unknown')
            context_interactions[context].append(interaction)
        
        sensitivity = {}
        for context, interactions in context_interactions.items():
            if len(interactions) < 3:
                continue
            
            satisfaction_scores = [i.get('satisfaction_score', 0.5) for i in interactions if i.get('satisfaction_score')]
            avg_satisfaction = statistics.mean(satisfaction_scores) if satisfaction_scores else 0.5
            
            sensitivity[context] = {
                'interaction_count': len(interactions),
                'average_satisfaction': avg_satisfaction,
                'context_importance': avg_satisfaction * len(interactions) / len(interaction_data)
            }
        
        return sensitivity
    
    def _analyze_automation_acceptance(self, interaction_data: List[Dict]) -> Dict[str, Any]:
        """Analyze acceptance of automated actions"""
        automated_interactions = [i for i in interaction_data if i.get('action') == 'automated']
        manual_interactions = [i for i in interaction_data if i.get('action') == 'manual']
        
        auto_satisfaction = []
        manual_satisfaction = []
        
        for interaction in automated_interactions:
            if interaction.get('satisfaction_score'):
                auto_satisfaction.append(interaction['satisfaction_score'])
        
        for interaction in manual_interactions:
            if interaction.get('satisfaction_score'):
                manual_satisfaction.append(interaction['satisfaction_score'])
        
        return {
            'automation_ratio': len(automated_interactions) / len(interaction_data) if interaction_data else 0,
            'automation_satisfaction': statistics.mean(auto_satisfaction) if auto_satisfaction else 0.5,
            'manual_satisfaction': statistics.mean(manual_satisfaction) if manual_satisfaction else 0.5,
            'automation_preference': statistics.mean(auto_satisfaction) > statistics.mean(manual_satisfaction) if auto_satisfaction and manual_satisfaction else False
        }
    
    def generate_personalized_recommendations(self, member_id: str, behavior_patterns: Dict[str, Any] = None) -> List[PersonalizedRecommendation]:
        """Generate personalized recommendations for a family member"""
        if member_id not in self.family_members:
            return []
        
        member = self.family_members[member_id]
        recommendations = []
        
        # Smart lighting recommendations
        lighting_rec = self._generate_lighting_recommendation(member, behavior_patterns)
        if lighting_rec:
            recommendations.append(lighting_rec)
        
        # Climate control recommendations
        climate_rec = self._generate_climate_recommendation(member, behavior_patterns)
        if climate_rec:
            recommendations.append(climate_rec)
        
        # Security recommendations
        security_rec = self._generate_security_recommendation(member, behavior_patterns)
        if security_rec:
            recommendations.append(security_rec)
        
        # Energy efficiency recommendations
        energy_rec = self._generate_energy_recommendation(member, behavior_patterns)
        if energy_rec:
            recommendations.append(energy_rec)
        
        # Productivity recommendations
        productivity_rec = self._generate_productivity_recommendation(member, behavior_patterns)
        if productivity_rec:
            recommendations.append(productivity_rec)
        
        # Health and wellness recommendations
        wellness_rec = self._generate_wellness_recommendation(member, behavior_patterns)
        if wellness_rec:
            recommendations.append(wellness_rec)
        
        # Save recommendations
        for rec in recommendations:
            self.recommendations[rec.id] = rec
            self.save_recommendation(rec)
        
        return recommendations
    
    def _generate_lighting_recommendation(self, member: FamilyMember, patterns: Dict[str, Any] = None) -> Optional[PersonalizedRecommendation]:
        """Generate personalized lighting recommendation"""
        if member.personality_type == PersonalityType.TECH_ENTHUSIAST:
            return PersonalizedRecommendation(
                id=f"rec_lighting_{member.id}_{int(time.time())}",
                member_id=member.id,
                recommendation_type="lighting",
                title="Advanced Circadian Rhythm Lighting System",
                description="Implement a sophisticated lighting system that automatically adjusts color temperature and brightness throughout the day to optimize your circadian rhythm and productivity.",
                benefits=[
                    "Improved sleep quality and energy levels",
                    "Enhanced focus during work hours",
                    "Reduced eye strain from screens",
                    "Automatic adjustment based on weather and season"
                ],
                implementation_steps=[
                    "Install Philips Hue or LIFX smart bulbs in main living areas",
                    "Add motion sensors for automatic activation",
                    "Configure circadian rhythm schedule in smart home app",
                    "Integrate with calendar for meeting-based lighting",
                    "Set up voice control for manual adjustments"
                ],
                estimated_cost=250.0,
                difficulty_level="intermediate",
                time_to_implement=4,
                personalization_score=0.9,
                context_relevance=0.8,
                created_date=datetime.now()
            )
        elif member.personality_type == PersonalityType.COMFORT_SEEKER:
            return PersonalizedRecommendation(
                id=f"rec_lighting_{member.id}_{int(time.time())}",
                member_id=member.id,
                recommendation_type="lighting",
                title="Cozy Ambient Lighting Setup",
                description="Create a warm, comfortable lighting environment that automatically adjusts to create the perfect ambiance for relaxation and comfort.",
                benefits=[
                    "Enhanced relaxation and comfort",
                    "Reduced stress from harsh lighting",
                    "Improved mood and well-being",
                    "Energy savings through smart scheduling"
                ],
                implementation_steps=[
                    "Install warm white LED strips behind furniture",
                    "Add table lamps with smart dimmers",
                    "Configure sunset/sunrise simulation",
                    "Set up gentle wake-up lighting",
                    "Create preset scenes for different activities"
                ],
                estimated_cost=180.0,
                difficulty_level="beginner",
                time_to_implement=3,
                personalization_score=0.85,
                context_relevance=0.9,
                created_date=datetime.now()
            )
        
        return None
    
    def _generate_climate_recommendation(self, member: FamilyMember, patterns: Dict[str, Any] = None) -> Optional[PersonalizedRecommendation]:
        """Generate personalized climate control recommendation"""
        if member.personality_type == PersonalityType.EFFICIENCY_FOCUSED:
            return PersonalizedRecommendation(
                id=f"rec_climate_{member.id}_{int(time.time())}",
                member_id=member.id,
                recommendation_type="climate",
                title="Precision Zone-Based Climate Control",
                description="Implement a highly efficient zone-based heating and cooling system that optimizes comfort while minimizing energy waste.",
                benefits=[
                    "30% reduction in energy costs",
                    "Perfect temperature in each room",
                    "Automatic scheduling based on occupancy",
                    "Integration with weather forecasts"
                ],
                implementation_steps=[
                    "Install smart thermostats in each zone",
                    "Add temperature and humidity sensors",
                    "Configure occupancy-based scheduling",
                    "Set up weather-responsive adjustments",
                    "Implement energy usage monitoring"
                ],
                estimated_cost=400.0,
                difficulty_level="intermediate",
                time_to_implement=6,
                personalization_score=0.9,
                context_relevance=0.85,
                created_date=datetime.now()
            )
        
        return None
    
    def _generate_security_recommendation(self, member: FamilyMember, patterns: Dict[str, Any] = None) -> Optional[PersonalizedRecommendation]:
        """Generate personalized security recommendation"""
        if member.privacy_level == "high":
            return PersonalizedRecommendation(
                id=f"rec_security_{member.id}_{int(time.time())}",
                member_id=member.id,
                recommendation_type="security",
                title="Privacy-Focused Security System",
                description="Implement a comprehensive security system that prioritizes privacy while maintaining excellent protection.",
                benefits=[
                    "Enhanced security without compromising privacy",
                    "Local processing of all video data",
                    "Encrypted communications",
                    "No cloud storage of personal data"
                ],
                implementation_steps=[
                    "Install local NVR system for video storage",
                    "Add privacy-focused cameras with local processing",
                    "Configure encrypted communication protocols",
                    "Set up secure remote access via VPN",
                    "Implement facial recognition with local database"
                ],
                estimated_cost=600.0,
                difficulty_level="advanced",
                time_to_implement=8,
                personalization_score=0.95,
                context_relevance=0.9,
                created_date=datetime.now()
            )
        
        return None
    
    def _generate_energy_recommendation(self, member: FamilyMember, patterns: Dict[str, Any] = None) -> Optional[PersonalizedRecommendation]:
        """Generate personalized energy efficiency recommendation"""
        if member.personality_type == PersonalityType.ENVIRONMENTALIST:
            return PersonalizedRecommendation(
                id=f"rec_energy_{member.id}_{int(time.time())}",
                member_id=member.id,
                recommendation_type="energy",
                title="Comprehensive Renewable Energy System",
                description="Transform your home into a net-positive energy producer with solar panels, battery storage, and intelligent energy management.",
                benefits=[
                    "Eliminate electricity bills",
                    "Reduce carbon footprint by 80%",
                    "Energy independence and resilience",
                    "Potential income from excess energy sales"
                ],
                implementation_steps=[
                    "Conduct professional energy audit",
                    "Install solar panel system on roof",
                    "Add battery storage system",
                    "Implement smart energy management system",
                    "Configure grid-tie and backup systems"
                ],
                estimated_cost=8000.0,
                difficulty_level="advanced",
                time_to_implement=40,
                personalization_score=0.95,
                context_relevance=0.85,
                created_date=datetime.now()
            )
        
        return None
    
    def _generate_productivity_recommendation(self, member: FamilyMember, patterns: Dict[str, Any] = None) -> Optional[PersonalizedRecommendation]:
        """Generate personalized productivity recommendation"""
        if "work_environment" in member.preferences:
            return PersonalizedRecommendation(
                id=f"rec_productivity_{member.id}_{int(time.time())}",
                member_id=member.id,
                recommendation_type="productivity",
                title="AI-Powered Productivity Environment",
                description="Create an intelligent workspace that automatically optimizes lighting, temperature, noise, and distractions based on your work patterns and calendar.",
                benefits=[
                    "25% increase in focus and productivity",
                    "Reduced fatigue and eye strain",
                    "Automatic distraction management",
                    "Seamless integration with work schedule"
                ],
                implementation_steps=[
                    "Install smart lighting with focus modes",
                    "Add noise cancellation and white noise system",
                    "Configure calendar-based automation",
                    "Set up productivity tracking and analytics",
                    "Implement break reminders and movement prompts"
                ],
                estimated_cost=350.0,
                difficulty_level="intermediate",
                time_to_implement=5,
                personalization_score=0.85,
                context_relevance=0.9,
                created_date=datetime.now()
            )
        
        return None
    
    def _generate_wellness_recommendation(self, member: FamilyMember, patterns: Dict[str, Any] = None) -> Optional[PersonalizedRecommendation]:
        """Generate personalized health and wellness recommendation"""
        return PersonalizedRecommendation(
            id=f"rec_wellness_{member.id}_{int(time.time())}",
            member_id=member.id,
            recommendation_type="wellness",
            title="Holistic Health Monitoring System",
            description="Implement a comprehensive health monitoring system that tracks air quality, sleep patterns, activity levels, and stress indicators.",
            benefits=[
                "Improved overall health and well-being",
                "Early detection of health issues",
                "Optimized sleep and recovery",
                "Stress reduction through environmental control"
            ],
            implementation_steps=[
                "Install air quality monitoring sensors",
                "Add sleep tracking and optimization system",
                "Configure stress detection through biometrics",
                "Set up activity and movement reminders",
                "Implement health data integration and analysis"
            ],
            estimated_cost=450.0,
            difficulty_level="intermediate",
            time_to_implement=6,
            personalization_score=0.8,
            context_relevance=0.85,
            created_date=datetime.now()
        )
    
    def create_contextual_automation(self, context_type: ContextType, conditions: Dict[str, Any], 
                                   actions: List[Dict[str, Any]], affected_members: List[str]) -> ContextualRule:
        """Create contextual automation rules"""
        rule_id = f"rule_{context_type.value}_{int(time.time())}"
        
        rule = ContextualRule(
            id=rule_id,
            name=f"Auto {context_type.value.title()} Response",
            context_type=context_type,
            conditions=conditions,
            actions=actions,
            affected_members=affected_members,
            priority=5,
            active=True,
            success_rate=0.0,  # Will be updated as rule is executed
            created_date=datetime.now()
        )
        
        self.contextual_rules[rule_id] = rule
        self.save_contextual_rule(rule)
        
        return rule
    
    def process_context_change(self, context_type: ContextType, context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process context changes and trigger appropriate automations"""
        self.current_context[context_type.value] = context_data
        self.context_history.append({
            'timestamp': datetime.now(),
            'context_type': context_type,
            'context_data': context_data
        })
        
        triggered_actions = []
        
        # Find applicable rules
        applicable_rules = [
            rule for rule in self.contextual_rules.values()
            if rule.context_type == context_type and rule.active
        ]
        
        # Sort by priority
        applicable_rules.sort(key=lambda r: r.priority, reverse=True)
        
        for rule in applicable_rules:
            if self._evaluate_rule_conditions(rule, context_data):
                # Execute rule actions
                for action in rule.actions:
                    executed_action = self._execute_contextual_action(action, rule.affected_members)
                    if executed_action:
                        triggered_actions.append(executed_action)
                
                # Update rule success rate
                rule.success_rate = (rule.success_rate * 0.9) + (1.0 * 0.1)  # Simple moving average
        
        # Log context change
        self.log_context_change(context_type, context_data, [r.id for r in applicable_rules])
        
        return triggered_actions
    
    def _evaluate_rule_conditions(self, rule: ContextualRule, context_data: Dict[str, Any]) -> bool:
        """Evaluate if rule conditions are met"""
        for condition_key, condition_value in rule.conditions.items():
            if condition_key not in context_data:
                return False
            
            actual_value = context_data[condition_key]
            
            # Handle different condition types
            if isinstance(condition_value, dict):
                if 'min' in condition_value and actual_value < condition_value['min']:
                    return False
                if 'max' in condition_value and actual_value > condition_value['max']:
                    return False
                if 'equals' in condition_value and actual_value != condition_value['equals']:
                    return False
            else:
                if actual_value != condition_value:
                    return False
        
        return True
    
    def _execute_contextual_action(self, action: Dict[str, Any], affected_members: List[str]) -> Optional[Dict[str, Any]]:
        """Execute a contextual action"""
        action_type = action.get('type')
        
        if action_type == 'adjust_lighting':
            return self._execute_lighting_action(action, affected_members)
        elif action_type == 'adjust_temperature':
            return self._execute_temperature_action(action, affected_members)
        elif action_type == 'play_music':
            return self._execute_music_action(action, affected_members)
        elif action_type == 'send_notification':
            return self._execute_notification_action(action, affected_members)
        elif action_type == 'activate_security':
            return self._execute_security_action(action, affected_members)
        
        return None
    
    def _execute_lighting_action(self, action: Dict[str, Any], affected_members: List[str]) -> Dict[str, Any]:
        """Execute lighting adjustment action"""
        # Get personalized lighting preferences for affected members
        lighting_settings = {}
        
        for member_id in affected_members:
            member_prefs = [p for p in self.preferences.values() 
                          if p.member_id == member_id and p.category == PreferenceCategory.LIGHTING]
            
            if member_prefs:
                pref = member_prefs[0]
                lighting_settings[member_id] = pref.preference_data
        
        # Apply lighting changes (simplified simulation)
        return {
            'action_type': 'lighting_adjustment',
            'affected_members': affected_members,
            'settings_applied': lighting_settings,
            'timestamp': datetime.now().isoformat(),
            'success': True
        }
    
    def _execute_temperature_action(self, action: Dict[str, Any], affected_members: List[str]) -> Dict[str, Any]:
        """Execute temperature adjustment action"""
        temp_settings = {}
        
        for member_id in affected_members:
            member_prefs = [p for p in self.preferences.values() 
                          if p.member_id == member_id and p.category == PreferenceCategory.TEMPERATURE]
            
            if member_prefs:
                pref = member_prefs[0]
                temp_settings[member_id] = pref.preference_data
        
        return {
            'action_type': 'temperature_adjustment',
            'affected_members': affected_members,
            'settings_applied': temp_settings,
            'timestamp': datetime.now().isoformat(),
            'success': True
        }
    
    def _execute_music_action(self, action: Dict[str, Any], affected_members: List[str]) -> Dict[str, Any]:
        """Execute music action"""
        music_settings = {}
        
        for member_id in affected_members:
            member_prefs = [p for p in self.preferences.values() 
                          if p.member_id == member_id and p.category == PreferenceCategory.MUSIC]
            
            if member_prefs:
                pref = member_prefs[0]
                music_settings[member_id] = pref.preference_data
        
        return {
            'action_type': 'music_control',
            'affected_members': affected_members,
            'settings_applied': music_settings,
            'timestamp': datetime.now().isoformat(),
            'success': True
        }
    
    def _execute_notification_action(self, action: Dict[str, Any], affected_members: List[str]) -> Dict[str, Any]:
        """Execute notification action"""
        return {
            'action_type': 'notification_sent',
            'affected_members': affected_members,
            'message': action.get('message', 'Contextual notification'),
            'timestamp': datetime.now().isoformat(),
            'success': True
        }
    
    def _execute_security_action(self, action: Dict[str, Any], affected_members: List[str]) -> Dict[str, Any]:
        """Execute security action"""
        return {
            'action_type': 'security_activation',
            'affected_members': affected_members,
            'security_level': action.get('level', 'standard'),
            'timestamp': datetime.now().isoformat(),
            'success': True
        }
    
    def _find_peak_hours(self, hours: List[int]) -> List[int]:
        """Find peak usage hours"""
        hour_counts = defaultdict(int)
        for hour in hours:
            hour_counts[hour] += 1
        
        return sorted(hour_counts.keys(), key=lambda h: hour_counts[h], reverse=True)[:3]
    
    def _calculate_usage_trend(self, interactions: List[Dict]) -> str:
        """Calculate usage trend over time"""
        if len(interactions) < 10:
            return "insufficient_data"
        
        # Simple trend analysis based on timestamps
        recent_interactions = interactions[-5:]
        older_interactions = interactions[-10:-5]
        
        recent_avg = len(recent_interactions) / 5
        older_avg = len(older_interactions) / 5
        
        if recent_avg > older_avg * 1.2:
            return "increasing"
        elif recent_avg < older_avg * 0.8:
            return "decreasing"
        else:
            return "stable"
    
    def _extract_preferred_settings(self, interactions: List[Dict]) -> Dict[str, Any]:
        """Extract preferred settings from interactions"""
        # Simplified extraction of common settings
        settings = defaultdict(list)
        
        for interaction in interactions:
            if 'settings' in interaction:
                for key, value in interaction['settings'].items():
                    settings[key].append(value)
        
        # Calculate most common settings
        preferred = {}
        for key, values in settings.items():
            if values:
                if isinstance(values[0], (int, float)):
                    preferred[key] = statistics.mean(values)
                else:
                    preferred[key] = max(set(values), key=values.count)
        
        return preferred
    
    def _calculate_confidence_trend(self, preference: PersonalPreference, interactions: List[Dict]) -> str:
        """Calculate confidence trend for a preference"""
        # Simplified confidence trend calculation
        recent_interactions = [i for i in interactions if i['timestamp'] > preference.last_updated - timedelta(days=7)]
        
        if len(recent_interactions) > 10:
            return "increasing"
        elif len(recent_interactions) < 3:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_preference_stability(self, preference: PersonalPreference, interactions: List[Dict]) -> float:
        """Calculate preference stability score"""
        # Simplified stability calculation
        relevant_interactions = [i for i in interactions if i.get('device_id') in str(preference.preference_data)]
        
        if len(relevant_interactions) < 5:
            return 0.5
        
        satisfaction_scores = [i.get('satisfaction_score', 0.5) for i in relevant_interactions if i.get('satisfaction_score')]
        
        if satisfaction_scores:
            variance = statistics.variance(satisfaction_scores) if len(satisfaction_scores) > 1 else 0
            stability = max(0, 1 - variance)
            return stability
        
        return 0.5
    
    def _update_member_profile(self, member: FamilyMember, patterns: Dict[str, Any]):
        """Update member profile based on behavior analysis"""
        # Update automation comfort based on acceptance patterns
        if 'automation_acceptance' in patterns:
            acceptance = patterns['automation_acceptance']
            if acceptance.get('automation_preference', False):
                member.automation_comfort = min(1.0, member.automation_comfort + 0.1)
            else:
                member.automation_comfort = max(0.0, member.automation_comfort - 0.05)
        
        # Update last updated timestamp
        member.last_updated = datetime.now()
        
        # Save updated member
        self.save_family_member(member)
    
    def _calculate_personalization_score(self, member_id: str) -> float:
        """Calculate overall personalization score for a member"""
        member_preferences = [p for p in self.preferences.values() if p.member_id == member_id]
        
        if not member_preferences:
            return 0.0
        
        # Calculate average confidence
        avg_confidence = statistics.mean([p.confidence for p in member_preferences])
        
        # Factor in number of preferences
        preference_coverage = min(1.0, len(member_preferences) / 10)  # Assume 10 is full coverage
        
        # Factor in recency of updates
        recent_updates = len([p for p in member_preferences if p.last_updated > datetime.now() - timedelta(days=30)])
        recency_factor = recent_updates / len(member_preferences)
        
        return (avg_confidence * 0.5) + (preference_coverage * 0.3) + (recency_factor * 0.2)
    
    def log_interaction(self, member_id: str, interaction_type: str, device_id: str = None, 
                       action: str = None, context: str = None, satisfaction_score: float = None, notes: str = None):
        """Log member interaction for learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO interaction_log 
            (member_id, timestamp, interaction_type, device_id, action, context, satisfaction_score, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (member_id, datetime.now(), interaction_type, device_id, action, context, satisfaction_score, notes))
        
        conn.commit()
        conn.close()
        
        # Add to in-memory storage
        self.interaction_history[member_id].append({
            'timestamp': datetime.now(),
            'interaction_type': interaction_type,
            'device_id': device_id,
            'action': action,
            'context': context,
            'satisfaction_score': satisfaction_score,
            'notes': notes
        })
        
        # Keep only recent data in memory
        if len(self.interaction_history[member_id]) > 1000:
            self.interaction_history[member_id].popleft()
    
    def log_context_change(self, context_type: ContextType, context_data: Dict[str, Any], triggered_rules: List[str]):
        """Log context changes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO context_log 
            (timestamp, context_type, context_data, triggered_rules, affected_members)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            datetime.now(), context_type.value, json.dumps(context_data),
            json.dumps(triggered_rules), json.dumps([])  # Would track affected members
        ))
        
        conn.commit()
        conn.close()
    
    def start_personalization_engine(self):
        """Start the personalization engine with scheduled tasks"""
        def run_personalization():
            while True:
                # Run periodic personalization tasks
                self.update_all_member_profiles()
                self.generate_daily_recommendations()
                self.optimize_contextual_rules()
                
                time.sleep(3600)  # Run every hour
        
        # Start personalization engine in background thread
        personalization_thread = threading.Thread(target=run_personalization, daemon=True)
        personalization_thread.start()
        logging.info("Personalization engine started")
    
    def update_all_member_profiles(self):
        """Update all member profiles based on recent interactions"""
        for member_id in self.family_members.keys():
            recent_interactions = list(self.interaction_history[member_id])[-100:]  # Last 100 interactions
            if recent_interactions:
                self.analyze_member_behavior(member_id, recent_interactions)
    
    def generate_daily_recommendations(self):
        """Generate daily personalized recommendations"""
        for member_id in self.family_members.keys():
            recommendations = self.generate_personalized_recommendations(member_id)
            if recommendations:
                logging.info(f"Generated {len(recommendations)} recommendations for {member_id}")
    
    def optimize_contextual_rules(self):
        """Optimize contextual rules based on success rates"""
        for rule in self.contextual_rules.values():
            if rule.success_rate < 0.3:  # Low success rate
                rule.active = False
                logging.info(f"Deactivated rule {rule.id} due to low success rate")
            elif rule.success_rate > 0.8:  # High success rate
                rule.priority = min(10, rule.priority + 1)  # Increase priority
    
    def save_family_member(self, member: FamilyMember):
        """Save family member to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO family_members 
            (id, name, age, personality_type, preferences, schedule, health_data, learning_style,
             skill_level, interests, accessibility_needs, privacy_level, automation_comfort, created_date, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            member.id, member.name, member.age, member.personality_type.value,
            json.dumps(member.preferences), json.dumps(member.schedule), json.dumps(member.health_data),
            member.learning_style, member.skill_level, json.dumps(member.interests),
            json.dumps(member.accessibility_needs), member.privacy_level, member.automation_comfort,
            member.created_date, member.last_updated
        ))
        
        conn.commit()
        conn.close()
    
    def save_preference(self, preference: PersonalPreference):
        """Save preference to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO personal_preferences 
            (id, member_id, category, preference_data, confidence, context_dependent,
             seasonal_variation, time_dependent, learned_from, priority, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            preference.id, preference.member_id, preference.category.value,
            json.dumps(preference.preference_data), preference.confidence, preference.context_dependent,
            preference.seasonal_variation, preference.time_dependent, preference.learned_from,
            preference.priority, preference.last_updated
        ))
        
        conn.commit()
        conn.close()
    
    def save_contextual_rule(self, rule: ContextualRule):
        """Save contextual rule to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO contextual_rules 
            (id, name, context_type, conditions, actions, affected_members, priority, active, success_rate, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            rule.id, rule.name, rule.context_type.value, json.dumps(rule.conditions),
            json.dumps(rule.actions), json.dumps(rule.affected_members), rule.priority,
            rule.active, rule.success_rate, rule.created_date
        ))
        
        conn.commit()
        conn.close()
    
    def save_recommendation(self, recommendation: PersonalizedRecommendation):
        """Save recommendation to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO personalized_recommendations 
            (id, member_id, recommendation_type, title, description, benefits, implementation_steps,
             estimated_cost, difficulty_level, time_to_implement, personalization_score, context_relevance, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            recommendation.id, recommendation.member_id, recommendation.recommendation_type,
            recommendation.title, recommendation.description, json.dumps(recommendation.benefits),
            json.dumps(recommendation.implementation_steps), recommendation.estimated_cost,
            recommendation.difficulty_level, recommendation.time_to_implement,
            recommendation.personalization_score, recommendation.context_relevance, recommendation.created_date
        ))
        
        conn.commit()
        conn.close()
    
    def load_data(self):
        """Load existing data from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Load family members
        cursor.execute('SELECT * FROM family_members')
        for row in cursor.fetchall():
            member = FamilyMember(
                id=row[0], name=row[1], age=row[2], personality_type=PersonalityType(row[3]),
                preferences=json.loads(row[4]), schedule=json.loads(row[5]), health_data=json.loads(row[6]),
                learning_style=row[7], skill_level=row[8], interests=json.loads(row[9]),
                accessibility_needs=json.loads(row[10]), privacy_level=row[11], automation_comfort=row[12],
                created_date=datetime.fromisoformat(row[13]), last_updated=datetime.fromisoformat(row[14])
            )
            self.family_members[member.id] = member
        
        conn.close()
        logging.info(f"Loaded {len(self.family_members)} family members from database")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive personalization dashboard data"""
        total_members = len(self.family_members)
        total_preferences = len(self.preferences)
        total_rules = len(self.contextual_rules)
        active_rules = len([r for r in self.contextual_rules.values() if r.active])
        
        return {
            "family_members": {
                "total": total_members,
                "personality_distribution": {
                    pt.value: len([m for m in self.family_members.values() if m.personality_type == pt])
                    for pt in PersonalityType
                },
                "average_automation_comfort": statistics.mean([m.automation_comfort for m in self.family_members.values()]) if total_members > 0 else 0,
                "skill_level_distribution": {
                    level: len([m for m in self.family_members.values() if m.skill_level == level])
                    for level in ["beginner", "intermediate", "advanced"]
                }
            },
            "preferences": {
                "total": total_preferences,
                "by_category": {
                    cat.value: len([p for p in self.preferences.values() if p.category == cat])
                    for cat in PreferenceCategory
                },
                "average_confidence": statistics.mean([p.confidence for p in self.preferences.values()]) if total_preferences > 0 else 0,
                "learned_preferences": len([p for p in self.preferences.values() if p.learned_from == "observed"])
            },
            "contextual_rules": {
                "total": total_rules,
                "active": active_rules,
                "by_context": {
                    ct.value: len([r for r in self.contextual_rules.values() if r.context_type == ct])
                    for ct in ContextType
                },
                "average_success_rate": statistics.mean([r.success_rate for r in self.contextual_rules.values()]) if total_rules > 0 else 0
            },
            "recommendations": {
                "total": len(self.recommendations),
                "by_type": {
                    rec_type: len([r for r in self.recommendations.values() if r.recommendation_type == rec_type])
                    for rec_type in set(r.recommendation_type for r in self.recommendations.values())
                },
                "high_personalization": len([r for r in self.recommendations.values() if r.personalization_score > 0.8])
            }
        }


# Global personalization engine instance
personalization_engine = PersonalizationEngine()

def initialize_personalization_system():
    """Initialize the personalization system"""
    logging.info("Personalization system initialized with sample family members")

if __name__ == "__main__":
    initialize_personalization_system()
    
    # Example usage
    print("Personalization Engine initialized")
    dashboard_data = personalization_engine.get_dashboard_data()
    print(f"Dashboard data: {dashboard_data}")
    
    # Example: Log an interaction
    personalization_engine.log_interaction(
        member_id="member_001",
        interaction_type="device_control",
        device_id="philips_hue_001",
        action="manual",
        context="evening_routine",
        satisfaction_score=0.9,
        notes="Adjusted brightness for reading"
    )

