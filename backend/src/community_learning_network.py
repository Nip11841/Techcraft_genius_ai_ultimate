"""
Community-Driven AI Learning & Open-Source Hardware Designs
Enables collaborative learning, sharing of designs, and collective intelligence
for the TechCraft Genius AI platform, creating a global network of DIY innovators.
"""

import json
import sqlite3
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import hashlib
import uuid
import threading
import time
from dataclasses import dataclass
from enum import Enum
import base64

class ContributionType(Enum):
    PROJECT_DESIGN = "project_design"
    IMPROVEMENT = "improvement"
    BUG_FIX = "bug_fix"
    COST_OPTIMIZATION = "cost_optimization"
    ALTERNATIVE_SOLUTION = "alternative_solution"
    TESTING_RESULTS = "testing_results"
    DOCUMENTATION = "documentation"

class DesignLicense(Enum):
    OPEN_SOURCE = "open_source"
    CREATIVE_COMMONS = "creative_commons"
    MIT = "mit"
    GPL = "gpl"
    PROPRIETARY = "proprietary"

@dataclass
class CommunityContribution:
    contributor_id: str
    contribution_type: ContributionType
    title: str
    description: str
    technical_details: Dict
    license_type: DesignLicense
    tags: List[str]
    difficulty_level: int
    estimated_cost: float
    build_time_hours: int

