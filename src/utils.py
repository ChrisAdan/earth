from dataclasses import dataclass
from enum import IntEnum
MIN_AGE = 18
MAX_AGE = 85

# Common US job titles by category
US_JOB_TITLES = [
    # Professional/Office
    "Software Engineer", "Accountant", "Marketing Manager", "Sales Representative",
    "Administrative Assistant", "Project Manager", "Business Analyst", "HR Specialist",
    "Financial Analyst", "Graphic Designer", "Customer Service Representative",
    "Operations Manager", "Data Analyst", "Office Manager", "Executive Assistant",
    
    # Healthcare
    "Nurse", "Medical Assistant", "Physical Therapist", "Pharmacist",
    "Dental Hygienist", "Medical Technician", "Healthcare Administrator",
    
    # Education
    "Teacher", "School Administrator", "Professor", "Librarian", "Tutor",
    
    # Retail/Service
    "Store Manager", "Cashier", "Sales Associate", "Restaurant Manager",
    "Server", "Barista", "Security Guard", "Janitor", "Maintenance Worker",
    
    # Trades/Technical
    "Electrician", "Plumber", "Carpenter", "Mechanic", "Technician",
    "Construction Worker", "HVAC Technician", "Truck Driver",
    
    # Government/Public Service
    "Police Officer", "Firefighter", "Postal Worker", "Social Worker",
    "Government Clerk", "Park Ranger",
    
    # Other
    "Real Estate Agent", "Insurance Agent", "Bank Teller", "Chef",
    "Photographer", "Artist", "Writer", "Consultant"
]

# Email domains for realistic email generation
EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "hotmail.com", "aol.com", "msn.com"]

class CareerLevel(IntEnum):
    """Career levels from entry to executive."""
    CL_1 = 1  # Entry level / Assistant
    CL_2 = 2  # Associate / Junior
    CL_3 = 3  # Mid-level / Professional
    CL_4 = 4  # Senior / Specialist
    CL_5 = 5  # Lead / Manager
    CL_6 = 6  # Senior Manager / Director
    CL_7 = 7  # Vice President / Senior Director
    CL_8 = 8  # C-Suite / Executive


@dataclass
class CareerProfile:
    """Career profile containing level, title, and salary."""
    career_level: CareerLevel
    job_title: str
    annual_income: int

