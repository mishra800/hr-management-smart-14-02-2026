"""
Comprehensive Leave Management Service
Based on Dhanush Group Attendance & Leave Policy

POLICY DEFINITIONS:
2.1 Attendance: Attendance is the concept of resources, who are expected to be present at work, 
    on time every day.
2.2 Absenteeism: Absenteeism generally refers to an employee being absent from work during 
    normal working days/hours.
2.3 Leave: Leave is a provision to stay away from work with prior approval from the approving 
    authorities. It may be granted for casual purposes or planned activity, on medical grounds, 
    or in any other emergency conditions.

OBJECTIVES:
3.1 Attendance Policy: Dhanush Group is encouraging all its resources to attend to regular duties 
    within the specified time. The main objective is to promote the efficient operations of the 
    company's productivity and client satisfaction.
3.2 Leave Policy: Dhanush group believes that its resources should have opportunities to enjoy time, 
    which is away from work to balance their family & professional life. The company gives the 
    opportunity to its resource on genuine reasons to spend time with their family during the leave 
    and take care of their personal needs.
"""

from datetime import datetime, date, time, timedelta
from typing import List, Dict, Optional, Tuple, Any
from app.schemas import LeaveRequestCreate, LeaveBalance, LeaveType, Holiday, WFHRequest
import calendar

