from fastapi import APIRouter, HTTPException
from datetime import datetime
import random

router = APIRouter(
    prefix="/recruitment",
    tags=["recruitment"]
)

# Mock data
MOCK_JOBS = [
    {
        "id": 1,
        "title": "Senior Software Engineer",
        "department": "Engineering",
        "location": "Remote",
        "description": "We are looking for a Senior Software Engineer to join our team...",
        "requirements": "5+ years of experience in Python, React, and cloud technologies",
        "posted_date": datetime.now().isoformat(),
        "is_active": True,
        "current_step": 3,
        "requisition_status": "approved"
    },
    {
        "id": 2,
        "title": "Product Manager",
        "department": "Product",
        "location": "New York",
        "description": "Join our product team to drive innovation...",
        "requirements": "3+ years of product management experience",
        "posted_date": datetime.now().isoformat(),
        "is_active": True,
        "current_step": 2,
        "requisition_status": "approved"
    },
    {
        "id": 3,
        "title": "Frontend Developer",
        "department": "Engineering",
        "location": "San Francisco",
        "description": "Build amazing user interfaces with React...",
        "requirements": "3+ years of React, TypeScript, and modern frontend tools",
        "posted_date": datetime.now().isoformat(),
        "is_active": True,
        "current_step": 4,
        "requisition_status": "approved"
    }
]

MOCK_APPLICATIONS = [
    {
        "id": 1,
        "job_id": 1,
        "candidate_name": "John Doe",
        "candidate_email": "john.doe@example.com",
        "status": "applied",
        "applied_date": datetime.now().isoformat(),
        "ai_fit_score": 85.5,
        "resume_url": "/uploads/resumes/john_doe_resume.pdf"
    },
    {
        "id": 2,
        "job_id": 1,
        "candidate_name": "Jane Smith",
        "candidate_email": "jane.smith@example.com",
        "status": "screening",
        "applied_date": datetime.now().isoformat(),
        "ai_fit_score": 92.3,
        "resume_url": "/uploads/resumes/jane_smith_resume.pdf"
    },
    {
        "id": 3,
        "job_id": 2,
        "candidate_name": "Mike Johnson",
        "candidate_email": "mike.johnson@example.com",
        "status": "shortlisted",
        "applied_date": datetime.now().isoformat(),
        "ai_fit_score": 78.9,
        "resume_url": "/uploads/resumes/mike_johnson_resume.pdf"
    },
    {
        "id": 4,
        "job_id": 3,
        "candidate_name": "Sarah Wilson",
        "candidate_email": "sarah.wilson@example.com",
        "status": "interview_scheduled",
        "applied_date": datetime.now().isoformat(),
        "ai_fit_score": 88.7,
        "resume_url": "/uploads/resumes/sarah_wilson_resume.pdf"
    }
]

@router.get("/")
def get_recruitment_overview():
    """Get recruitment overview"""
    return {
        "success": True,
        "message": "Recruitment overview retrieved successfully",
        "data": {
            "total_jobs": len(MOCK_JOBS),
            "active_jobs": len([j for j in MOCK_JOBS if j["is_active"]]),
            "total_applications": len(MOCK_APPLICATIONS),
            "pending_applications": len([a for a in MOCK_APPLICATIONS if a["status"] == "applied"])
        }
    }

@router.get("/jobs/active")
def get_active_jobs():
    """Get active job postings"""
    active_jobs = [job for job in MOCK_JOBS if job.get("is_active", True)]
    return active_jobs

@router.get("/apply/{link_code}")
def get_job_by_link(link_code: str):
    """Get job details by application link code"""
    # For demo purposes, map link codes to job IDs
    link_to_job = {
        "senior-engineer-2025": 1,
        "product-manager-ny": 2,
        "frontend-dev-sf": 3,
        "default": 1  # fallback
    }
    
    job_id = link_to_job.get(link_code, link_to_job["default"])
    job = next((j for j in MOCK_JOBS if j["id"] == job_id), None)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Add application link info
    job_with_link = job.copy()
    job_with_link["application_link"] = link_code
    job_with_link["apply_url"] = f"/apply/{link_code}"
    
    return job_with_link

@router.get("/jobs/")
def get_jobs():
    """Get all job postings"""
    return MOCK_JOBS

