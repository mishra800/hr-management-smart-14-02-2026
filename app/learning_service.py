from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from app import models, schemas
import json
import random

class LearningService:
    """Comprehensive Learning Management Service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_courses(self) -> List[models.Course]:
        """Get all available courses"""
        return self.db.query(models.Course).all()
    
    def create_course(self, course_data: schemas.CourseCreate) -> models.Course:
        """Create a new course"""
        db_course = models.Course(**course_data.dict())
        self.db.add(db_course)
        self.db.commit()
        self.db.refresh(db_course)
        return db_course
    
    def get_employee_enrollments(self, employee_id: int) -> List[models.Enrollment]:
        """Get all enrollments for an employee"""
        return self.db.query(models.Enrollment).filter(
            models.Enrollment.employee_id == employee_id
        ).all()
    
    def enroll_employee(self, employee_id: int, course_id: int) -> models.Enrollment:
        """Enroll an employee in a course"""
        # Check if already enrolled
        existing = self.db.query(models.Enrollment).filter(
            models.Enrollment.employee_id == employee_id,
            models.Enrollment.course_id == course_id
        ).first()
        
        if existing:
            raise ValueError("Employee already enrolled in this course")
        
        enrollment = models.Enrollment(
            employee_id=employee_id,
            course_id=course_id,
            progress=0
        )
        self.db.add(enrollment)
        self.db.commit()
        self.db.refresh(enrollment)
        return enrollment
    
    def update_progress(self, enrollment_id: int, progress: int) -> models.Enrollment:
        """Update enrollment progress"""
        enrollment = self.db.query(models.Enrollment).filter(
            models.Enrollment.id == enrollment_id
        ).first()
        
        if not enrollment:
            raise ValueError("Enrollment not found")
        
        enrollment.progress = min(100, max(0, progress))  # Ensure 0-100 range
        self.db.commit()
        self.db.refresh(enrollment)
        return enrollment
    
    def get_skills(self) -> List[models.Skill]:
        """Get all skills, seed if empty"""
        skills = self.db.query(models.Skill).all()
        
        if not skills:
            # Seed default skills
            default_skills = [
                "Python", "JavaScript", "React", "Node.js", "SQL", 
                "Machine Learning", "Cloud Architecture", "DevOps",
                "Project Management", "Leadership", "Communication",
                "Data Analysis", "System Design", "Microservices"
            ]
            
            for skill_name in default_skills:
                skill = models.Skill(name=skill_name)
                self.db.add(skill)
            
            self.db.commit()
            skills = self.db.query(models.Skill).all()
        
        return skills
    
    def get_employee_skills(self, employee_id: int) -> List[models.EmployeeSkill]:
        """Get all skills for an employee"""
        return self.db.query(models.EmployeeSkill).filter(
            models.EmployeeSkill.employee_id == employee_id
        ).all()
    
    def add_employee_skill(self, employee_id: int, skill_id: int, proficiency: int) -> models.EmployeeSkill:
        """Add or update employee skill"""
        # Check if skill already exists for employee
        existing = self.db.query(models.EmployeeSkill).filter(
            models.EmployeeSkill.employee_id == employee_id,
            models.EmployeeSkill.skill_id == skill_id
        ).first()
        
        if existing:
            existing.proficiency = min(100, max(0, proficiency))  # Ensure 0-100 range
            self.db.commit()
            self.db.refresh(existing)
            return existing
        
        employee_skill = models.EmployeeSkill(
            employee_id=employee_id,
            skill_id=skill_id,
            proficiency=min(100, max(0, proficiency))
        )
        self.db.add(employee_skill)
        self.db.commit()
        self.db.refresh(employee_skill)
        return employee_skill
    
    def recommend_courses(self, employee_id: int) -> List[models.Course]:
        """Recommend courses for an employee based on their skills and enrollments"""
        # Get courses employee is not enrolled in
        enrolled_course_ids = [
            e.course_id for e in self.get_employee_enrollments(employee_id)
        ]
        
        available_courses = self.db.query(models.Course).filter(
            ~models.Course.id.in_(enrolled_course_ids)
        ).all()
        
        # For now, return random selection of available courses
        # In production, this would use AI/ML algorithms
        random.shuffle(available_courses)
        return available_courses[:3]
    
    def analyze_skill_gaps(self, employee_id: int, current_role: str, target_role: Optional[str] = None) -> Dict[str, Any]:
        """Analyze skill gaps for career progression"""
        # Mock implementation - in production would use AI analysis
        role = target_role if target_role else current_role
        
        if "Engineer" in role or "Developer" in role:
            skills = [
                {"name": "JavaScript/TypeScript", "current": 85, "required": 90, "priority": "Medium", "time": "1-2 months"},
                {"name": "System Design", "current": 65, "required": 85, "priority": "High", "time": "2-3 months"},
                {"name": "Cloud Architecture", "current": 55, "required": 80, "priority": "Critical", "time": "4-6 months"},
                {"name": "Microservices", "current": 70, "required": 85, "priority": "High", "time": "2-3 months"},
                {"name": "DevOps & CI/CD", "current": 60, "required": 75, "priority": "Medium", "time": "1-2 months"}
            ]
        elif "Data" in role or "Analyst" in role:
            skills = [
                {"name": "Machine Learning", "current": 75, "required": 90, "priority": "Critical", "time": "3-4 months"},
                {"name": "Deep Learning", "current": 60, "required": 85, "priority": "High", "time": "4-5 months"},
                {"name": "Statistical Analysis", "current": 80, "required": 90, "priority": "Medium", "time": "1-2 months"},
                {"name": "Big Data", "current": 50, "required": 75, "priority": "High", "time": "3-4 months"},
                {"name": "MLOps", "current": 45, "required": 70, "priority": "Critical", "time": "4-6 months"}
            ]
        else:
            skills = [
                {"name": "Project Management", "current": 70, "required": 85, "priority": "High", "time": "2-3 months"},
                {"name": "Communication", "current": 80, "required": 90, "priority": "Low", "time": "1 month"},
                {"name": "Agile/Scrum", "current": 75, "required": 85, "priority": "Medium", "time": "1-2 months"}
            ]
        
        recommendations = [
            "Focus on critical priority skills first for maximum impact",
            "Enroll in recommended courses and certifications",
            "Seek mentorship from senior team members",
            "Practice skills through real projects"
        ]
        
        return {
            "role": role,
            "skills": skills,
            "recommendations": recommendations,
            "analysis_date": datetime.utcnow().isoformat()
        }
    
    def get_personalized_training(self, employee_id: int, career_goal: str, current_skills: str = "") -> Dict[str, Any]:
        """Get personalized training recommendations"""
        goal = career_goal.lower()
        courses = []
        
        if "machine learning" in goal or "data" in goal:
            courses = [
                {
                    "title": "Machine Learning Specialization",
                    "provider": "Coursera",
                    "relevance": 98,
                    "duration": "3 months",
                    "level": "Intermediate",
                    "skills": ["Supervised Learning", "Neural Networks"],
                    "cost": "$49/mo"
                },
                {
                    "title": "Deep Learning Specialization",
                    "provider": "DeepLearning.AI",
                    "relevance": 95,
                    "duration": "4 months",
                    "level": "Advanced",
                    "skills": ["CNNs", "RNNs", "TensorFlow"],
                    "cost": "$49/mo"
                },
                {
                    "title": "Data Science Professional Cert",
                    "provider": "IBM",
                    "relevance": 96,
                    "duration": "4 months",
                    "level": "Beginner",
                    "skills": ["Python", "SQL", "Data Viz"],
                    "cost": "$39/mo"
                }
            ]
        elif "cloud" in goal or "architect" in goal:
            courses = [
                {
                    "title": "AWS Certified Solutions Architect",
                    "provider": "AWS Training",
                    "relevance": 97,
                    "duration": "2 months",
                    "level": "Intermediate",
                    "skills": ["AWS Services", "Cloud Architecture"],
                    "cost": "$150"
                },
                {
                    "title": "Google Cloud Professional Architect",
                    "provider": "Google Cloud",
                    "relevance": 94,
                    "duration": "2.5 months",
                    "level": "Advanced",
                    "skills": ["GCP Services", "Kubernetes"],
                    "cost": "$200"
                }
            ]
        else:
            courses = [
                {
                    "title": "Leadership Principles",
                    "provider": "Harvard Business School",
                    "relevance": 90,
                    "duration": "6 weeks",
                    "level": "Intermediate",
                    "skills": ["Management", "Strategy"],
                    "cost": "$1600"
                },
                {
                    "title": "PMP Certification Prep",
                    "provider": "PMI",
                    "relevance": 88,
                    "duration": "3 months",
                    "level": "Advanced",
                    "skills": ["Project Management", "Agile"],
                    "cost": "$400"
                }
            ]
        
        tips = [
            "Dedicate 5-10 hours per week for consistent progress",
            "Apply concepts in real projects immediately",
            "Join study groups and online communities",
            "Set weekly milestones and track progress"
        ]
        
        return {
            "goal": career_goal,
            "courses": courses,
            "tips": tips,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def predict_learning_outcome(self, employee_id: int, target_skill: str) -> Dict[str, Any]:
        """Predict learning outcomes for a target skill"""
        skill = target_skill
        
        if "Machine Learning" in skill or "ML" in skill:
            return {
                "skill": skill,
                "success_probability": 85,
                "completion_time": "6-8 months",
                "proficiency": "Advanced",
                "career_impact": "High",
                "roi_score": 9.0,
                "timeline": [
                    {"month": 1, "level": "Beginner", "proficiency": 25},
                    {"month": 3, "level": "Intermediate", "proficiency": 50},
                    {"month": 6, "level": "Advanced", "proficiency": 75},
                    {"month": 8, "level": "Expert", "proficiency": 90}
                ],
                "opportunities": ["Senior ML Engineer", "Lead ML Projects", "Research Scientist"],
                "challenges": ["Steep math learning curve", "Time investment", "Keeping up with rapid changes"]
            }
        elif "Cloud" in skill:
            return {
                "skill": skill,
                "success_probability": 90,
                "completion_time": "4-6 months",
                "proficiency": "Advanced",
                "career_impact": "Very High",
                "roi_score": 9.5,
                "timeline": [
                    {"month": 1, "level": "Beginner", "proficiency": 30},
                    {"month": 3, "level": "Intermediate", "proficiency": 60},
                    {"month": 5, "level": "Advanced", "proficiency": 85}
                ],
                "opportunities": ["Cloud Architect", "Migration Lead", "DevOps Consultant"],
                "challenges": ["Multiple platforms to learn", "Certification costs", "Rapid service updates"]
            }
        else:
            return {
                "skill": skill,
                "success_probability": 75,
                "completion_time": "3-5 months",
                "proficiency": "Intermediate",
                "career_impact": "Medium",
                "roi_score": 7.5,
                "timeline": [
                    {"month": 1, "level": "Beginner", "proficiency": 20},
                    {"month": 3, "level": "Intermediate", "proficiency": 50},
                    {"month": 5, "level": "Advanced", "proficiency": 70}
                ],
                "opportunities": ["Senior Role", "Team Lead", "Subject Matter Expert"],
                "challenges": ["Time management", "Consistency", "Practical application"]
            }