class LeaveService:
    def __init__(self):
        # Policy definitions as per Dhanush Group guidelines
        self.policy_definitions = {
            "attendance": {
                "definition": "Attendance is the concept of resources, who are expected to be present at work, on time every day.",
                "objective": "Promote efficient operations of the company's productivity and client satisfaction",
                "implementation": [
                    "Expected presence during normal working hours (10:00 AM - 7:00 PM)",
                    "Grace period of 15 minutes allowed (maximum 3 times per month)",
                    "Real-time attendance tracking and monitoring",
                    "Performance correlation with attendance consistency"
                ]
            },
            "absenteeism": {
                "definition": "Absenteeism generally refers to an employee being absent from work during normal working days/hours.",
                "impact": "Affects team productivity and client deliverables",
                "monitoring": [
                    "Absence tracking and pattern analysis",
                    "Automated notifications for unauthorized absence",
                    "Escalation process for consecutive absences (3+ days)",
                    "Integration with leave management system"
                ]
            },
            "leave": {
                "definition": "Leave is a provision to stay away from work with prior approval from the approving authorities. It may be granted for casual purposes or planned activity, on medical grounds, or in any other emergency conditions.",
                "objective": "Balance family & professional life while maintaining business continuity",
                "philosophy": "Resources should have opportunities to enjoy time away from work to balance their family & professional life",
                "implementation": [
                    "Prior approval required from designated authorities",
                    "Multiple leave types for different purposes",
                    "Automated workflow with manager/HR approval",
                    "Work-life balance focused policies"
                ]
            }
        }
        
        # Initialize leave types based on Dhanush Group policy (Section 9)
        self.leave_types = {
            "CL": {
                "name": "Casual Leave",
                "code": "CL",
                "max_days_per_year": 18,  # 1.5 days per month = 18 per annum
                "max_consecutive_days": 3,  # Maximum three Casual leaves can be availed at a stretch
                "applicable_to": ["probationary", "permanent"],
                "probationary_rules": {
                    "monthly_entitlement": 1,  # 1 leave per month from second month
                    "start_from_month": 2      # From the second month after joining
                },
                "permanent_rules": {
                    "monthly_entitlement": 1.5,  # 1.5 days per month on prorate basis
                    "annual_entitlement": 18     # 18 Leaves per annum
                },
                "requires_medical_certificate": False,
                "carry_forward": False,
                "encashable": False
            },
            "BL": {
                "name": "Birthday / Wedding Anniversary Leave",
                "code": "BL", 
                "max_days_per_year": 1,
                "max_consecutive_days": 1,
                "applicable_to": ["probationary", "permanent"],
                "rules": "The resource will be entitled to avail 1-day paid leave either for Birthday or for Wedding Anniversary per year.",
                "eligibility": "1 Leave Per Annum",
                "choice": "either_birthday_or_anniversary",  # Either Birthday OR Wedding Anniversary
                "requires_medical_certificate": False,
                "carry_forward": False,
                "encashable": False
            },
            "BRL": {
                "name": "Bereavement Leave",
                "code": "BRL",
                "max_days_per_year": 3,
                "max_consecutive_days": 3,
                "applicable_to": ["permanent"],  # Only permanent resources
                "rules": "It is a paid leave that is available to an employee at the time of death or funeral of employee's immediate family member.",
                "eligibility": "3 Days Per Annum",
                "family_scope": "immediate_family_member",
                "occasions": ["death", "funeral"],
                "requires_medical_certificate": False,
                "carry_forward": False,
                "encashable": False
            },
            "ML": {
                "name": "Maternity Leave",
                "code": "ML",
                "max_days_per_year": 108,  # 108 days as per new policy
                "max_consecutive_days": 108,
                "applicable_to": ["permanent"],
                "gender_specific": "female",
                "rules": {
                    "eligibility": "Female employees are eligible for maternity leave of 108 days",
                    "timing": "Can be taken after 7 months of pregnancy or after childbirth, as per employee's requirement",
                    "advance_application": "Employee must apply for maternity leave at least 2 months in advance",
                    "medical_documents": "Submission of medical documents is mandatory"
                },
                "approval_flow": [
                    "Employee applies for leave",
                    "HR approval",
                    "Manager approval"
                ],
                "advance_notice_required": 60,  # 2 months in advance
                "pregnancy_timing": {
                    "after_7_months": True,
                    "after_childbirth": True,
                    "employee_choice": True
                },
                "requires_medical_certificate": True,
                "carry_forward": False,
                "encashable": False
            },
            "PL": {
                "name": "Paternity Leave",
                "code": "PL",
                "max_days_per_year": 3,
                "max_consecutive_days": 3,
                "applicable_to": ["permanent"],
                "gender_specific": "male",
                "rules": {
                    "eligibility": "Male employees are eligible for paternity leave of 3 days",
                    "timing": "The leave must be taken around the time of childbirth"
                },
                "approval_flow": [
                    "Employee applies for leave",
                    "HR approval", 
                    "Manager approval"
                ],
                "timing": "around_childbirth",
                "requires_medical_certificate": False,
                "carry_forward": False,
                "encashable": False
            },
            "BDL": {
                "name": "Blood Donation Leave",
                "code": "BDL",
                "max_days_per_year": 1,
                "max_consecutive_days": 1,
                "applicable_to": ["probationary", "permanent"],
                "rules": "Blood donation leave is a paid leave to the resource who donates blood on an emergency basis to his/her fellow colleagues who are working in the company.",
                "eligibility": "1 Day – i.e., on the day of Blood donation",
                "special_condition": "emergency_donation_to_colleague",
                "purpose": "Keeping in view of the weakness of the resource who donates blood",
                "scope": "fellow_colleagues_in_company",
                "timing": "day_of_donation",
                "requires_medical_certificate": False,
                "carry_forward": False,
                "encashable": False
            }
        }
        
        # Office timings and break schedules (Section 6)
        self.office_config = {
            "start_time": time(10, 0),  # 10:00 AM
            "end_time": time(19, 0),    # 7:00 PM
            "total_hours": 9,
            "grace_period_minutes": 15,
            "max_grace_periods_per_month": 3,
            "minimum_half_day_hours": 5,
            "minimum_full_day_hours": 9,
            "breaks": {
                "coffee_morning": {
                    "name": "Coffee / Tea Break",
                    "start": time(12, 0),    # 12:00 Noon
                    "end": time(12, 10),     # 12:10 PM
                    "duration": 10,          # 10 minutes
                    "type": "coffee_tea"
                },
                "lunch": {
                    "name": "Lunch Break", 
                    "start": time(13, 30),   # 1:30 PM
                    "end": time(14, 10),     # 2:10 PM
                    "duration": 40,          # 40 minutes
                    "type": "lunch"
                },
                "coffee_evening": {
                    "name": "Snack / Coffee / Tea Break",
                    "start": time(17, 0),    # 5:00 PM
                    "end": time(17, 10),     # 5:10 PM
                    "duration": 10,          # 10 minutes
                    "type": "snack_coffee_tea"
                }
            },
            "total_break_time": 60  # Total 1 hour break time during regular duty hours
        }
        
        # WFH policy configuration (Section 11)
        self.wfh_config = {
            "restricted_days": ["monday", "friday"],
            "requires_prior_approval": True,
            "min_notice_days": 1,  # Prior approval 1-2 days before
            "max_notice_days": 2,
            "avoid_before_after_holidays": True,
            "hr_intimation_required": True,
            "failure_to_inform_hr": "leave_or_lop",  # Days treated as leave/LOP if HR not informed
            "valid_reasons": {
                "medical_emergencies": {
                    "requires_medical_report": True,
                    "hr_evaluation_required": True,
                    "description": "Genuine medical emergencies with valid medical reports"
                },
                "emergency_situations": {
                    "requires_documentation": True,
                    "manager_approval_required": True,
                    "description": "Absolutely emergency situations with valid documentation"
                }
            },
            "strategic_timing": {
                "avoid_mondays_fridays": {
                    "reason": "Critical for team alignment and project progress",
                    "exception": "absolutely_emergency_with_valid_document"
                },
                "avoid_before_after_holidays": {
                    "reason": "Disrupts workflow continuity",
                    "consequence": "Holiday between leaves considered as leave/LOP if reason not accepted"
                }
            },
            "adhoc_requests": {
                "minimize": True,
                "impact": "Frequent changes impact team productivity and collaboration",
                "recommendation": "Plan WFH in advance"
            },
            "commitment_productivity": {
                "philosophy": "WFH choices reflect commitment",
                "balance": "Value work-life balance while maintaining dedication to team goals",
                "impact": "Consistent dedication contributes to individual productivity"
            }
        }
        
        # Attendance Policy Guidelines (Section 7)
        self.attendance_guidelines = {
            "late_login_beyond_grace": {
                "action_required": "written_permission_from_manager",
                "description": "If a resource is not able to log in on time/beyond the buffer/grace period, he/she has to obtain written permission from the reporting manager."
            },
            "shift_timing_changes": {
                "hr_intimation_required": True,
                "manager_approval_required": True,
                "description": "If any changes are required in the shift timings of a resource apart from the regular timings, an intimation has to be given to HR with the respective manager's approval."
            },
            "same_day_logout_missing": {
                "hr_intimation_required": True,
                "description": "If any resource's Log-In and do not Log out within the same day, that has to be intimated to HR."
            }
        }
        
        # Leave Categories (Section 8)
        self.leave_categories = {
            "planned_leave": {
                "name": "Planned Leave",
                "description": "Planned leave refers to a pre-planned schedule with prior intimation to respective officials.",
                "reasons": [
                    "Planned vacations", "Medical appointments", "Personal reasons", 
                    "Family activities", "Marriage events", "Similar reasons"
                ],
                "requires_prior_intimation": True
            },
            "unplanned_leave": {
                "name": "Unplanned Leave", 
                "description": "Unplanned leave refers to leave due to unplanned/emergency situations.",
                "reasons": [
                    "Sudden illness", "Family emergencies", "Transportation emergencies",
                    "Accidents", "Household emergencies", "Natural calamities"
                ],
                "emergency_nature": True
            },
            "unauthorized_leave": {
                "name": "Unauthorized Leave",
                "description": "If any resource is continuously absent from regular duties for more than 3 consecutive days without intimation, it will be treated as an unauthorized leave.",
                "threshold_days": 3,
                "disciplinary_action": "HR will initiate appropriate disciplinary action",
                "consecutive_absence_required": True
            }
        }

    def get_leave_types(self, employee_type: str = "permanent", gender: str = None) -> List[Dict]:
        """Get applicable leave types for an employee"""
        applicable_types = []
        
        for code, leave_type in self.leave_types.items():
            if employee_type in leave_type["applicable_to"]:
                # Check gender-specific leaves
                if "gender_specific" in leave_type:
                    if gender and gender.lower() == leave_type["gender_specific"]:
                        applicable_types.append({
                            "code": code,
                            "name": leave_type["name"],
                            "max_days": leave_type["max_days_per_year"],
                            "max_consecutive": leave_type["max_consecutive_days"],
                            "requires_certificate": leave_type["requires_medical_certificate"]
                        })
                else:
                    applicable_types.append({
                        "code": code,
                        "name": leave_type["name"],
                        "max_days": leave_type["max_days_per_year"],
                        "max_consecutive": leave_type["max_consecutive_days"],
                        "requires_certificate": leave_type["requires_medical_certificate"]
                    })
        
        return applicable_types

    def calculate_leave_balance(self, employee_id: int, employee_type: str, 
                              joining_date: date, current_date: date = None) -> List[LeaveBalance]:
        """Calculate leave balance based on employee type and joining date"""
        if current_date is None:
            current_date = date.today()
        
        balances = []
        current_year = current_date.year
        
        for code, leave_type in self.leave_types.items():
            if employee_type not in leave_type["applicable_to"]:
                continue
                
            # Calculate pro-rata allocation for the year
            if joining_date.year == current_year:
                # Pro-rata calculation for joining year
                months_worked = 12 - joining_date.month + 1
                if code == "CL" and employee_type == "probationary":
                    # Probationary employees get 1 leave per month from 2nd month
                    total_allocated = max(0, months_worked - 1)
                elif code == "CL":
                    # Regular employees get 1.5 leaves per month
                    total_allocated = (months_worked * 1.5)
                else:
                    # Other leaves are annual allocations
                    total_allocated = leave_type["max_days_per_year"]
            else:
                # Full year allocation
                if code == "CL" and employee_type == "probationary":
                    total_allocated = 12  # 1 per month
                else:
                    total_allocated = leave_type["max_days_per_year"]
            
            # Mock used leaves (in real implementation, fetch from database)
            used = 0  # This would be calculated from actual leave records
            
            balances.append(LeaveBalance(
                employee_id=employee_id,
                leave_type=leave_type["name"],
                total_allocated=total_allocated,
                used=used,
                balance=total_allocated - used,
                year=current_year
            ))
        
        return balances

    def validate_leave_request(self, request: LeaveRequestCreate, employee_data: Dict) -> Tuple[bool, str]:
        """Validate leave request against policy rules"""
        
        # Basic date validation
        if request.start_date > request.end_date:
            return False, "Start date cannot be after end date"
        
        if request.start_date < date.today():
            return False, "Cannot apply for past dates"
        
        # Get leave type configuration
        leave_type_code = None
        for code, config in self.leave_types.items():
            if config["name"] == request.leave_type:
                leave_type_code = code
                leave_config = config
                break
        
        if not leave_type_code:
            return False, "Invalid leave type"
        
        # Check if employee is eligible for this leave type
        employee_type = employee_data.get("type", "permanent")
        if employee_type not in leave_config["applicable_to"]:
            return False, f"This leave type is not applicable for {employee_type} employees"
        
        # Check gender-specific leaves
        if "gender_specific" in leave_config:
            employee_gender = employee_data.get("gender", "").lower()
            if employee_gender != leave_config["gender_specific"]:
                return False, f"This leave type is only applicable for {leave_config['gender_specific']} employees"
        
        # Special validation for Birthday/Anniversary Leave (BL)
        if leave_type_code == "BL":
            bl_validation_result = self.validate_birthday_anniversary_leave(request, employee_data)
            if not bl_validation_result[0]:
                return bl_validation_result
        
        # Special validation for Maternity Leave (ML)
        if leave_type_code == "ML":
            ml_validation_result = self.validate_maternity_leave(request, employee_data)
            if not ml_validation_result[0]:
                return ml_validation_result
        
        # Special validation for Paternity Leave (PL)
        if leave_type_code == "PL":
            pl_validation_result = self.validate_paternity_leave(request, employee_data)
            if not pl_validation_result[0]:
                return pl_validation_result
        
        # Calculate leave duration
        leave_duration = (request.end_date - request.start_date).days + 1
        
        # Check maximum consecutive days
        if leave_duration > leave_config["max_consecutive_days"]:
            return False, f"Maximum {leave_config['max_consecutive_days']} consecutive days allowed for {request.leave_type}"
        
        # Check if medical certificate is required
        if leave_config["requires_medical_certificate"] and not request.medical_certificate:
            return False, "Medical certificate is required for this leave type"
        
        # Check for clubbing with weekends/holidays
        if self._is_clubbed_with_holidays(request.start_date, request.end_date):
            return False, "Clubbing of leaves with weekends/holidays is strongly discouraged"
        
        # Check leave balance (mock implementation)
        # In real implementation, check actual balance from database
        
        return True, "Leave request is valid"

    def _is_clubbed_with_holidays(self, start_date: date, end_date: date) -> bool:
        """Check if leave is clubbed with weekends or holidays"""
        
        # Check if leave starts right after a weekend
        day_before_start = start_date - timedelta(days=1)
        if day_before_start.weekday() == 6:  # Sunday
            return True
        
        # Check if leave ends right before a weekend
        day_after_end = end_date + timedelta(days=1)
        if day_after_end.weekday() == 5:  # Saturday
            return True
        
        # Check for holidays (mock implementation)
        # In real implementation, check against holiday database
        holidays = self.get_holidays_for_year(start_date.year)
        
        for holiday in holidays:
            holiday_date = datetime.strptime(holiday["date"], "%Y-%m-%d").date()
            if (holiday_date == day_before_start or 
                holiday_date == day_after_end):
                return True
        
        return False

    def validate_wfh_request(self, wfh_request: WFHRequest) -> Tuple[bool, str]:
        """Validate Work From Home request"""
        
        # Check if it's a restricted day (Monday/Friday)
        weekday = wfh_request.date.strftime("%A").lower()
        if weekday in self.wfh_config["restricted_days"]:
            if not wfh_request.manager_approval_email:
                return False, f"WFH on {weekday.title()} requires manager approval with valid documentation"
        
        # Check minimum notice period
        notice_days = (wfh_request.date - date.today()).days
        if notice_days < self.wfh_config["min_notice_days"]:
            return False, f"WFH requests require at least {self.wfh_config['min_notice_days']} day(s) prior notice"
        
        # Check if it's before/after holidays
        if self.wfh_config["avoid_before_after_holidays"]:
            if self._is_adjacent_to_holiday(wfh_request.date):
                return False, "WFH requests immediately before or after holidays are discouraged"
        
        return True, "WFH request is valid"

    def _is_adjacent_to_holiday(self, request_date: date) -> bool:
        """Check if date is adjacent to a holiday"""
        holidays = self.get_holidays_for_year(request_date.year)
        
        for holiday in holidays:
            holiday_date = datetime.strptime(holiday["date"], "%Y-%m-%d").date()
            if abs((holiday_date - request_date).days) <= 1:
                return True
        
        return False

    def validate_birthday_anniversary_leave(self, request: LeaveRequestCreate, employee_data: Dict) -> Tuple[bool, str]:
        """
        Validate Birthday/Anniversary Leave (BL) restrictions:
        - Employee can only take leave for either birthday OR wedding anniversary in a year, not both
        - Must specify which occasion (birthday or anniversary) they're taking leave for
        """
        
        # Check if bl_occasion_type is specified
        if not hasattr(request, 'bl_occasion_type') or not request.bl_occasion_type:
            return False, "For Birthday/Anniversary leave, you must specify whether this is for 'birthday' or 'anniversary'"
        
        if request.bl_occasion_type not in ["birthday", "anniversary"]:
            return False, "Birthday/Anniversary leave occasion must be either 'birthday' or 'anniversary'"
        
        employee_id = employee_data.get("id")
        current_year = request.start_date.year
        
        # Check if employee has already taken BL leave this year
        existing_bl_leaves = self.get_bl_leaves_for_year(employee_id, current_year)
        
        if existing_bl_leaves:
            # Employee has already taken BL leave this year
            existing_occasion = existing_bl_leaves[0].get("occasion_type")
            
            if existing_occasion == request.bl_occasion_type:
                return False, f"You have already taken Birthday/Anniversary leave for your {request.bl_occasion_type} this year"
            else:
                return False, f"You have already taken Birthday/Anniversary leave for your {existing_occasion} this year. You can only take leave for either birthday OR anniversary per year, not both"
        
        # Validate that the requested date makes sense for the occasion
        if request.bl_occasion_type == "birthday":
            employee_dob = employee_data.get("date_of_birth")
            if employee_dob:
                # Convert to date if it's a datetime
                if isinstance(employee_dob, str):
                    employee_dob = datetime.strptime(employee_dob, "%Y-%m-%d").date()
                elif hasattr(employee_dob, 'date'):
                    employee_dob = employee_dob.date()
                
                # Check if the leave date is close to the birthday (within 7 days)
                birthday_this_year = employee_dob.replace(year=current_year)
                days_diff = abs((request.start_date - birthday_this_year).days)
                
                if days_diff > 7:
                    return False, f"Birthday leave should be taken within 7 days of your birthday ({birthday_this_year.strftime('%B %d')})"
        
        elif request.bl_occasion_type == "anniversary":
            wedding_anniversary = employee_data.get("wedding_anniversary_date")
            if wedding_anniversary:
                # Convert to date if it's a datetime
                if isinstance(wedding_anniversary, str):
                    wedding_anniversary = datetime.strptime(wedding_anniversary, "%Y-%m-%d").date()
                elif hasattr(wedding_anniversary, 'date'):
                    wedding_anniversary = wedding_anniversary.date()
                
                # Check if the leave date is close to the anniversary (within 7 days)
                anniversary_this_year = wedding_anniversary.replace(year=current_year)
                days_diff = abs((request.start_date - anniversary_this_year).days)
                
                if days_diff > 7:
                    return False, f"Anniversary leave should be taken within 7 days of your wedding anniversary ({anniversary_this_year.strftime('%B %d')})"
            else:
                return False, "Wedding anniversary date not found in your profile. Please update your profile to include your wedding anniversary date before applying for anniversary leave"
        
        return True, "Birthday/Anniversary leave validation passed"

    def get_bl_leaves_for_year(self, employee_id: int, year: int) -> List[Dict]:
        """
        Get Birthday/Anniversary leaves taken by employee in a specific year
        In real implementation, this would query the database
        """
        # Mock implementation - check MOCK_LEAVE_REQUESTS from router
        # In real system, this would query the database:
        # SELECT * FROM leave_requests WHERE employee_id = ? AND leave_type = 'Birthday / Wedding Anniversary Leave' AND YEAR(start_date) = ?
        
        # For now, we'll import and check the mock data
        try:
            from app.routers.leave import MOCK_LEAVE_REQUESTS
            
            bl_leaves = []
            for leave in MOCK_LEAVE_REQUESTS.values():
                if (leave["employee_id"] == employee_id and 
                    leave["leave_type"] == "Birthday / Wedding Anniversary Leave" and
                    datetime.fromisoformat(leave["start_date"]).year == year):
                    bl_leaves.append({
                        "id": leave["id"],
                        "occasion_type": leave.get("bl_occasion_type"),
                        "start_date": leave["start_date"],
                        "status": leave["status"]
                    })
            
            return bl_leaves
        except ImportError:
            # Fallback if import fails
            return []

    def validate_maternity_leave(self, request: LeaveRequestCreate, employee_data: Dict) -> Tuple[bool, str]:
        """
        Validate Maternity Leave (ML) request:
        - Only for female employees
        - 108 days maximum
        - Must apply at least 2 months in advance
        - Medical documents mandatory
        - Can be taken after 7 months of pregnancy or after childbirth
        """
        
        # Check gender (already checked in main validation, but double-check)
        if employee_data.get("gender", "").lower() != "female":
            return False, "Maternity leave is only available for female employees"
        
        # Check advance notice (2 months = 60 days)
        advance_notice_days = (request.start_date - date.today()).days
        if advance_notice_days < 60:
            return False, "Maternity leave must be applied at least 2 months (60 days) in advance"
        
        # Check medical certificate requirement
        if not request.medical_certificate:
            return False, "Medical documents are mandatory for maternity leave application"
        
        # Check leave duration (108 days maximum)
        leave_duration = (request.end_date - request.start_date).days + 1
        if leave_duration > 108:
            return False, "Maximum 108 days allowed for maternity leave"
        
        # Check if employee has already taken maternity leave this year
        employee_id = employee_data.get("id")
        current_year = request.start_date.year
        existing_ml_leaves = self.get_maternity_leaves_for_year(employee_id, current_year)
        
        if existing_ml_leaves:
            return False, "You have already taken maternity leave this year"
        
        # Additional validation for timing (after 7 months of pregnancy or after childbirth)
        # This would typically require additional fields in the request like expected_delivery_date
        # For now, we'll assume the timing is validated through medical documents
        
        return True, "Maternity leave validation passed"

    def validate_paternity_leave(self, request: LeaveRequestCreate, employee_data: Dict) -> Tuple[bool, str]:
        """
        Validate Paternity Leave (PL) request:
        - Only for male employees
        - 3 days maximum
        - Must be taken around the time of childbirth
        """
        
        # Check gender (already checked in main validation, but double-check)
        if employee_data.get("gender", "").lower() != "male":
            return False, "Paternity leave is only available for male employees"
        
        # Check leave duration (3 days maximum)
        leave_duration = (request.end_date - request.start_date).days + 1
        if leave_duration > 3:
            return False, "Maximum 3 days allowed for paternity leave"
        
        # Check if employee has already taken paternity leave this year
        employee_id = employee_data.get("id")
        current_year = request.start_date.year
        existing_pl_leaves = self.get_paternity_leaves_for_year(employee_id, current_year)
        
        if existing_pl_leaves:
            return False, "You have already taken paternity leave this year"
        
        # Additional validation for timing (around childbirth)
        # This would typically require additional fields like child_birth_date
        # For now, we'll assume the timing is appropriate based on the request
        
        return True, "Paternity leave validation passed"

    def get_maternity_leaves_for_year(self, employee_id: int, year: int) -> List[Dict]:
        """
        Get Maternity leaves taken by employee in a specific year
        In real implementation, this would query the database
        """
        try:
            from app.routers.leave import MOCK_LEAVE_REQUESTS
            
            ml_leaves = []
            for leave in MOCK_LEAVE_REQUESTS.values():
                if (leave["employee_id"] == employee_id and 
                    leave["leave_type"] == "Maternity Leave" and
                    datetime.fromisoformat(leave["start_date"]).year == year):
                    ml_leaves.append({
                        "id": leave["id"],
                        "start_date": leave["start_date"],
                        "end_date": leave["end_date"],
                        "status": leave["status"]
                    })
            
            return ml_leaves
        except ImportError:
            return []

    def get_paternity_leaves_for_year(self, employee_id: int, year: int) -> List[Dict]:
        """
        Get Paternity leaves taken by employee in a specific year
        In real implementation, this would query the database
        """
        try:
            from app.routers.leave import MOCK_LEAVE_REQUESTS
            
            pl_leaves = []
            for leave in MOCK_LEAVE_REQUESTS.values():
                if (leave["employee_id"] == employee_id and 
                    leave["leave_type"] == "Paternity Leave" and
                    datetime.fromisoformat(leave["start_date"]).year == year):
                    pl_leaves.append({
                        "id": leave["id"],
                        "start_date": leave["start_date"],
                        "end_date": leave["end_date"],
                        "status": leave["status"]
                    })
            
            return pl_leaves
        except ImportError:
            return []

    def get_holidays_for_year(self, year: int) -> List[Dict]:
        """Get holidays for a specific year"""
        # Mock holidays - in real implementation, fetch from database
        return [
            {"id": 1, "name": "New Year's Day", "date": f"{year}-01-01", "type": "National"},
            {"id": 2, "name": "Republic Day", "date": f"{year}-01-26", "type": "National"},
            {"id": 3, "name": "Independence Day", "date": f"{year}-08-15", "type": "National"},
            {"id": 4, "name": "Gandhi Jayanti", "date": f"{year}-10-02", "type": "National"},
            {"id": 5, "name": "Diwali", "date": f"{year}-11-12", "type": "National"},
            {"id": 6, "name": "Christmas", "date": f"{year}-12-25", "type": "National"},
            {"id": 7, "name": "Good Friday", "date": f"{year}-03-29", "type": "National"},
            {"id": 8, "name": "Holi", "date": f"{year}-03-13", "type": "National"}
        ]

    def calculate_working_days(self, start_date: date, end_date: date) -> int:
        """Calculate working days excluding weekends and holidays"""
        working_days = 0
        current_date = start_date
        holidays = self.get_holidays_for_year(start_date.year)
        holiday_dates = [datetime.strptime(h["date"], "%Y-%m-%d").date() for h in holidays]
        
        while current_date <= end_date:
            # Skip weekends (Saturday=5, Sunday=6)
            if current_date.weekday() < 5:  # Monday=0 to Friday=4
                # Skip holidays
                if current_date not in holiday_dates:
                    working_days += 1
            current_date += timedelta(days=1)
        
        return working_days

    def get_leave_calendar(self, month: int, year: int) -> Dict:
        """Get leave calendar for a specific month"""
        # Mock implementation - in real system, fetch from database
        calendar_data = {
            "month": month,
            "year": year,
            "leaves": [],
            "holidays": [],
            "working_days": 0
        }
        
        # Get holidays for the month
        holidays = self.get_holidays_for_year(year)
        for holiday in holidays:
            holiday_date = datetime.strptime(holiday["date"], "%Y-%m-%d").date()
            if holiday_date.month == month:
                calendar_data["holidays"].append(holiday)
        
        # Calculate working days
        first_day = date(year, month, 1)
        last_day = date(year, month, calendar.monthrange(year, month)[1])
        calendar_data["working_days"] = self.calculate_working_days(first_day, last_day)
        
        return calendar_data

    def check_unauthorized_absence(self, employee_id: int, absence_days: int) -> Dict:
        """Check for unauthorized absence and recommend disciplinary action"""
        if absence_days > 3:
            return {
                "is_unauthorized": True,
                "action_required": "disciplinary_action",
                "message": f"Employee has been absent for {absence_days} consecutive days without intimation. Initiate disciplinary action as per policy."
            }
        
        return {
            "is_unauthorized": False,
            "action_required": None,
            "message": "No unauthorized absence detected"
        }

    def calculate_late_login_penalty(self, late_logins_this_month: int) -> Dict:
        """Calculate penalty for late logins"""
        if late_logins_this_month <= 3:
            return {
                "penalty": None,
                "message": f"Grace period used: {late_logins_this_month}/3"
            }
        
        penalty_days = late_logins_this_month - 3
        return {
            "penalty": "half_day_deduction",
            "penalty_days": penalty_days,
            "message": f"Late login penalty: {penalty_days} half day(s) will be deducted"
        }

    def get_leave_statistics(self, employee_id: int, year: int) -> Dict:
        """Get comprehensive leave statistics for an employee"""
        # Mock implementation - in real system, calculate from database
        return {
            "total_leaves_taken": 8,
            "casual_leaves_used": 5,
            "sick_leaves_used": 2,
            "other_leaves_used": 1,
            "leaves_pending_approval": 1,
            "leaves_rejected": 0,
            "average_leave_duration": 1.5,
            "most_common_leave_type": "Casual Leave",
            "leave_pattern_analysis": {
                "frequent_monday_friday": False,
                "frequent_before_holidays": False,
                "long_leave_frequency": "Low"
            }
        }
    def get_policy_definitions(self) -> Dict:
        """Get comprehensive policy definitions and objectives"""
        return {
            "definitions": self.policy_definitions,
            "objectives": {
                "attendance_policy": {
                    "title": "Attendance Policy Objective",
                    "description": "Dhanush Group is encouraging all its resources to attend to regular duties within the specified time. The main objective is to promote the efficient operations of the company's productivity and client satisfaction.",
                    "key_points": [
                        "Encourage regular attendance within specified time",
                        "Promote efficient company operations", 
                        "Enhance overall productivity",
                        "Ensure client satisfaction through reliable service delivery"
                    ]
                },
                "leave_policy": {
                    "title": "Leave Policy Objective", 
                    "description": "Dhanush group believes that its resources should have opportunities to enjoy time, which is away from work to balance their family & professional life. The company gives the opportunity to its resource on genuine reasons to spend time with their family during the leave and take care of their personal needs.",
                    "key_points": [
                        "Work-life balance is a fundamental right",
                        "Family time is essential for employee well-being",
                        "Personal needs should be accommodated",
                        "Genuine reasons for leave are always considered"
                    ]
                }
            },
            "implementation_status": {
                "attendance_tracking": True,
                "leave_management": True,
                "work_life_balance": True,
                "family_friendly_policies": True,
                "productivity_monitoring": True,
                "client_satisfaction_focus": True
            }
        }

    def validate_policy_compliance(self, request_type: str, request_data: Dict) -> Tuple[bool, str, List[str]]:
        """Validate if a request complies with policy definitions and objectives"""
        compliance_issues = []
        
        if request_type == "leave":
            # Check if leave supports work-life balance objective
            if not request_data.get("reason"):
                compliance_issues.append("Leave reason required to ensure genuine need as per policy")
            
            # Check if proper approval process is followed
            if not request_data.get("manager_approval_required", True):
                compliance_issues.append("Manager approval required as per leave definition")
            
            # Check if it's for family/personal reasons (policy objective)
            family_keywords = ["family", "personal", "wedding", "birthday", "medical", "emergency"]
            reason = request_data.get("reason", "").lower()
            is_family_related = any(keyword in reason for keyword in family_keywords)
            
            if is_family_related:
                compliance_issues.append("✓ Supports work-life balance objective")
        
        elif request_type == "attendance":
            # Check attendance policy compliance
            if request_data.get("late_minutes", 0) > 15:
                compliance_issues.append("Exceeds grace period as per attendance policy")
            
            # Check productivity impact
            if request_data.get("consecutive_late_days", 0) > 3:
                compliance_issues.append("May impact productivity and client satisfaction")
        
        is_compliant = len([issue for issue in compliance_issues if not issue.startswith("✓")]) == 0
        message = "Policy compliant" if is_compliant else "Policy compliance issues found"
        
        return is_compliant, message, compliance_issues
    def get_break_timings(self) -> Dict[str, Any]:
        """
        Get break timings as per Section 6
        During regular duty hours, resources can utilize One Hour Break-time
        """
        return {
            "total_break_time": self.office_config["total_break_time"],
            "break_schedule": self.office_config["breaks"],
            "policy": "During the regular duty hours, the resources can utilize One Hour Break-time, during the below timings",
            "breaks_detail": [
                {
                    "name": "Coffee / Tea Break",
                    "time": "12:00 Noon to 12:10 PM",
                    "duration": "10 mins",
                    "type": "coffee_tea"
                },
                {
                    "name": "Lunch Break", 
                    "time": "1:30 PM to 2:10 PM",
                    "duration": "40 mins",
                    "type": "lunch"
                },
                {
                    "name": "Snack / Coffee / Tea Break",
                    "time": "5:00 PM to 5:10 PM", 
                    "duration": "10 mins",
                    "type": "snack_coffee_tea"
                }
            ]
        }
    
    def validate_break_timing(self, break_start: time, break_end: time) -> Dict[str, Any]:
        """Validate if break timing is within allowed break periods"""
        current_time = datetime.now().time()
        
        for break_name, break_info in self.office_config["breaks"].items():
            if break_info["start"] <= current_time <= break_info["end"]:
                return {
                    "is_valid_break_time": True,
                    "break_type": break_info["type"],
                    "break_name": break_info["name"],
                    "remaining_time": (datetime.combine(date.today(), break_info["end"]) - 
                                     datetime.combine(date.today(), current_time)).seconds // 60
                }
        
        return {
            "is_valid_break_time": False,
            "message": "Current time is not within designated break periods",
            "next_break": self._get_next_break_time(current_time)
        }
    
    def _get_next_break_time(self, current_time: time) -> Dict[str, str]:
        """Get the next available break time"""
        for break_name, break_info in self.office_config["breaks"].items():
            if current_time < break_info["start"]:
                return {
                    "break_name": break_info["name"],
                    "start_time": break_info["start"].strftime("%I:%M %p"),
                    "duration": f"{break_info['duration']} minutes"
                }
        return {"message": "No more breaks today"}
    
    def get_attendance_guidelines(self) -> Dict[str, Any]:
        """Get attendance policy guidelines as per Section 7"""
        return {
            "guidelines": self.attendance_guidelines,
            "summary": [
                "Written manager permission required for late login beyond grace period",
                "HR intimation with manager approval required for shift timing changes", 
                "HR intimation required if login without logout on same day"
            ]
        }
    
    def check_unauthorized_leave_status(self, employee_id: int, consecutive_absent_days: int) -> Dict[str, Any]:
        """
        Check for unauthorized leave as per Section 8
        More than 3 consecutive days without intimation = unauthorized leave
        """
        threshold = self.leave_categories["unauthorized_leave"]["threshold_days"]
        
        if consecutive_absent_days > threshold:
            return {
                "is_unauthorized": True,
                "consecutive_days": consecutive_absent_days,
                "threshold": threshold,
                "status": "unauthorized_leave",
                "disciplinary_action_required": True,
                "message": f"Employee absent for {consecutive_absent_days} consecutive days without intimation. HR disciplinary action required.",
                "policy_reference": self.leave_categories["unauthorized_leave"]["description"]
            }
        
        return {
            "is_unauthorized": False,
            "consecutive_days": consecutive_absent_days,
            "threshold": threshold,
            "status": "within_limits",
            "message": f"Consecutive absence ({consecutive_absent_days} days) is within policy limits"
        }
    
    def categorize_leave_request(self, leave_data: Dict) -> Dict[str, Any]:
        """
        Categorize leave request as per Section 8
        Planned, Unplanned, or Unauthorized
        """
        advance_notice_days = leave_data.get("advance_notice_days", 0)
        reason = leave_data.get("reason", "").lower()
        
        # Check for planned leave indicators
        planned_reasons = [r.lower() for r in self.leave_categories["planned_leave"]["reasons"]]
        unplanned_reasons = [r.lower() for r in self.leave_categories["unplanned_leave"]["reasons"]]
        
        is_planned = any(keyword in reason for keyword in ["vacation", "appointment", "marriage", "planned"])
        is_emergency = any(keyword in reason for keyword in ["emergency", "sudden", "accident", "illness"])
        
        if advance_notice_days >= 1 and (is_planned or not is_emergency):
            return {
                "category": "planned_leave",
                "description": self.leave_categories["planned_leave"]["description"],
                "requires_prior_intimation": True,
                "advance_notice_provided": advance_notice_days
            }
        elif is_emergency or advance_notice_days == 0:
            return {
                "category": "unplanned_leave", 
                "description": self.leave_categories["unplanned_leave"]["description"],
                "emergency_nature": True,
                "requires_documentation": True
            }
        else:
            return {
                "category": "planned_leave",
                "description": self.leave_categories["planned_leave"]["description"],
                "requires_prior_intimation": True
            }
    
    def validate_leave_type_eligibility(self, employee_data: Dict, leave_type_code: str, child_number: int = 1) -> Dict[str, Any]:
        """
        Enhanced leave type eligibility validation as per Section 9 detailed rules
        """
        if leave_type_code not in self.leave_types:
            return {"eligible": False, "reason": "Invalid leave type"}
        
        leave_type = self.leave_types[leave_type_code]
        employee_type = employee_data.get("type", "permanent")
        employee_gender = employee_data.get("gender", "").lower()
        joining_date = datetime.strptime(employee_data.get("joining_date", "2023-01-01"), "%Y-%m-%d").date()
        
        # Check basic eligibility
        if employee_type not in leave_type["applicable_to"]:
            return {
                "eligible": False,
                "reason": f"{leave_type['name']} is only applicable to {', '.join(leave_type['applicable_to'])} employees"
            }
        
        # Gender-specific validation
        if "gender_specific" in leave_type and employee_gender != leave_type["gender_specific"]:
            return {
                "eligible": False,
                "reason": f"{leave_type['name']} is only applicable to {leave_type['gender_specific']} employees"
            }
        
        # Special validations per leave type
        validation_result = {"eligible": True, "details": {}}
        
        if leave_type_code == "CL":
            # Casual Leave specific validation
            if employee_type == "probationary":
                months_since_joining = (date.today().year - joining_date.year) * 12 + (date.today().month - joining_date.month)
                if months_since_joining < 2:
                    return {
                        "eligible": False,
                        "reason": "Probationary employees can avail casual leave from the second month after joining"
                    }
                validation_result["details"]["monthly_entitlement"] = leave_type["probationary_rules"]["monthly_entitlement"]
            else:
                validation_result["details"]["annual_entitlement"] = leave_type["permanent_rules"]["annual_entitlement"]
                validation_result["details"]["monthly_entitlement"] = leave_type["permanent_rules"]["monthly_entitlement"]
        
        elif leave_type_code == "ML":
            # Maternity Leave specific validation
            work_days_requirement = 160
            validation_result["details"]["work_requirement"] = f"Must work minimum {work_days_requirement} days in past 12 months"
            
            if child_number == 1:
                validation_result["details"]["leave_days"] = leave_type["eligibility"]["first_child"]
            else:
                validation_result["details"]["leave_days"] = leave_type["eligibility"]["second_child"]
        
        elif leave_type_code == "BRL":
            # Bereavement Leave specific validation
            validation_result["details"]["scope"] = "Available at the time of death or funeral of immediate family member"
        
        elif leave_type_code == "BDL":
            # Blood Donation Leave specific validation
            validation_result["details"]["condition"] = "Only for emergency blood donation to fellow colleagues in the company"
            validation_result["details"]["timing"] = "On the day of blood donation"
        
        return validation_result
    
    def get_national_state_holidays(self, year: int = None) -> Dict[str, Any]:
        """
        Get National & State Holidays as per Section 10
        HR department publishes approved holiday list annually
        """
        if year is None:
            year = datetime.now().year
        
        # Enhanced holiday list with national and state holidays
        holidays = [
            # National Holidays
            {"id": 1, "name": "New Year's Day", "date": f"{year}-01-01", "type": "National", "category": "Fixed"},
            {"id": 2, "name": "Republic Day", "date": f"{year}-01-26", "type": "National", "category": "Fixed"},
            {"id": 3, "name": "Independence Day", "date": f"{year}-08-15", "type": "National", "category": "Fixed"},
            {"id": 4, "name": "Gandhi Jayanti", "date": f"{year}-10-02", "type": "National", "category": "Fixed"},
            {"id": 5, "name": "Christmas", "date": f"{year}-12-25", "type": "National", "category": "Fixed"},
            
            # Religious/Cultural Holidays (dates may vary by year)
            {"id": 6, "name": "Holi", "date": f"{year}-03-13", "type": "National", "category": "Religious"},
            {"id": 7, "name": "Good Friday", "date": f"{year}-03-29", "type": "National", "category": "Religious"},
            {"id": 8, "name": "Eid ul-Fitr", "date": f"{year}-04-21", "type": "National", "category": "Religious"},
            {"id": 9, "name": "Dussehra", "date": f"{year}-10-15", "type": "National", "category": "Religious"},
            {"id": 10, "name": "Diwali", "date": f"{year}-11-12", "type": "National", "category": "Religious"},
            
            # State Holidays (Telangana specific)
            {"id": 11, "name": "Telangana Formation Day", "date": f"{year}-06-02", "type": "State", "category": "State Specific"},
            {"id": 12, "name": "Bonalu Festival", "date": f"{year}-07-20", "type": "State", "category": "Cultural"},
        ]
        
        return {
            "year": year,
            "holidays": holidays,
            "total_holidays": len(holidays),
            "national_holidays": len([h for h in holidays if h["type"] == "National"]),
            "state_holidays": len([h for h in holidays if h["type"] == "State"]),
            "hr_publication_note": "Every year, the HR department will publish the approved holiday list of the year over an e-mail to all the resources working with the Dhanush group.",
            "categories": {
                "Fixed": [h for h in holidays if h["category"] == "Fixed"],
                "Religious": [h for h in holidays if h["category"] == "Religious"], 
                "State Specific": [h for h in holidays if h["category"] == "State Specific"],
                "Cultural": [h for h in holidays if h["category"] == "Cultural"]
            }
        }
    
    def publish_holiday_list(self, year: int, hr_user_id: int) -> Dict[str, Any]:
        """
        Simulate HR department publishing holiday list via email
        As per Section 10 requirement
        """
        holiday_data = self.get_national_state_holidays(year)
        
        publication_record = {
            "year": year,
            "published_by": hr_user_id,
            "published_at": datetime.now().isoformat(),
            "total_holidays": holiday_data["total_holidays"],
            "email_sent": True,
            "recipients": "all_dhanush_group_resources",
            "publication_method": "email",
            "status": "published"
        }
        
        return {
            "success": True,
            "message": f"Holiday list for {year} published successfully to all Dhanush Group resources",
            "publication_record": publication_record,
            "holiday_summary": {
                "total_holidays": holiday_data["total_holidays"],
                "national_holidays": holiday_data["national_holidays"],
                "state_holidays": holiday_data["state_holidays"]
            }
        }
    
    # Section 11: Enhanced WFH Policy Methods
    
    def validate_wfh_request_enhanced(self, wfh_request: WFHRequest, employee_data: Dict = None) -> Tuple[bool, str, Dict]:
        """
        Enhanced WFH request validation as per Section 11
        Returns: (is_valid, message, validation_details)
        """
        validation_details = {
            "prior_approval_check": False,
            "hr_intimation_check": False,
            "valid_reason_check": False,
            "strategic_timing_check": False,
            "adhoc_request_check": False,
            "warnings": [],
            "requirements": []
        }
        
        # Check prior approval (1-2 days before)
        notice_days = (wfh_request.date - date.today()).days
        if notice_days < self.wfh_config["min_notice_days"]:
            validation_details["warnings"].append(f"Less than {self.wfh_config['min_notice_days']} day notice provided")
            if notice_days < 0:
                return False, "WFH requests cannot be made for past dates", validation_details
        elif notice_days > self.wfh_config["max_notice_days"]:
            validation_details["warnings"].append("WFH request made too far in advance")
        else:
            validation_details["prior_approval_check"] = True
        
        # Check HR intimation requirement
        if not hasattr(wfh_request, 'hr_informed') or not wfh_request.hr_informed:
            validation_details["requirements"].append("HR department must be informed about WFH day")
            validation_details["warnings"].append("Failure to inform HR will result in day being treated as leave/LOP")
        else:
            validation_details["hr_intimation_check"] = True
        
        # Check valid reasons
        reason_lower = wfh_request.reason.lower()
        is_medical_emergency = any(keyword in reason_lower for keyword in ["medical", "emergency", "health", "doctor", "hospital"])
        is_emergency = any(keyword in reason_lower for keyword in ["emergency", "urgent", "critical"])
        
        if is_medical_emergency:
            if not hasattr(wfh_request, 'medical_report') or not wfh_request.medical_report:
                validation_details["requirements"].append("Medical report required for medical emergency WFH")
            else:
                validation_details["valid_reason_check"] = True
                validation_details["requirements"].append("HR will evaluate and decide WFH vs leave classification")
        elif is_emergency:
            if not hasattr(wfh_request, 'emergency_documentation') or not wfh_request.emergency_documentation:
                validation_details["requirements"].append("Valid documentation required for emergency WFH")
            else:
                validation_details["valid_reason_check"] = True
        else:
            validation_details["warnings"].append("Ensure reason is valid as per WFH policy")
        
        # Check strategic timing (avoid Mondays/Fridays)
        weekday = wfh_request.date.strftime("%A").lower()
        if weekday in self.wfh_config["restricted_days"]:
            if not (is_emergency and hasattr(wfh_request, 'emergency_documentation')):
                return False, f"WFH on {weekday.title()} not allowed unless absolutely emergency with valid documentation", validation_details
            else:
                validation_details["warnings"].append(f"WFH on {weekday.title()} approved due to emergency with documentation")
        
        validation_details["strategic_timing_check"] = True
        
        # Check holiday adjacency
        if self._is_adjacent_to_holiday(wfh_request.date):
            validation_details["warnings"].append("WFH before/after holidays disrupts workflow continuity")
            validation_details["requirements"].append("If reason not accepted by HR, holiday between leaves will be considered leave/LOP")
        
        # Check for ad-hoc pattern (if employee data available)
        if employee_data:
            recent_wfh_count = employee_data.get("recent_wfh_requests", 0)
            if recent_wfh_count > 2:  # More than 2 WFH in recent period
                validation_details["warnings"].append("Frequent WFH requests detected - minimize ad-hoc requests")
                validation_details["adhoc_request_check"] = False
            else:
                validation_details["adhoc_request_check"] = True
        
        # Overall validation
        critical_checks = [
            validation_details["prior_approval_check"] or notice_days >= 0,  # At least not past date
            validation_details["strategic_timing_check"]
        ]
        
        if all(critical_checks):
            return True, "WFH request validation passed with requirements", validation_details
        else:
            return False, "WFH request validation failed", validation_details
    
    def get_wfh_policy_details(self) -> Dict[str, Any]:
        """Get comprehensive WFH policy details as per Section 11"""
        return {
            "section_11_wfh_policy": {
                "title": "Work From Home Policy",
                "importance": "Crucial role in maintaining productivity, collaboration, and employee satisfaction",
                "approval_process": {
                    "prior_approval": {
                        "requirement": "Employees must seek prior approval 1-2 days before from respective managers",
                        "purpose": "Ensures proper planning and coordination"
                    },
                    "hr_intimation": {
                        "requirement": "Employees must inform HR department about WFH days",
                        "consequence": "Failure results in days being treated as leave/LOP"
                    }
                },
                "valid_reasons": self.wfh_config["valid_reasons"],
                "strategic_timing": self.wfh_config["strategic_timing"],
                "adhoc_requests": self.wfh_config["adhoc_requests"],
                "commitment_productivity": self.wfh_config["commitment_productivity"]
            },
            "configuration": self.wfh_config
        }
    
    def evaluate_wfh_medical_emergency(self, wfh_data: Dict) -> Dict[str, Any]:
        """
        HR evaluation for medical emergency WFH requests
        Returns classification decision
        """
        medical_report_quality = wfh_data.get("medical_report_quality", "good")  # good, fair, poor
        emergency_severity = wfh_data.get("emergency_severity", "moderate")  # high, moderate, low
        employee_history = wfh_data.get("employee_wfh_history", "good")  # good, fair, poor
        
        # HR decision logic
        if medical_report_quality == "good" and emergency_severity in ["high", "moderate"]:
            classification = "wfh_approved"
            message = "Medical emergency WFH approved based on valid medical report"
        elif medical_report_quality == "fair" and emergency_severity == "high":
            classification = "wfh_approved"
            message = "Medical emergency WFH approved due to high severity"
        else:
            classification = "leave_classification"
            message = "Request classified as leave due to insufficient medical documentation"
        
        return {
            "classification": classification,
            "message": message,
            "hr_decision": {
                "medical_report_quality": medical_report_quality,
                "emergency_severity": emergency_severity,
                "employee_history": employee_history,
                "decision_date": datetime.now().isoformat(),
                "requires_follow_up": classification == "leave_classification"
            }
        }
    
    def check_wfh_commitment_impact(self, employee_id: int, wfh_frequency: int, productivity_metrics: Dict = None) -> Dict[str, Any]:
        """
        Analyze WFH commitment and productivity impact
        """
        if productivity_metrics is None:
            productivity_metrics = {"task_completion": 85, "team_collaboration": 80, "goal_achievement": 90}
        
        # Commitment analysis
        if wfh_frequency <= 2:  # 2 or fewer WFH per month
            commitment_level = "high"
            impact_assessment = "Positive - demonstrates balanced approach"
        elif wfh_frequency <= 4:  # 3-4 WFH per month
            commitment_level = "moderate"
            impact_assessment = "Neutral - monitor productivity metrics"
        else:  # 5+ WFH per month
            commitment_level = "needs_attention"
            impact_assessment = "Requires review - frequent WFH may impact team collaboration"
        
        # Productivity correlation
        avg_productivity = sum(productivity_metrics.values()) / len(productivity_metrics)
        if avg_productivity >= 85:
            productivity_impact = "positive"
        elif avg_productivity >= 70:
            productivity_impact = "neutral"
        else:
            productivity_impact = "negative"
        
        return {
            "employee_id": employee_id,
            "wfh_frequency_monthly": wfh_frequency,
            "commitment_level": commitment_level,
            "impact_assessment": impact_assessment,
            "productivity_metrics": productivity_metrics,
            "avg_productivity": avg_productivity,
            "productivity_impact": productivity_impact,
            "recommendations": self._get_wfh_recommendations(commitment_level, productivity_impact),
            "policy_reminder": "WFH choices reflect commitment. Consistent dedication to team goals contributes to individual productivity."
        }
    
    def _get_wfh_recommendations(self, commitment_level: str, productivity_impact: str) -> List[str]:
        """Get personalized WFH recommendations"""
        recommendations = []
        
        if commitment_level == "needs_attention":
            recommendations.extend([
                "Consider reducing WFH frequency to improve team collaboration",
                "Schedule regular in-office days for team alignment",
                "Focus on maintaining productivity metrics during WFH days"
            ])
        
        if productivity_impact == "negative":
            recommendations.extend([
                "Review WFH setup and environment for productivity optimization",
                "Increase communication frequency with team during WFH",
                "Consider manager consultation for WFH best practices"
            ])
        
        if commitment_level == "high" and productivity_impact == "positive":
            recommendations.append("Excellent WFH balance - continue current approach")
        
        return recommendations
    
    def generate_wfh_analytics(self, department: str = None, time_period: str = "monthly") -> Dict[str, Any]:
        """Generate WFH analytics for management review"""
        # Mock analytics data - in real implementation, fetch from database
        analytics = {
            "time_period": time_period,
            "department": department or "All Departments",
            "total_wfh_requests": 45,
            "approved_requests": 38,
            "rejected_requests": 7,
            "approval_rate": 84.4,
            "reasons_breakdown": {
                "medical_emergency": 15,
                "personal_emergency": 12,
                "planned_wfh": 8,
                "other": 10
            },
            "day_wise_distribution": {
                "monday": 2,  # Restricted day
                "tuesday": 12,
                "wednesday": 15,
                "thursday": 13,
                "friday": 3   # Restricted day
            },
            "hr_intimation_compliance": {
                "informed_hr": 35,
                "failed_to_inform": 10,
                "compliance_rate": 77.8
            },
            "productivity_correlation": {
                "high_productivity_wfh": 28,
                "moderate_productivity_wfh": 8,
                "low_productivity_wfh": 2,
                "avg_productivity_score": 82.5
            },
            "policy_violations": {
                "monday_friday_requests": 5,
                "holiday_adjacent_requests": 8,
                "insufficient_notice": 3,
                "no_hr_intimation": 10
            }
        }
        
        return analytics
    # ============================================
    # ENHANCED BUSINESS METHODS
    # ============================================
    
    def validate_encashment_eligibility(self, employee_id: int, leave_type: str, days_to_encash: float) -> Tuple[bool, str]:
        """Validate if employee is eligible for leave encashment"""
        if leave_type not in self.leave_types:
            return False, f"Invalid leave type: {leave_type}"
        
        leave_config = self.leave_types[leave_type]
        
        if not leave_config.get("encashable", False):
            return False, f"{leave_config['name']} is not eligible for encashment"
        
        # Check minimum balance requirement (typically 5 days minimum balance)
        current_balance = self.get_current_leave_balance(employee_id, leave_type)
        if current_balance - days_to_encash < 5:
            return False, "Minimum 5 days balance must be maintained after encashment"
        
        return True, "Eligible for encashment"
    
    def calculate_encashment_amount(self, salary: float, days_to_encash: float) -> float:
        """Calculate encashment amount based on salary and days"""
        daily_salary = salary / 30  # Assuming 30 days per month
        return daily_salary * days_to_encash
    
    def validate_carry_forward_eligibility(self, employee_id: int, leave_type: str, days_to_carry: float) -> Tuple[bool, str]:
        """Validate if employee is eligible for leave carry forward"""
        if leave_type not in self.leave_types:
            return False, f"Invalid leave type: {leave_type}"
        
        leave_config = self.leave_types[leave_type]
        
        if not leave_config.get("carry_forward", False):
            return False, f"{leave_config['name']} cannot be carried forward"
        
        # Check maximum carry forward limit (typically 5 days)
        if days_to_carry > 5:
            return False, "Maximum 5 days can be carried forward"
        
        return True, "Eligible for carry forward"
    
    def get_resignation_notice_period_restrictions(self, employee_id: int, notice_start: date, notice_end: date) -> Dict[str, Any]:
        """Get leave restrictions during resignation notice period"""
        restrictions = {
            "notice_period_start": notice_start.isoformat(),
            "notice_period_end": notice_end.isoformat(),
            "restrictions": {
                "casual_leave": "Not allowed during notice period",
                "annual_leave": "Requires special approval",
                "sick_leave": "Allowed with medical certificate",
                "emergency_leave": "Case-by-case basis"
            },
            "encashment_eligible": True,
            "carry_forward_eligible": False,
            "pending_leaves_action": "Must be settled before last working day"
        }
        return restrictions
    
    def calculate_shift_based_leaves(self, calculation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate leaves based on different shift timings"""
        shift_type = calculation_data.get("shift_type", "regular")
        hours_per_day = calculation_data.get("hours_per_day", 9)
        
        if shift_type == "night_shift":
            # Night shift employees get additional considerations
            leave_multiplier = 1.1
        elif shift_type == "rotational":
            # Rotational shift employees
            leave_multiplier = 1.05
        else:
            # Regular shift
            leave_multiplier = 1.0
        
        base_leave_days = calculation_data.get("requested_days", 1)
        adjusted_leave_days = base_leave_days * leave_multiplier
        
        return {
            "shift_type": shift_type,
            "base_days": base_leave_days,
            "adjusted_days": round(adjusted_leave_days, 2),
            "multiplier": leave_multiplier,
            "reason": f"Shift-based adjustment for {shift_type}"
        }
    
    def analyze_attendance_leave_correlation(self, employee_id: int, year: int) -> Dict[str, Any]:
        """Analyze correlation between attendance patterns and leave usage"""
        # Mock correlation analysis
        correlation_data = {
            "employee_id": employee_id,
            "year": year,
            "attendance_rate": 92.5,
            "leave_utilization_rate": 78.3,
            "patterns": {
                "monday_friday_leaves": 35,  # Percentage of leaves on Mon/Fri
                "post_holiday_leaves": 12,   # Leaves taken after holidays
                "sick_leave_clustering": 8   # Sick leaves in clusters
            },
            "recommendations": [
                "Monitor Monday/Friday leave patterns",
                "Review sick leave clustering for potential abuse",
                "Encourage better leave planning"
            ],
            "risk_score": "Medium",
            "compliance_score": 85
        }
        return correlation_data
    
    def generate_advanced_analytics(self, analytics_request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate advanced analytics with predictive insights"""
        analytics_type = analytics_request.get("type", "comprehensive")
        
        advanced_analytics = {
            "analytics_type": analytics_type,
            "predictive_insights": {
                "peak_leave_months": ["December", "April", "May"],
                "expected_leave_requests_next_quarter": 45,
                "departments_at_risk": ["Engineering", "Sales"],
                "leave_trend": "Increasing by 8% annually"
            },
            "cost_analysis": {
                "total_leave_cost": 125000,
                "encashment_liability": 35000,
                "replacement_cost": 18000
            },
            "policy_effectiveness": {
                "approval_rate": 91.2,
                "policy_compliance": 87.5,
                "employee_satisfaction": 4.2
            },
            "recommendations": [
                "Implement leave planning workshops",
                "Review encashment policy limits",
                "Enhance mobile leave application process"
            ]
        }
        return advanced_analytics
    
    def check_comprehensive_policy_compliance(self, employee_id: int, compliance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check comprehensive policy compliance for leave requests"""
        leave_type = compliance_data.get("leave_type")
        start_date = datetime.strptime(compliance_data.get("start_date"), "%Y-%m-%d").date()
        end_date = datetime.strptime(compliance_data.get("end_date"), "%Y-%m-%d").date()
        
        compliance_checks = {
            "leave_type_valid": leave_type in self.leave_types,
            "advance_notice_given": (start_date - date.today()).days >= 1,
            "not_adjacent_to_weekend": True,  # Would check actual dates
            "not_adjacent_to_holiday": True,  # Would check against holiday calendar
            "within_balance_limits": True,    # Would check actual balance
            "manager_approval_required": True,
            "hr_approval_required": leave_type in ["ML", "BRL"],
            "medical_certificate_required": leave_type == "SL" and (end_date - start_date).days > 2
        }
        
        compliance_score = sum(compliance_checks.values()) / len(compliance_checks) * 100
        
        return {
            "compliant": compliance_score >= 80,
            "compliance_score": compliance_score,
            "checks": compliance_checks,
            "violations": [k for k, v in compliance_checks.items() if not v],
            "recommendations": self._get_compliance_recommendations(compliance_checks)
        }
    
    def _get_compliance_recommendations(self, checks: Dict[str, bool]) -> List[str]:
        """Get recommendations based on compliance check results"""
        recommendations = []
        
        if not checks.get("advance_notice_given"):
            recommendations.append("Provide at least 1 day advance notice for leave requests")
        
        if not checks.get("not_adjacent_to_weekend"):
            recommendations.append("Avoid taking leaves adjacent to weekends without valid reason")
        
        if not checks.get("within_balance_limits"):
            recommendations.append("Ensure sufficient leave balance before applying")
        
        return recommendations
    
    def get_role_based_dashboard_data(self, user_role: str, employee_id: int) -> Dict[str, Any]:
        """Get role-specific dashboard data"""
        base_data = {
            "user_role": user_role,
            "employee_id": employee_id,
            "timestamp": datetime.now().isoformat()
        }
        
        if user_role == "employee":
            base_data.update({
                "my_leave_balance": self.get_current_leave_balance(employee_id, "CL"),
                "pending_requests": 2,
                "upcoming_holidays": 3,
                "quick_actions": ["Apply Leave", "Check Balance", "View Calendar"]
            })
        
        elif user_role == "manager":
            base_data.update({
                "team_pending_approvals": 5,
                "team_on_leave_today": 2,
                "team_wfh_today": 3,
                "quick_actions": ["Approve Leaves", "Team Calendar", "Analytics"]
            })
        
        elif user_role in ["hr", "admin"]:
            base_data.update({
                "total_pending_approvals": 12,
                "employees_on_leave_today": 8,
                "policy_violations": 3,
                "quick_actions": ["Bulk Approve", "Analytics", "Policy Management", "Reports"]
            })
        
        return base_data
    
    def execute_automated_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute automated leave workflow processes"""
        workflow_type = workflow_data.get("type", "reminder")
        
        if workflow_type == "reminder":
            # Send leave balance reminders
            result = {
                "workflow_type": "reminder",
                "emails_sent": 45,
                "success_rate": 98.5,
                "failed_deliveries": 1
            }
        
        elif workflow_type == "auto_approval":
            # Auto-approve certain types of leaves
            result = {
                "workflow_type": "auto_approval",
                "requests_processed": 12,
                "auto_approved": 8,
                "requires_manual_review": 4
            }
        
        elif workflow_type == "escalation":
            # Escalate pending requests
            result = {
                "workflow_type": "escalation",
                "escalated_requests": 6,
                "notifications_sent": 18,
                "success": True
            }
        
        else:
            result = {"error": "Unknown workflow type"}
        
        result["success"] = True
        return result
    
    def get_mobile_optimized_data(self, employee_id: int) -> Dict[str, Any]:
        """Get mobile-optimized leave data"""
        mobile_data = {
            "employee_id": employee_id,
            "quick_stats": {
                "cl_balance": 12,
                "sl_balance": 8,
                "pending_requests": 1,
                "next_holiday": "2024-03-15"
            },
            "recent_requests": [
                {"id": 1, "type": "CL", "dates": "2024-02-15 to 2024-02-16", "status": "approved"},
                {"id": 2, "type": "SL", "dates": "2024-01-20", "status": "approved"}
            ],
            "quick_actions": [
                {"action": "apply_leave", "label": "Apply Leave", "icon": "calendar"},
                {"action": "check_balance", "label": "Check Balance", "icon": "clock"},
                {"action": "wfh_request", "label": "WFH Request", "icon": "home"}
            ],
            "notifications": [
                {"type": "reminder", "message": "Your leave balance expires in 60 days"},
                {"type": "approval", "message": "Your leave request has been approved"}
            ]
        }
        return mobile_data
    
    def integrate_with_smhr_system(self, smhr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate with SMHR system"""
        integration_result = {
            "integration_type": "SMHR",
            "data_synced": True,
            "records_processed": smhr_data.get("record_count", 0),
            "sync_timestamp": datetime.now().isoformat(),
            "success": True,
            "message": "Successfully integrated with SMHR system"
        }
        return integration_result
    
    def integrate_with_payroll_system(self, payroll_data: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate with payroll system"""
        integration_result = {
            "integration_type": "Payroll",
            "leave_deductions_calculated": True,
            "encashment_amounts_processed": True,
            "employees_affected": payroll_data.get("employee_count", 0),
            "total_amount": payroll_data.get("total_amount", 0),
            "sync_timestamp": datetime.now().isoformat(),
            "success": True,
            "message": "Successfully integrated with payroll system"
        }
        return integration_result
    
    def get_leave_audit_trail(self, request_id: int) -> Dict[str, Any]:
        """Get complete audit trail for a leave request"""
        # Mock audit trail data
        audit_trail = {
            "request_id": request_id,
            "audit_events": [
                {
                    "timestamp": "2024-01-15T10:30:00",
                    "event": "request_created",
                    "user": "John Doe (Employee)",
                    "details": "Leave request submitted"
                },
                {
                    "timestamp": "2024-01-15T14:20:00",
                    "event": "manager_review",
                    "user": "Jane Smith (Manager)",
                    "details": "Request reviewed and approved"
                },
                {
                    "timestamp": "2024-01-16T09:15:00",
                    "event": "hr_notification",
                    "user": "System",
                    "details": "HR notified of approval"
                }
            ],
            "current_status": "approved",
            "total_events": 3,
            "compliance_score": 95
        }
        return audit_trail
    
    def get_current_leave_balance(self, employee_id: int, leave_type: str) -> float:
        """Get current leave balance for employee and leave type"""
        # Mock implementation - would query database in real system
        mock_balances = {
            "CL": 12.5,
            "SL": 8.0,
            "AL": 15.0,
            "PL": 3.0
        }
        return mock_balances.get(leave_type, 0.0)
    
    def publish_holidays(self, holidays: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Publish holidays for the year"""
        published_holidays = []
        for holiday in holidays:
            published_holiday = {
                "id": len(published_holidays) + 1,
                "name": holiday.get("name"),
                "date": holiday.get("date"),
                "type": holiday.get("type", "national"),
                "is_optional": holiday.get("is_optional", False),
                "published_at": datetime.now().isoformat(),
                "published_by": "HR Department"
            }
            published_holidays.append(published_holiday)
        
        return published_holidays
    
    def generate_leave_report(self, year: int, department: Optional[str], format: str) -> Dict[str, Any]:
        """Generate comprehensive leave report"""
        report_data = {
            "report_id": f"LEAVE_REPORT_{year}_{datetime.now().strftime('%Y%m%d')}",
            "year": year,
            "department": department,
            "format": format,
            "summary": {
                "total_employees": 150,
                "total_leave_requests": 456,
                "approved_requests": 420,
                "rejected_requests": 36,
                "total_leave_days": 1234
            },
            "department_breakdown": [
                {"department": "Engineering", "employees": 60, "leave_days": 520},
                {"department": "Sales", "employees": 40, "leave_days": 380},
                {"department": "Marketing", "employees": 30, "leave_days": 290},
                {"department": "HR", "employees": 20, "leave_days": 44}
            ],
            "leave_type_breakdown": [
                {"type": "Casual Leave", "requests": 280, "days": 560},
                {"type": "Sick Leave", "requests": 120, "days": 240},
                {"type": "Annual Leave", "requests": 56, "days": 434}
            ],
            "generated_at": datetime.now().isoformat(),
            "file_size": "2.5 MB"
        }
        return report_data
    
    def update_policy_configurations(self, policy_updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update leave policy configurations"""
        updated_policies = {
            "updated_sections": list(policy_updates.keys()),
            "update_timestamp": datetime.now().isoformat(),
            "updated_by": "HR Admin",
            "changes": policy_updates,
            "effective_date": policy_updates.get("effective_date", date.today().isoformat()),
            "notification_sent": True
        }
        return updated_policies