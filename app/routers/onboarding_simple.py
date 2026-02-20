from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from datetime import datetime
import random
from ..dependencies import get_current_user

router = APIRouter(
    prefix="/onboarding",
    tags=["onboarding"]
)

@router.get("/my-employee-id")
def get_my_employee_id(current_user: dict = Depends(get_current_user)):
    """Get current user's employee ID"""
    # For mock purposes, return the user ID as employee ID
    return {
        "success": True,
        "employee_id": current_user.get("id", 1),
        "user_id": current_user.get("id", 1)
    }

@router.get("/documents")
def get_onboarding_documents(current_user: dict = Depends(get_current_user)):
    """Get onboarding documents"""
    return {
        "success": True,
        "data": [
            {
                "id": 1,
                "name": "Employee Handbook",
                "type": "handbook",
                "url": "/documents/employee-handbook.pdf",
                "required": True,
                "completed": True,
                "uploaded_at": "2025-01-20T10:00:00"
            },
            {
                "id": 2,
                "name": "Tax Forms (W-4)",
                "type": "tax_form",
                "url": "/documents/w4-form.pdf",
                "required": True,
                "completed": False,
                "uploaded_at": None
            },
            {
                "id": 3,
                "name": "Emergency Contact Form",
                "type": "emergency_contact",
                "url": "/documents/emergency-contact.pdf",
                "required": True,
                "completed": True,
                "uploaded_at": "2025-01-22T14:30:00"
            },
            {
                "id": 4,
                "name": "Direct Deposit Form",
                "type": "banking",
                "url": "/documents/direct-deposit.pdf",
                "required": True,
                "completed": False,
                "uploaded_at": None
            }
        ]
    }

@router.post("/generate-offer")
def generate_offer_letter(current_user: dict = Depends(get_current_user)):
    """Generate offer letter"""
    return {
        "success": True,
        "data": {
            "id": 1,
            "employee_id": current_user.get("id", 1),
            "position": "Software Developer",
            "department": "Engineering",
            "salary": "$75,000",
            "start_date": "2025-02-01",
            "benefits": [
                "Health Insurance",
                "401(k) Matching",
                "Paid Time Off",
                "Professional Development"
            ],
            "offer_letter_url": "/documents/offer-letter.pdf",
            "status": "pending_signature",
            "generated_at": datetime.now().isoformat()
        }
    }

@router.get("/induction-modules")
def get_induction_modules(current_user: dict = Depends(get_current_user)):
    """Get induction modules"""
    return {
        "success": True,
        "data": [
            {
                "id": 1,
                "title": "Company Overview",
                "description": "Learn about our company history, mission, and values",
                "duration": "30 minutes",
                "status": "completed",
                "completion_date": "2025-01-20T10:00:00",
                "url": "/training/company-overview"
            },
            {
                "id": 2,
                "title": "HR Policies",
                "description": "Understanding workplace policies and procedures",
                "duration": "45 minutes",
                "status": "in_progress",
                "completion_date": None,
                "url": "/training/hr-policies"
            },
            {
                "id": 3,
                "title": "IT Security Training",
                "description": "Cybersecurity best practices and company IT policies",
                "duration": "60 minutes",
                "status": "not_started",
                "completion_date": None,
                "url": "/training/it-security"
            },
            {
                "id": 4,
                "title": "Team Introduction",
                "description": "Meet your team members and understand team dynamics",
                "duration": "90 minutes",
                "status": "not_started",
                "completion_date": None,
                "url": "/training/team-intro"
            }
        ]
    }

@router.post("/sign-offer")
def sign_offer_letter(current_user: dict = Depends(get_current_user)):
    """Sign offer letter"""
    return {
        "success": True,
        "message": "Offer letter signed successfully",
        "data": {
            "id": 1,
            "employee_id": current_user.get("id", 1),
            "status": "signed",
            "signed_at": datetime.now().isoformat(),
            "next_steps": [
                "Complete background check",
                "Submit required documents",
                "Schedule first day orientation"
            ]
        }
    }