@router.get("/jobs/{job_id}")
def get_job(job_id: int):
    """Get specific job by ID"""
    job = next((j for j in MOCK_JOBS if j["id"] == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/jobs/{job_id}/applications")
def get_job_applications(job_id: int):
    """Get applications for a specific job"""
    job = next((j for j in MOCK_JOBS if j["id"] == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_applications = [a for a in MOCK_APPLICATIONS if a["job_id"] == job_id]
    return job_applications

@router.get("/jobs/{job_id}/sourcing/candidates")
def get_sourced_candidates(job_id: int):
    """Get sourced candidates for a job"""
    job = next((j for j in MOCK_JOBS if j["id"] == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Mock sourced candidates
    sourced_candidates = [
        {
            "id": f"sourced_{job_id}_1",
            "name": "Alex Rodriguez",
            "email": "alex.rodriguez@example.com",
            "source": "LinkedIn",
            "match_score": 89,
            "skills": ["Python", "React", "AWS", "Docker"],
            "experience_years": 5,
            "current_company": "Tech Corp",
            "location": "Remote",
            "availability": "2 weeks notice"
        },
        {
            "id": f"sourced_{job_id}_2",
            "name": "Emily Chen",
            "email": "emily.chen@example.com",
            "source": "GitHub",
            "match_score": 92,
            "skills": ["JavaScript", "TypeScript", "Node.js", "MongoDB"],
            "experience_years": 4,
            "current_company": "Startup Inc",
            "location": "San Francisco",
            "availability": "Immediate"
        }
    ]
    return sourced_candidates

@router.get("/jobs/{job_id}/assessment/generate")
def generate_assessment(job_id: int, difficulty: str = "medium"):
    """Generate assessment questions for a job"""
    job = next((j for j in MOCK_JOBS if j["id"] == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Mock assessment questions based on job title
    title = job["title"].lower()
    
    if "software" in title or "engineer" in title:
        questions = [
            {
                "id": 1,
                "question": "What is the time complexity of binary search?",
                "options": ["O(n)", "O(log n)", "O(n²)", "O(1)"],
                "correct_answer": "O(log n)",
                "type": "multiple_choice"
            },
            {
                "id": 2,
                "question": "Explain the difference between REST and GraphQL APIs.",
                "type": "text",
                "expected_keywords": ["REST", "GraphQL", "endpoints", "queries"]
            },
            {
                "id": 3,
                "question": "Write a function to reverse a string in Python.",
                "type": "coding",
                "language": "python"
            }
        ]
    elif "product" in title:
        questions = [
            {
                "id": 1,
                "question": "How would you prioritize features in a product backlog?",
                "type": "text",
                "expected_keywords": ["user value", "business impact", "effort", "prioritization"]
            },
            {
                "id": 2,
                "question": "What metrics would you track for a mobile app?",
                "options": ["DAU/MAU", "Retention Rate", "Conversion Rate", "All of the above"],
                "correct_answer": "All of the above",
                "type": "multiple_choice"
            }
        ]
    else:
        questions = [
            {
                "id": 1,
                "question": "Describe your experience with the technologies mentioned in the job description.",
                "type": "text"
            },
            {
                "id": 2,
                "question": "How do you handle challenging situations at work?",
                "type": "text"
            }
        ]
    
    return questions

@router.get("/applications/{application_id}/score-breakdown")
def get_score_breakdown(application_id: int):
    """Get AI score breakdown for an application"""
    application = next((a for a in MOCK_APPLICATIONS if a["id"] == application_id), None)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Mock score breakdown
    breakdown = {
        "overall_score": application["ai_fit_score"],
        "breakdown": {
            "skills_match": random.randint(70, 95),
            "experience_level": random.randint(75, 90),
            "education_fit": random.randint(80, 95),
            "keyword_relevance": random.randint(65, 85),
            "cultural_fit": random.randint(70, 90)
        },
        "strengths": [
            "Strong technical background",
            "Relevant industry experience",
            "Good communication skills"
        ],
        "areas_for_improvement": [
            "Could benefit from more leadership experience",
            "Additional certifications would be valuable"
        ],
        "recommendations": [
            "Proceed to technical interview",
            "Focus on leadership questions during interview"
        ]
    }
    
    return breakdown

@router.get("/applications")
def get_applications():
    """Get all applications"""
    return MOCK_APPLICATIONS

@router.get("/stats")
def get_recruitment_stats():
    """Get recruitment statistics"""
    return {
        "success": True,
        "message": "Recruitment stats retrieved",
        "data": {
            "total_jobs": len(MOCK_JOBS),
            "active_jobs": len([j for j in MOCK_JOBS if j["is_active"]]),
            "total_applications": len(MOCK_APPLICATIONS),
            "pending_applications": len([a for a in MOCK_APPLICATIONS if a["status"] == "applied"]),
            "interviews_scheduled": len([a for a in MOCK_APPLICATIONS if a["status"] == "interview_scheduled"])
        }
    }