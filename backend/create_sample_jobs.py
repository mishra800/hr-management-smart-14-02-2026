#!/usr/bin/env python3
"""
Create sample job postings in the database
"""
import sys
sys.path.insert(0, '.')

from app.database import engine
from sqlalchemy import text
import json
import uuid

def create_sample_jobs():
    """Create sample job postings for testing"""
    print("=" * 70)
    print("Creating Sample Job Postings")
    print("=" * 70)
    
    sample_jobs = [
        {
            "title": "Senior Software Engineer",
            "department": "Engineering",
            "location": "Bangalore, India",
            "employment_type": "full_time",
            "description": "We are looking for an experienced Senior Software Engineer to join our growing team. You will be responsible for designing, developing, and maintaining high-quality software solutions.\n\nRequirements:\n- 5+ years of software development experience\n- Strong knowledge of Python/Java\n- Experience with cloud platforms (AWS/Azure)\n- Excellent problem-solving skills\n\nResponsibilities:\n- Design and develop scalable software solutions\n- Mentor junior developers\n- Participate in code reviews\n- Collaborate with cross-functional teams",
            "requirements": "5+ years of software development experience, Strong knowledge of Python/Java, Experience with cloud platforms (AWS/Azure), Excellent problem-solving skills",
            "salary_min": 1500000,
            "salary_max": 2500000,
            "required_skills": ["Python", "Java", "AWS", "Azure", "Problem Solving"],
            "min_experience_years": 5,
            "max_experience_years": 10,
            "remote_allowed": True,
            "status": "active"
        },
        {
            "title": "HR Manager",
            "department": "Human Resources",
            "location": "Mumbai, India",
            "employment_type": "full_time",
            "description": "Join our HR team as an HR Manager. You will oversee recruitment, employee relations, and HR operations.\n\nRequirements:\n- 3+ years of HR experience\n- Strong interpersonal skills\n- Knowledge of labor laws\n- Experience with HRMS systems\n\nResponsibilities:\n- Manage recruitment process\n- Handle employee relations\n- Ensure compliance with labor laws\n- Develop HR policies",
            "requirements": "3+ years of HR experience, Strong interpersonal skills, Knowledge of labor laws, Experience with HRMS systems",
            "salary_min": 800000,
            "salary_max": 1200000,
            "required_skills": ["HR Management", "Recruitment", "Employee Relations", "Labor Laws"],
            "min_experience_years": 3,
            "max_experience_years": 8,
            "remote_allowed": False,
            "status": "active"
        },
        {
            "title": "Frontend Developer",
            "department": "Engineering",
            "location": "Hyderabad, India",
            "employment_type": "full_time",
            "description": "We're seeking a talented Frontend Developer to create amazing user experiences. You'll work with React, TypeScript, and modern web technologies.\n\nRequirements:\n- 3+ years of frontend development\n- Expert in React.js\n- Strong CSS/HTML skills\n- Experience with TypeScript\n\nResponsibilities:\n- Build responsive web applications\n- Implement UI/UX designs\n- Optimize application performance\n- Write clean, maintainable code",
            "requirements": "3+ years of frontend development, Expert in React.js, Strong CSS/HTML skills, Experience with TypeScript",
            "salary_min": 1000000,
            "salary_max": 1800000,
            "required_skills": ["React.js", "TypeScript", "CSS", "HTML", "JavaScript"],
            "min_experience_years": 3,
            "max_experience_years": 7,
            "remote_allowed": True,
            "status": "active"
        },
        {
            "title": "Data Analyst",
            "department": "Analytics",
            "location": "Pune, India",
            "employment_type": "full_time",
            "description": "Looking for a Data Analyst to help us make data-driven decisions. You'll analyze data, create reports, and provide insights.\n\nRequirements:\n- 1-2 years of data analysis experience\n- Proficiency in SQL\n- Knowledge of Python/R\n- Strong analytical skills\n\nResponsibilities:\n- Analyze business data\n- Create dashboards and reports\n- Identify trends and patterns\n- Present findings to stakeholders",
            "requirements": "1-2 years of data analysis experience, Proficiency in SQL, Knowledge of Python/R, Strong analytical skills",
            "salary_min": 600000,
            "salary_max": 900000,
            "required_skills": ["SQL", "Python", "R", "Data Analysis", "Excel"],
            "min_experience_years": 1,
            "max_experience_years": 3,
            "remote_allowed": True,
            "status": "active"
        },
        {
            "title": "DevOps Engineer",
            "department": "Engineering",
            "location": "Bangalore, India",
            "employment_type": "full_time",
            "description": "Join our DevOps team to build and maintain our infrastructure. You'll work with cloud platforms, CI/CD pipelines, and automation tools.\n\nRequirements:\n- 4+ years of DevOps experience\n- Strong knowledge of AWS/Azure\n- Experience with Docker/Kubernetes\n- Proficiency in scripting (Python/Bash)\n\nResponsibilities:\n- Manage cloud infrastructure\n- Build CI/CD pipelines\n- Automate deployment processes\n- Monitor system performance",
            "requirements": "4+ years of DevOps experience, Strong knowledge of AWS/Azure, Experience with Docker/Kubernetes, Proficiency in scripting (Python/Bash)",
            "salary_min": 1800000,
            "salary_max": 2800000,
            "required_skills": ["AWS", "Azure", "Docker", "Kubernetes", "CI/CD", "Python", "Bash"],
            "min_experience_years": 4,
            "max_experience_years": 10,
            "remote_allowed": True,
            "status": "active"
        }
    ]
    
    with engine.connect() as conn:
        # Check if jobs already exist
        check_query = text("SELECT COUNT(*) FROM job_postings")
        existing_count = conn.execute(check_query).scalar()
        
        if existing_count > 0:
            print(f"\n✓ Database already has {existing_count} job postings")
            print("Skipping sample data creation...")
            
            # Show existing jobs
            verify_query = text("""
                SELECT id, title, department, location, status
                FROM job_postings
                ORDER BY created_at DESC
            """)
            
            jobs = conn.execute(verify_query).fetchall()
            
            print("\nExisting Job Postings:")
            print("-" * 70)
            for job in jobs:
                print(f"ID: {job[0]} | {job[1]}")
                print(f"  Department: {job[2]} | Location: {job[3]} | Status: {job[4]}")
                print("-" * 70)
            return
        
        print(f"\nCreating {len(sample_jobs)} sample job postings...")
        print("-" * 70)
        
        created_count = 0
        for job in sample_jobs:
            try:
                # Generate unique application link code
                link_code = str(uuid.uuid4())[:8]
                
                insert_query = text("""
                    INSERT INTO job_postings (
                        title,
                        department,
                        location,
                        employment_type,
                        description,
                        requirements,
                        salary_min,
                        salary_max,
                        status,
                        posted_by,
                        posted_date,
                        workflow_mode,
                        requisition_status,
                        application_link_code,
                        required_skills,
                        min_experience_years,
                        max_experience_years,
                        remote_allowed,
                        created_at,
                        updated_at
                    )
                    VALUES (
                        :title,
                        :department,
                        :location,
                        :employment_type,
                        :description,
                        :requirements,
                        :salary_min,
                        :salary_max,
                        :status,
                        1,
                        CURRENT_DATE,
                        'flexible',
                        'approved',
                        :application_link_code,
                        :required_skills,
                        :min_experience_years,
                        :max_experience_years,
                        :remote_allowed,
                        CURRENT_TIMESTAMP,
                        CURRENT_TIMESTAMP
                    )
                    RETURNING id, title
                """)
                
                result = conn.execute(insert_query, {
                    "title": job["title"],
                    "department": job["department"],
                    "location": job["location"],
                    "employment_type": job["employment_type"],
                    "description": job["description"],
                    "requirements": job["requirements"],
                    "salary_min": job["salary_min"],
                    "salary_max": job["salary_max"],
                    "status": job["status"],
                    "application_link_code": link_code,
                    "required_skills": json.dumps(job["required_skills"]),
                    "min_experience_years": job["min_experience_years"],
                    "max_experience_years": job["max_experience_years"],
                    "remote_allowed": job["remote_allowed"]
                })
                
                row = result.fetchone()
                print(f"✓ Created: {row[1]} (ID: {row[0]})")
                created_count += 1
                
            except Exception as e:
                print(f"✗ Failed to create {job['title']}: {e}")
        
        conn.commit()
        
        print("\n" + "=" * 70)
        print(f"✅ Successfully created {created_count} job postings!")
        print("=" * 70)
        
        # Verify
        verify_query = text("""
            SELECT id, title, department, location, status
            FROM job_postings
            ORDER BY created_at DESC
        """)
        
        jobs = conn.execute(verify_query).fetchall()
        
        print("\nJob Postings in Database:")
        print("-" * 70)
        for job in jobs:
            print(f"ID: {job[0]} | {job[1]}")
            print(f"  Department: {job[2]} | Location: {job[3]} | Status: {job[4]}")
            print("-" * 70)
        
        print("\n✅ Recruitment page should now display these jobs!")
        print("=" * 70)

if __name__ == "__main__":
    try:
        create_sample_jobs()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