@router.post("/upload-doc")
def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload onboarding document"""
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Mock file upload
    return {
        "success": True,
        "message": "Document uploaded successfully",
        "data": {
            "id": random.randint(100, 999),
            "filename": file.filename,
            "size": random.randint(1000, 50000),
            "uploaded_at": datetime.now().isoformat(),
            "status": "uploaded",
            "url": f"/documents/onboarding/{file.filename}"
        }
    }

@router.get("/progress/{employee_id}")
def get_employee_progress(
    employee_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get onboarding progress for specific employee"""
    return {
        "success": True,
        "data": {
            "employee_id": employee_id,
            "overall_progress": 75,
            "completed_tasks": 6,
            "total_tasks": 8,
            "estimated_completion": "2025-02-05",
            "phases": [
                {
                    "phase": "Documentation",
                    "progress": 100,
                    "status": "completed"
                },
                {
                    "phase": "IT Setup",
                    "progress": 80,
                    "status": "in_progress"
                },
                {
                    "phase": "Training",
                    "progress": 40,
                    "status": "in_progress"
                },
                {
                    "phase": "Team Integration",
                    "progress": 0,
                    "status": "pending"
                }
            ]
        }
    }

@router.get("/timeline/{employee_id}")
def get_onboarding_timeline(
    employee_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get onboarding timeline for employee"""
    return {
        "success": True,
        "data": {
            "employee_id": employee_id,
            "start_date": "2025-01-15",
            "expected_completion": "2025-02-15",
            "milestones": [
                {
                    "id": 1,
                    "title": "Offer Acceptance",
                    "description": "Employee accepted job offer",
                    "date": "2025-01-15T10:00:00",
                    "status": "completed",
                    "type": "milestone"
                },
                {
                    "id": 2,
                    "title": "Background Check",
                    "description": "Background verification completed",
                    "date": "2025-01-18T14:30:00",
                    "status": "completed",
                    "type": "verification"
                },
                {
                    "id": 3,
                    "title": "First Day",
                    "description": "Employee's first day at the company",
                    "date": "2025-02-01T09:00:00",
                    "status": "upcoming",
                    "type": "milestone"
                },
                {
                    "id": 4,
                    "title": "IT Equipment Setup",
                    "description": "Laptop and accessories assignment",
                    "date": "2025-02-01T10:00:00",
                    "status": "upcoming",
                    "type": "task"
                },
                {
                    "id": 5,
                    "title": "Team Introduction",
                    "description": "Meet team members and manager",
                    "date": "2025-02-01T14:00:00",
                    "status": "upcoming",
                    "type": "meeting"
                },
                {
                    "id": 6,
                    "title": "Training Modules",
                    "description": "Complete mandatory training courses",
                    "date": "2025-02-03T09:00:00",
                    "status": "upcoming",
                    "type": "training"
                },
                {
                    "id": 7,
                    "title": "30-Day Check-in",
                    "description": "First performance and satisfaction review",
                    "date": "2025-03-01T15:00:00",
                    "status": "scheduled",
                    "type": "review"
                }
            ]
        }
    }

@router.get("/compliance-status/{employee_id}")
def get_compliance_status(
    employee_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get compliance status for employee"""
    return {
        "success": True,
        "data": {
            "employee_id": employee_id,
            "overall_compliance": 85,
            "requirements": [
                {
                    "name": "Background Check",
                    "status": "completed",
                    "completed_date": "2025-01-15T10:00:00"
                },
                {
                    "name": "Drug Test",
                    "status": "completed",
                    "completed_date": "2025-01-18T14:30:00"
                },
                {
                    "name": "I-9 Verification",
                    "status": "pending",
                    "due_date": "2025-02-01T17:00:00"
                },
                {
                    "name": "Tax Forms (W-4)",
                    "status": "pending",
                    "due_date": "2025-02-01T17:00:00"
                },
                {
                    "name": "Emergency Contacts",
                    "status": "completed",
                    "completed_date": "2025-01-22T09:15:00"
                }
            ]
        }
    }

@router.get("/it-resources/{employee_id}")
def get_it_resources(
    employee_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get IT resources for employee"""
    return {
        "success": True,
        "data": {
            "employee_id": employee_id,
            "laptop": {
                "model": "MacBook Pro 14-inch",
                "serial": "ABC123456789",
                "status": "assigned",
                "assigned_date": "2025-01-20T10:00:00"
            },
            "accessories": [
                {
                    "item": "Wireless Mouse",
                    "model": "Logitech MX Master 3",
                    "status": "assigned"
                },
                {
                    "item": "Monitor",
                    "model": "Dell 27-inch 4K",
                    "status": "pending"
                },
                {
                    "item": "Keyboard",
                    "model": "Apple Magic Keyboard",
                    "status": "assigned"
                }
            ],
            "software": [
                {
                    "name": "Microsoft Office 365",
                    "license": "Business Premium",
                    "status": "activated"
                },
                {
                    "name": "Slack",
                    "status": "invited"
                },
                {
                    "name": "Zoom",
                    "status": "activated"
                }
            ],
            "accounts": [
                {
                    "service": "Company Email",
                    "username": f"employee{employee_id}@company.com",
                    "status": "active"
                },
                {
                    "service": "VPN Access",
                    "status": "pending"
                },
                {
                    "service": "File Server",
                    "status": "active"
                }
            ]
        }
    }

@router.post("/chat")
def onboarding_chat(
    message: str,
    current_user: dict = Depends(get_current_user)
):
    """Onboarding chatbot"""
    # Simple chatbot responses
    responses = {
        "wifi": "The WiFi password is 'CompanyGuest2025'. You can also connect to the 'Company-Secure' network using your employee credentials.",
        "benefits": "Our benefits include health insurance, dental, vision, 401(k) with company matching, paid time off, and professional development opportunities.",
        "first day": "On your first day, please arrive at 9:00 AM at the main reception. Bring a valid ID and your signed offer letter. You'll receive your laptop and access cards.",
        "parking": "Employee parking is available in the north lot. You'll receive a parking pass on your first day.",
        "dress code": "We have a business casual dress code. Jeans are acceptable on Fridays.",
        "lunch": "We have a cafeteria on the 2nd floor open from 11:30 AM to 2:00 PM. There are also several restaurants within walking distance.",
        "team": "You'll be introduced to your team during your first week. Your manager will schedule one-on-one meetings with each team member.",
        "training": "Your training schedule will be provided on your first day. Most training modules are available online and can be completed at your own pace."
    }
    
    # Find matching response
    message_lower = message.lower()
    response = "I'm here to help with your onboarding questions! You can ask me about WiFi, benefits, your first day, parking, dress code, lunch options, your team, or training."
    
    for keyword, answer in responses.items():
        if keyword in message_lower:
            response = answer
            break
    
    return {
        "success": True,
        "response": response,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/tasks")
def get_onboarding_tasks():
    """Get onboarding tasks"""
    return {
        "success": True,
        "message": "Onboarding tasks retrieved",
        "data": [
            {
                "id": 1,
                "title": "Complete profile setup",
                "description": "Fill in all required profile information",
                "status": "completed",
                "due_date": "2024-12-20"
            },
            {
                "id": 2,
                "title": "IT equipment setup",
                "description": "Receive and configure laptop and accessories",
                "status": "in_progress",
                "due_date": "2024-12-22"
            }
        ]
    }

@router.get("/progress")
def get_onboarding_progress():
    """Get onboarding progress"""
    return {
        "success": True,
        "message": "Onboarding progress retrieved",
        "data": {
            "employee_id": 1,
            "overall_progress": 75,
            "completed_tasks": 6,
            "total_tasks": 8,
            "estimated_completion": "2024-12-25"
        }
    }

@router.get("/checklist")
def get_onboarding_checklist():
    """Get onboarding checklist"""
    return {
        "success": True,
        "message": "Onboarding checklist retrieved",
        "data": [
            {"item": "Profile Setup", "completed": True},
            {"item": "IT Equipment", "completed": True},
            {"item": "Team Introduction", "completed": False},
            {"item": "Training Modules", "completed": False}
        ]
    }