# Career level job titles by industry vertical
CAREER_TITLES = {
    # Technology
    "tech": {
        CareerLevel.CL_1: ["Software Engineer I", "Junior Developer", "QA Tester", "Technical Support Specialist"],
        CareerLevel.CL_2: ["Software Engineer II", "Frontend Developer", "Backend Developer", "Data Analyst"],
        CareerLevel.CL_3: ["Software Engineer III", "Full Stack Developer", "DevOps Engineer", "Product Analyst"],
        CareerLevel.CL_4: ["Senior Software Engineer", "Technical Lead", "Senior Data Scientist", "Security Engineer"],
        CareerLevel.CL_5: ["Engineering Manager", "Lead Developer", "Principal Engineer", "Team Lead"],
        CareerLevel.CL_6: ["Senior Engineering Manager", "Director of Engineering", "Principal Architect"],
        CareerLevel.CL_7: ["VP of Engineering", "Senior Director of Technology", "Chief Architect"],
        CareerLevel.CL_8: ["Chief Technology Officer", "VP of Product", "Chief Data Officer"]
    },
    
    # Business & Finance
    "business": {
        CareerLevel.CL_1: ["Business Analyst I", "Junior Consultant", "Financial Analyst I", "Administrative Assistant"],
        CareerLevel.CL_2: ["Business Analyst II", "Associate Consultant", "Financial Analyst II", "Coordinator"],
        CareerLevel.CL_3: ["Senior Business Analyst", "Consultant", "Senior Financial Analyst", "Project Manager"],
        CareerLevel.CL_4: ["Principal Business Analyst", "Senior Consultant", "Finance Manager", "Senior Project Manager"],
        CareerLevel.CL_5: ["Manager", "Lead Consultant", "Senior Finance Manager", "Program Manager"],
        CareerLevel.CL_6: ["Senior Manager", "Director of Operations", "Finance Director", "Senior Program Manager"],
        CareerLevel.CL_7: ["VP of Operations", "Senior Director", "VP of Finance", "Executive Director"],
        CareerLevel.CL_8: ["Chief Operating Officer", "Chief Financial Officer", "President", "Managing Director"]
    },
    
    # Sales & Marketing
    "sales_marketing": {
        CareerLevel.CL_1: ["Sales Associate", "Marketing Coordinator", "Inside Sales Rep", "Marketing Assistant"],
        CareerLevel.CL_2: ["Account Executive", "Marketing Specialist", "Sales Representative", "Digital Marketing Specialist"],
        CareerLevel.CL_3: ["Senior Account Executive", "Marketing Manager", "Territory Manager", "Product Marketing Manager"],
        CareerLevel.CL_4: ["Sales Manager", "Senior Marketing Manager", "Regional Sales Manager", "Brand Manager"],
        CareerLevel.CL_5: ["Senior Sales Manager", "Marketing Director", "Area Sales Director", "Channel Manager"],
        CareerLevel.CL_6: ["Sales Director", "Senior Marketing Director", "VP of Sales", "Director of Marketing"],
        CareerLevel.CL_7: ["VP of Sales", "VP of Marketing", "Chief Revenue Officer", "Senior VP Sales"],
        CareerLevel.CL_8: ["Chief Marketing Officer", "President of Sales", "Chief Revenue Officer", "Executive VP"]
    },
    
    # Healthcare
    "healthcare": {
        CareerLevel.CL_1: ["Medical Assistant", "Healthcare Aide", "Medical Receptionist", "Lab Technician"],
        CareerLevel.CL_2: ["Registered Nurse", "Physical Therapist", "Pharmacy Technician", "Medical Technologist"],
        CareerLevel.CL_3: ["Senior Nurse", "Nurse Practitioner", "Clinical Specialist", "Healthcare Coordinator"],
        CareerLevel.CL_4: ["Charge Nurse", "Senior Therapist", "Clinical Manager", "Department Supervisor"],
        CareerLevel.CL_5: ["Nursing Manager", "Clinical Director", "Department Manager", "Program Manager"],
        CareerLevel.CL_6: ["Director of Nursing", "Medical Director", "Senior Clinical Director", "VP of Patient Care"],
        CareerLevel.CL_7: ["VP of Clinical Operations", "Chief Medical Officer", "Senior VP Healthcare"],
        CareerLevel.CL_8: ["Chief Executive Officer", "President", "Chief Operating Officer", "System CEO"]
    },
    
    # Education
    "education": {
        CareerLevel.CL_1: ["Teaching Assistant", "Substitute Teacher", "Tutor", "Education Aide"],
        CareerLevel.CL_2: ["Teacher", "Instructor", "Counselor", "Librarian"],
        CareerLevel.CL_3: ["Senior Teacher", "Department Chair", "Curriculum Specialist", "Academic Advisor"],
        CareerLevel.CL_4: ["Lead Teacher", "Assistant Principal", "Instructional Coordinator", "Program Director"],
        CareerLevel.CL_5: ["Principal", "Department Head", "Academic Director", "District Coordinator"],
        CareerLevel.CL_6: ["Senior Principal", "Assistant Superintendent", "Director of Education", "Dean"],
        CareerLevel.CL_7: ["Superintendent", "VP of Academic Affairs", "Provost", "Associate Dean"],
        CareerLevel.CL_8: ["President", "Chancellor", "Chief Academic Officer", "Executive Director"]
    },
    
    # General/Services
    "general": {
        CareerLevel.CL_1: ["Customer Service Rep", "Administrative Assistant", "Clerk", "Support Specialist"],
        CareerLevel.CL_2: ["Customer Success Specialist", "Administrative Coordinator", "Specialist", "Associate"],
        CareerLevel.CL_3: ["Team Lead", "Operations Specialist", "Program Coordinator", "Senior Associate"],
        CareerLevel.CL_4: ["Supervisor", "Operations Manager", "Senior Specialist", "Team Manager"],
        CareerLevel.CL_5: ["Manager", "Operations Director", "Department Manager", "Program Manager"],
        CareerLevel.CL_6: ["Senior Manager", "Director", "Regional Manager", "Senior Director"],
        CareerLevel.CL_7: ["Vice President", "Executive Director", "Regional VP", "Senior VP"],
        CareerLevel.CL_8: ["President", "Chief Executive Officer", "Chief Operating Officer", "Managing Director"]
    }
}

# Base salary ranges by career level (2025 US market)
SALARY_RANGES = {
    CareerLevel.CL_1: (35000, 55000),    # Entry level
    CareerLevel.CL_2: (45000, 70000),    # Associate
    CareerLevel.CL_3: (60000, 90000),    # Mid-level
    CareerLevel.CL_4: (80000, 120000),   # Senior
    CareerLevel.CL_5: (100000, 150000),  # Lead/Manager
    CareerLevel.CL_6: (130000, 200000),  # Director
    CareerLevel.CL_7: (180000, 300000),  # VP
    CareerLevel.CL_8: (250000, 500000),  # C-Suite
}

# Industry salary multipliers
INDUSTRY_MULTIPLIERS = {
    "tech": 1.3,           # Tech pays premium
    "business": 1.1,       # Finance/consulting premium
    "sales_marketing": 1.0, # Average market
    "healthcare": 1.1,     # Healthcare premium
    "education": 0.8,      # Education typically lower
    "general": 0.9,        # General/services below average
}