class CommunityLearningNetwork:
    def __init__(self, db_path: str = "community_network.db"):
        self.db_path = db_path
        self.init_database()
        
        # Network settings
        self.reputation_system_enabled = True
        self.auto_validation_enabled = True
        self.collaborative_filtering_enabled = True
        
        # Learning algorithms
        self.learning_algorithms = {
            "pattern_recognition": True,
            "cost_optimization": True,
            "design_evolution": True,
            "failure_analysis": True
        }
        
    def init_database(self):
        """Initialize the community learning network database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Community members table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS community_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                email TEXT,
                location TEXT,
                skill_level INTEGER DEFAULT 1,
                specializations TEXT,
                reputation_score REAL DEFAULT 100.0,
                contributions_count INTEGER DEFAULT 0,
                successful_builds INTEGER DEFAULT 0,
                failed_builds INTEGER DEFAULT 0,
                helpful_votes INTEGER DEFAULT 0,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP,
                is_verified BOOLEAN DEFAULT 0,
                is_moderator BOOLEAN DEFAULT 0
            )
        ''')
        
        # Open source designs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS open_source_designs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                design_id TEXT UNIQUE NOT NULL,
                contributor_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT,
                subcategory TEXT,
                difficulty_level INTEGER,
                estimated_cost REAL,
                build_time_hours INTEGER,
                materials_list TEXT,
                tools_required TEXT,
                step_by_step_instructions TEXT,
                code_snippets TEXT,
                circuit_diagrams TEXT,
                cad_files TEXT,
                images TEXT,
                videos TEXT,
                license_type TEXT,
                tags TEXT,
                version TEXT DEFAULT '1.0',
                parent_design_id TEXT,
                fork_count INTEGER DEFAULT 0,
                star_count INTEGER DEFAULT 0,
                download_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_verified BOOLEAN DEFAULT 0,
                is_featured BOOLEAN DEFAULT 0,
                FOREIGN KEY (contributor_id) REFERENCES community_members (member_id)
            )
        ''')
        
        # Build reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS build_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id TEXT UNIQUE NOT NULL,
                design_id TEXT NOT NULL,
                builder_id TEXT NOT NULL,
                build_status TEXT NOT NULL,
                actual_cost REAL,
                actual_build_time_hours INTEGER,
                difficulty_rating INTEGER,
                success_rating INTEGER,
                modifications_made TEXT,
                issues_encountered TEXT,
                solutions_found TEXT,
                photos TEXT,
                videos TEXT,
                would_recommend BOOLEAN,
                public_notes TEXT,
                private_feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (design_id) REFERENCES open_source_designs (design_id),
                FOREIGN KEY (builder_id) REFERENCES community_members (member_id)
            )
        ''')
        
        # Collaborative improvements table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collaborative_improvements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                improvement_id TEXT UNIQUE NOT NULL,
                original_design_id TEXT NOT NULL,
                contributor_id TEXT NOT NULL,
                improvement_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                technical_changes TEXT,
                cost_impact REAL,
                difficulty_impact INTEGER,
                performance_impact TEXT,
                evidence_provided TEXT,
                testing_results TEXT,
                community_votes INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                merged_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (original_design_id) REFERENCES open_source_designs (design_id),
                FOREIGN KEY (contributor_id) REFERENCES community_members (member_id)
            )
        ''')
        
        # Knowledge base table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                knowledge_id TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                source_type TEXT,
                source_url TEXT,
                contributor_id TEXT,
                confidence_level REAL DEFAULT 0.5,
                validation_count INTEGER DEFAULT 0,
                usage_count INTEGER DEFAULT 0,
                last_validated TIMESTAMP,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Learning patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id TEXT UNIQUE NOT NULL,
                pattern_type TEXT NOT NULL,
                pattern_data TEXT NOT NULL,
                confidence_score REAL,
                supporting_evidence TEXT,
                applications TEXT,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                validated_by_community BOOLEAN DEFAULT 0,
                usage_count INTEGER DEFAULT 0
            )
        ''')
        
        # Innovation challenges table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS innovation_challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                challenge_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                problem_statement TEXT,
                constraints TEXT,
                success_criteria TEXT,
                prize_description TEXT,
                deadline DATE,
                created_by TEXT,
                status TEXT DEFAULT 'active',
                submission_count INTEGER DEFAULT 0,
                winner_design_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES community_members (member_id)
            )
        ''')
        
        # Global learning insights table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS global_learning_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                insight_id TEXT UNIQUE NOT NULL,
                insight_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                data_sources TEXT,
                statistical_significance REAL,
                practical_applications TEXT,
                cost_implications TEXT,
                geographic_relevance TEXT,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                validated BOOLEAN DEFAULT 0,
                impact_score REAL DEFAULT 0.0
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Initialize with sample data
        self._populate_sample_community_data()
    
    def _populate_sample_community_data(self):
        """Populate database with sample community data"""
        sample_members = [
            {
                "member_id": "maker_001",
                "username": "TechTinkerer",
                "location": "London, UK",
                "skill_level": 4,
                "specializations": "Electronics,3D Printing,Home Automation",
                "reputation_score": 850.0
            },
            {
                "member_id": "maker_002", 
                "username": "DIYGenius",
                "location": "Manchester, UK",
                "skill_level": 5,
                "specializations": "Robotics,Arduino,Raspberry Pi",
                "reputation_score": 920.0
            },
            {
                "member_id": "maker_003",
                "username": "BudgetBuilder",
                "location": "Birmingham, UK", 
                "skill_level": 3,
                "specializations": "Cost Optimization,Upcycling,Woodworking",
                "reputation_score": 720.0
            }
        ]
        
        sample_designs = [
            {
                "design_id": "design_001",
                "contributor_id": "maker_001",
                "title": "Smart Bin Collection Robot",
                "description": "Autonomous robot that brings bins back from the kerb to your garden",
                "category": "Robotics",
                "subcategory": "Home Automation",
                "difficulty_level": 4,
                "estimated_cost": 180.0,
                "build_time_hours": 20,
                "materials_list": "Arduino Uno,Ultrasonic sensors,DC motors,Wheels,Chassis materials",
                "tools_required": "Soldering iron,Screwdriver set,3D printer",
                "license_type": "open_source",
                "tags": "automation,bins,robot,outdoor",
                "success_rate": 0.85
            },
            {
                "design_id": "design_002",
                "contributor_id": "maker_002",
                "title": "Car Detection Gate Opener",
                "description": "Automatically opens gate when your car approaches using license plate recognition",
                "category": "Security",
                "subcategory": "Access Control",
                "difficulty_level": 3,
                "estimated_cost": 120.0,
                "build_time_hours": 12,
                "materials_list": "Raspberry Pi,Camera module,Servo motor,Gate hardware",
                "tools_required": "Basic tools,Computer for setup",
                "license_type": "open_source",
                "tags": "security,automation,car,gate",
                "success_rate": 0.92
            },
            {
                "design_id": "design_003",
                "contributor_id": "maker_003",
                "title": "Ultra-Efficient DIY Solar Panel",
                "description": "Build high-efficiency solar panels for under £100 using salvaged cells",
                "category": "Energy",
                "subcategory": "Solar Power",
                "difficulty_level": 3,
                "estimated_cost": 85.0,
                "build_time_hours": 8,
                "materials_list": "Solar cells,Tempered glass,EVA film,Aluminum frame",
                "tools_required": "Soldering iron,Glass cutter,Frame tools",
                "license_type": "creative_commons",
                "tags": "solar,energy,budget,diy",
                "success_rate": 0.78
            }
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert sample members
        for member in sample_members:
            cursor.execute('''
                INSERT OR IGNORE INTO community_members 
                (member_id, username, location, skill_level, specializations, reputation_score)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                member["member_id"], member["username"], member["location"],
                member["skill_level"], member["specializations"], member["reputation_score"]
            ))
        
        # Insert sample designs
        for design in sample_designs:
            cursor.execute('''
                INSERT OR IGNORE INTO open_source_designs 
                (design_id, contributor_id, title, description, category, subcategory,
                 difficulty_level, estimated_cost, build_time_hours, materials_list,
                 tools_required, license_type, tags, success_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                design["design_id"], design["contributor_id"], design["title"],
                design["description"], design["category"], design["subcategory"],
                design["difficulty_level"], design["estimated_cost"], design["build_time_hours"],
                design["materials_list"], design["tools_required"], design["license_type"],
                design["tags"], design["success_rate"]
            ))
        
        conn.commit()
        conn.close()
    
    def register_community_member(self, username: str, email: str = None,
                                location: str = None, specializations: List[str] = None) -> str:
        """Register a new community member"""
        member_id = f"maker_{uuid.uuid4().hex[:8]}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO community_members 
            (member_id, username, email, location, specializations)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            member_id, username, email, location,
            ",".join(specializations) if specializations else ""
        ))
        
        conn.commit()
        conn.close()
        
        return member_id
    
    def submit_design(self, contributor_id: str, title: str, description: str,
                     category: str, difficulty_level: int, estimated_cost: float,
                     materials_list: List[str], tools_required: List[str],
                     instructions: str, license_type: str = "open_source",
                     tags: List[str] = None) -> str:
        """Submit a new open-source design to the community"""
        design_id = f"design_{uuid.uuid4().hex[:8]}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Estimate build time based on complexity
        build_time = self._estimate_build_time(difficulty_level, len(materials_list))
        
        cursor.execute('''
            INSERT INTO open_source_designs 
            (design_id, contributor_id, title, description, category, difficulty_level,
             estimated_cost, build_time_hours, materials_list, tools_required,
             step_by_step_instructions, license_type, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            design_id, contributor_id, title, description, category, difficulty_level,
            estimated_cost, build_time, ",".join(materials_list), ",".join(tools_required),
            instructions, license_type, ",".join(tags) if tags else ""
        ))
        
        # Update contributor's contribution count
        cursor.execute('''
            UPDATE community_members 
            SET contributions_count = contributions_count + 1
            WHERE member_id = ?
        ''', (contributor_id,))
        
        conn.commit()
        conn.close()
        
        return design_id
    
    def _estimate_build_time(self, difficulty_level: int, component_count: int) -> int:
        """Estimate build time based on difficulty and complexity"""
        base_time = difficulty_level * 2  # 2 hours per difficulty level
        component_time = component_count * 0.5  # 30 minutes per component
        return int(base_time + component_time)
    
    def submit_build_report(self, design_id: str, builder_id: str, build_status: str,
                           actual_cost: float = None, actual_build_time: int = None,
                           difficulty_rating: int = None, success_rating: int = None,
                           modifications: str = None, issues: str = None,
                           solutions: str = None, would_recommend: bool = True) -> str:
        """Submit a build report for a design"""
        report_id = f"report_{uuid.uuid4().hex[:8]}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO build_reports 
            (report_id, design_id, builder_id, build_status, actual_cost,
             actual_build_time_hours, difficulty_rating, success_rating,
             modifications_made, issues_encountered, solutions_found, would_recommend)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            report_id, design_id, builder_id, build_status, actual_cost,
            actual_build_time, difficulty_rating, success_rating,
            modifications, issues, solutions, would_recommend
        ))
        
        # Update design success rate
        self._update_design_success_rate(design_id)
        
        # Update builder's build count
        if build_status == "success":
            cursor.execute('''
                UPDATE community_members 
                SET successful_builds = successful_builds + 1
                WHERE member_id = ?
            ''', (builder_id,))
        else:
            cursor.execute('''
                UPDATE community_members 
                SET failed_builds = failed_builds + 1
                WHERE member_id = ?
            ''', (builder_id,))
        
        conn.commit()
        conn.close()
        
        return report_id
    
    def _update_design_success_rate(self, design_id: str):
        """Update the success rate for a design based on build reports"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_builds,
                SUM(CASE WHEN build_status = 'success' THEN 1 ELSE 0 END) as successful_builds
            FROM build_reports 
            WHERE design_id = ?
        ''', (design_id,))
        
        result = cursor.fetchone()
        total_builds, successful_builds = result
        
        if total_builds > 0:
            success_rate = successful_builds / total_builds
            cursor.execute('''
                UPDATE open_source_designs 
                SET success_rate = ?
                WHERE design_id = ?
            ''', (success_rate, design_id))
        
        conn.commit()
        conn.close()
    
    def suggest_improvement(self, design_id: str, contributor_id: str,
                          improvement_type: str, title: str, description: str,
                          technical_changes: str, cost_impact: float = 0.0) -> str:
        """Suggest an improvement to an existing design"""
        improvement_id = f"improve_{uuid.uuid4().hex[:8]}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO collaborative_improvements 
            (improvement_id, original_design_id, contributor_id, improvement_type,
             title, description, technical_changes, cost_impact)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            improvement_id, design_id, contributor_id, improvement_type,
            title, description, technical_changes, cost_impact
        ))
        
        conn.commit()
        conn.close()
        
        return improvement_id
    
    def get_trending_designs(self, category: str = None, days: int = 30) -> List[Dict]:
        """Get trending designs based on recent activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since_date = datetime.now() - timedelta(days=days)
        
        base_query = '''
            SELECT 
                d.*,
                m.username as contributor_name,
                COUNT(br.id) as recent_builds,
                AVG(br.success_rating) as avg_rating
            FROM open_source_designs d
            LEFT JOIN community_members m ON d.contributor_id = m.member_id
            LEFT JOIN build_reports br ON d.design_id = br.design_id 
                AND br.created_at > ?
        '''
        
        params = [since_date]
        
        if category:
            base_query += " WHERE d.category = ?"
            params.append(category)
        
        base_query += '''
            GROUP BY d.design_id
            ORDER BY recent_builds DESC, d.star_count DESC, d.success_rate DESC
            LIMIT 20
        '''
        
        cursor.execute(base_query, params)
        results = cursor.fetchall()
        
        conn.close()
        
        trending = []
        for result in results:
            trending.append({
                "design_id": result[1],
                "title": result[3],
                "description": result[4],
                "category": result[5],
                "difficulty_level": result[7],
                "estimated_cost": result[8],
                "build_time_hours": result[9],
                "contributor_name": result[26],
                "success_rate": result[21],
                "recent_builds": result[27],
                "average_rating": result[28] if result[28] else 0,
                "star_count": result[18],
                "tags": result[16].split(",") if result[16] else []
            })
        
        return trending
    
    def search_designs(self, query: str = None, category: str = None,
                      max_cost: float = None, max_difficulty: int = None,
                      tags: List[str] = None, min_success_rate: float = None) -> List[Dict]:
        """Search for designs with various filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        base_query = '''
            SELECT d.*, m.username as contributor_name
            FROM open_source_designs d
            LEFT JOIN community_members m ON d.contributor_id = m.member_id
            WHERE 1=1
        '''
        
        params = []
        
        if query:
            base_query += " AND (d.title LIKE ? OR d.description LIKE ? OR d.tags LIKE ?)"
            query_param = f"%{query}%"
            params.extend([query_param, query_param, query_param])
        
        if category:
            base_query += " AND d.category = ?"
            params.append(category)
        
        if max_cost:
            base_query += " AND d.estimated_cost <= ?"
            params.append(max_cost)
        
        if max_difficulty:
            base_query += " AND d.difficulty_level <= ?"
            params.append(max_difficulty)
        
        if min_success_rate:
            base_query += " AND d.success_rate >= ?"
            params.append(min_success_rate)
        
        if tags:
            for tag in tags:
                base_query += " AND d.tags LIKE ?"
                params.append(f"%{tag}%")
        
        base_query += " ORDER BY d.success_rate DESC, d.star_count DESC"
        
        cursor.execute(base_query, params)
        results = cursor.fetchall()
        
        conn.close()
        
        designs = []
        for result in results:
            designs.append({
                "design_id": result[1],
                "title": result[3],
                "description": result[4],
                "category": result[5],
                "subcategory": result[6],
                "difficulty_level": result[7],
                "estimated_cost": result[8],
                "build_time_hours": result[9],
                "materials_list": result[10].split(",") if result[10] else [],
                "tools_required": result[11].split(",") if result[11] else [],
                "contributor_name": result[25],
                "success_rate": result[21],
                "star_count": result[18],
                "download_count": result[19],
                "tags": result[16].split(",") if result[16] else [],
                "license_type": result[15],
                "created_at": result[22]
            })
        
        return designs
    
    def get_design_details(self, design_id: str) -> Dict:
        """Get detailed information about a specific design"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get design details
        cursor.execute('''
            SELECT d.*, m.username as contributor_name, m.reputation_score
            FROM open_source_designs d
            LEFT JOIN community_members m ON d.contributor_id = m.member_id
            WHERE d.design_id = ?
        ''', (design_id,))
        
        design_result = cursor.fetchone()
        
        if not design_result:
            conn.close()
            return {"error": "Design not found"}
        
        # Get build reports
        cursor.execute('''
            SELECT br.*, m.username as builder_name
            FROM build_reports br
            LEFT JOIN community_members m ON br.builder_id = m.member_id
            WHERE br.design_id = ?
            ORDER BY br.created_at DESC
        ''', (design_id,))
        
        build_reports = cursor.fetchall()
        
        # Get improvements
        cursor.execute('''
            SELECT ci.*, m.username as contributor_name
            FROM collaborative_improvements ci
            LEFT JOIN community_members m ON ci.contributor_id = m.member_id
            WHERE ci.original_design_id = ?
            ORDER BY ci.community_votes DESC, ci.created_at DESC
        ''', (design_id,))
        
        improvements = cursor.fetchall()
        
        conn.close()
        
        # Format design details
        design = {
            "design_id": design_result[1],
            "title": design_result[3],
            "description": design_result[4],
            "category": design_result[5],
            "subcategory": design_result[6],
            "difficulty_level": design_result[7],
            "estimated_cost": design_result[8],
            "build_time_hours": design_result[9],
            "materials_list": design_result[10].split(",") if design_result[10] else [],
            "tools_required": design_result[11].split(",") if design_result[11] else [],
            "instructions": design_result[12],
            "code_snippets": design_result[13],
            "contributor_name": design_result[26],
            "contributor_reputation": design_result[27],
            "success_rate": design_result[21],
            "star_count": design_result[18],
            "download_count": design_result[19],
            "fork_count": design_result[17],
            "tags": design_result[16].split(",") if design_result[16] else [],
            "license_type": design_result[15],
            "version": design_result[20],
            "created_at": design_result[22],
            "updated_at": design_result[23],
            "is_verified": design_result[24]
        }
        
        # Format build reports
        design["build_reports"] = []
        for report in build_reports:
            design["build_reports"].append({
                "builder_name": report[17],
                "build_status": report[3],
                "actual_cost": report[4],
                "actual_build_time": report[5],
                "difficulty_rating": report[6],
                "success_rating": report[7],
                "modifications": report[8],
                "issues": report[9],
                "solutions": report[10],
                "would_recommend": report[13],
                "created_at": report[16]
            })
        
        # Format improvements
        design["improvements"] = []
        for improvement in improvements:
            design["improvements"].append({
                "improvement_id": improvement[1],
                "contributor_name": improvement[14],
                "improvement_type": improvement[3],
                "title": improvement[4],
                "description": improvement[5],
                "cost_impact": improvement[7],
                "community_votes": improvement[10],
                "status": improvement[11],
                "created_at": improvement[13]
            })
        
        return design
    
    def discover_learning_patterns(self) -> List[Dict]:
        """Discover learning patterns from community data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        patterns = []
        
        # Pattern 1: Cost vs Success Rate correlation
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN estimated_cost < 50 THEN 'Under £50'
                    WHEN estimated_cost < 100 THEN '£50-£100'
                    WHEN estimated_cost < 200 THEN '£100-£200'
                    ELSE 'Over £200'
                END as cost_range,
                AVG(success_rate) as avg_success_rate,
                COUNT(*) as design_count
            FROM open_source_designs
            GROUP BY cost_range
            ORDER BY avg_success_rate DESC
        ''')
        
        cost_success_data = cursor.fetchall()
        patterns.append({
            "pattern_type": "cost_success_correlation",
            "title": "Cost vs Success Rate Analysis",
            "data": [{"cost_range": row[0], "success_rate": row[1], "count": row[2]} 
                    for row in cost_success_data],
            "insight": "Lower cost projects tend to have higher success rates due to simpler implementations"
        })
        
        # Pattern 2: Difficulty vs Build Time correlation
        cursor.execute('''
            SELECT 
                difficulty_level,
                AVG(build_time_hours) as avg_build_time,
                AVG(success_rate) as avg_success_rate,
                COUNT(*) as design_count
            FROM open_source_designs
            GROUP BY difficulty_level
            ORDER BY difficulty_level
        ''')
        
        difficulty_data = cursor.fetchall()
        patterns.append({
            "pattern_type": "difficulty_time_correlation",
            "title": "Difficulty vs Build Time Analysis",
            "data": [{"difficulty": row[0], "build_time": row[1], "success_rate": row[2], "count": row[3]} 
                    for row in difficulty_data],
            "insight": "Build time increases exponentially with difficulty, but success rates plateau after level 3"
        })
        
        # Pattern 3: Popular component combinations
        cursor.execute('''
            SELECT materials_list, COUNT(*) as usage_count
            FROM open_source_designs
            WHERE materials_list IS NOT NULL
            GROUP BY materials_list
            HAVING COUNT(*) > 1
            ORDER BY usage_count DESC
            LIMIT 10
        ''')
        
        component_data = cursor.fetchall()
        patterns.append({
            "pattern_type": "popular_components",
            "title": "Most Popular Component Combinations",
            "data": [{"components": row[0], "usage_count": row[1]} for row in component_data],
            "insight": "Arduino-based projects dominate, suggesting strong community expertise in this area"
        })
        
        conn.close()
        
        return patterns
    
    def generate_global_insights(self) -> Dict:
        """Generate global insights from community learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        insights = {}
        
        # Community growth metrics
        cursor.execute('''
            SELECT 
                COUNT(*) as total_members,
                AVG(reputation_score) as avg_reputation,
                SUM(contributions_count) as total_contributions,
                SUM(successful_builds) as total_successful_builds
            FROM community_members
        ''')
        
        community_stats = cursor.fetchone()
        insights["community_health"] = {
            "total_members": community_stats[0],
            "average_reputation": round(community_stats[1], 2),
            "total_contributions": community_stats[2],
            "total_successful_builds": community_stats[3]
        }
        
        # Design ecosystem health
        cursor.execute('''
            SELECT 
                COUNT(*) as total_designs,
                AVG(success_rate) as avg_success_rate,
                AVG(estimated_cost) as avg_cost,
                COUNT(DISTINCT category) as categories_covered
            FROM open_source_designs
        ''')
        
        design_stats = cursor.fetchone()
        insights["design_ecosystem"] = {
            "total_designs": design_stats[0],
            "average_success_rate": round(design_stats[1], 3),
            "average_cost": round(design_stats[2], 2),
            "categories_covered": design_stats[3]
        }
        
        # Innovation trends
        cursor.execute('''
            SELECT 
                category,
                COUNT(*) as design_count,
                AVG(success_rate) as avg_success_rate,
                AVG(estimated_cost) as avg_cost
            FROM open_source_designs
            GROUP BY category
            ORDER BY design_count DESC
        ''')
        
        category_trends = cursor.fetchall()
        insights["innovation_trends"] = [
            {
                "category": row[0],
                "design_count": row[1],
                "success_rate": round(row[2], 3),
                "average_cost": round(row[3], 2)
            } for row in category_trends
        ]
        
        # Learning velocity
        cursor.execute('''
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as designs_created
            FROM open_source_designs
            WHERE created_at > date('now', '-30 days')
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        ''')
        
        daily_creation = cursor.fetchall()
        insights["learning_velocity"] = {
            "designs_per_day": [{"date": row[0], "count": row[1]} for row in daily_creation],
            "trend": "increasing" if len(daily_creation) > 0 else "stable"
        }
        
        conn.close()
        
        return insights
    
    def create_innovation_challenge(self, creator_id: str, title: str, description: str,
                                  problem_statement: str, constraints: str,
                                  success_criteria: str, deadline: str,
                                  prize_description: str = None) -> str:
        """Create a new innovation challenge for the community"""
        challenge_id = f"challenge_{uuid.uuid4().hex[:8]}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO innovation_challenges 
            (challenge_id, title, description, problem_statement, constraints,
             success_criteria, deadline, created_by, prize_description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            challenge_id, title, description, problem_statement, constraints,
            success_criteria, deadline, creator_id, prize_description
        ))
        
        conn.commit()
        conn.close()
        
        return challenge_id
    
    def get_active_challenges(self) -> List[Dict]:
        """Get all active innovation challenges"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ic.*, m.username as creator_name
            FROM innovation_challenges ic
            LEFT JOIN community_members m ON ic.created_by = m.member_id
            WHERE ic.status = 'active' AND ic.deadline > date('now')
            ORDER BY ic.deadline ASC
        ''')
        
        challenges = cursor.fetchall()
        conn.close()
        
        return [
            {
                "challenge_id": challenge[1],
                "title": challenge[2],
                "description": challenge[3],
                "problem_statement": challenge[4],
                "constraints": challenge[5],
                "success_criteria": challenge[6],
                "prize_description": challenge[7],
                "deadline": challenge[8],
                "creator_name": challenge[12],
                "submission_count": challenge[10],
                "created_at": challenge[11]
            } for challenge in challenges
        ]
    
    def get_community_leaderboard(self, metric: str = "reputation") -> List[Dict]:
        """Get community leaderboard based on various metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if metric == "reputation":
            order_by = "reputation_score DESC"
        elif metric == "contributions":
            order_by = "contributions_count DESC"
        elif metric == "successful_builds":
            order_by = "successful_builds DESC"
        else:
            order_by = "reputation_score DESC"
        
        cursor.execute(f'''
            SELECT 
                username, location, skill_level, reputation_score,
                contributions_count, successful_builds, helpful_votes
            FROM community_members
            WHERE reputation_score > 0
            ORDER BY {order_by}
            LIMIT 20
        ''')
        
        leaderboard = cursor.fetchall()
        conn.close()
        
        return [
            {
                "rank": idx + 1,
                "username": member[0],
                "location": member[1],
                "skill_level": member[2],
                "reputation_score": member[3],
                "contributions": member[4],
                "successful_builds": member[5],
                "helpful_votes": member[6]
            } for idx, member in enumerate(leaderboard)
        ]

