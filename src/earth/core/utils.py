from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional, cast
from datetime import datetime, date, timezone
from enum import IntEnum, Enum
import uuid
import random

DEFAULT_RANDOM_STATE: int = 8172025
MIN_AGE: int = 18
MAX_AGE: int = 85
MIN_RATIO_PEOPLE_TO_COMPANIES: float = 1.0
MAX_RATIO_PEOPLE_TO_COMPANIES: float = 100.0
COUNTER: int = 0


def get_reproducible_uuid(
    seed: Optional[int] = DEFAULT_RANDOM_STATE,
) -> str:
    global COUNTER
    seeded_random_generator = random.Random()
    seeded_random_generator.seed(cast(int, seed) + COUNTER)
    COUNTER += 1
    reproducible_uuid_int = seeded_random_generator.getrandbits(128)
    seeded_uuid = uuid.UUID(int=reproducible_uuid_int)
    return seeded_uuid.hex


# Common US job titles by category
US_JOB_TITLES = [
    # Professional/Office
    "Software Engineer",
    "Accountant",
    "Marketing Manager",
    "Sales Representative",
    "Administrative Assistant",
    "Project Manager",
    "Business Analyst",
    "HR Specialist",
    "Financial Analyst",
    "Graphic Designer",
    "Customer Service Representative",
    "Operations Manager",
    "Data Analyst",
    "Office Manager",
    "Executive Assistant",
    # Healthcare
    "Nurse",
    "Medical Assistant",
    "Physical Therapist",
    "Pharmacist",
    "Dental Hygienist",
    "Medical Technician",
    "Healthcare Administrator",
    # Education
    "Teacher",
    "School Administrator",
    "Professor",
    "Librarian",
    "Tutor",
    # Retail/Service
    "Store Manager",
    "Cashier",
    "Sales Associate",
    "Restaurant Manager",
    "Server",
    "Barista",
    "Security Guard",
    "Janitor",
    "Maintenance Worker",
    # Trades/Technical
    "Electrician",
    "Plumber",
    "Carpenter",
    "Mechanic",
    "Technician",
    "Construction Worker",
    "HVAC Technician",
    "Truck Driver",
    # Government/Public Service
    "Police Officer",
    "Firefighter",
    "Postal Worker",
    "Social Worker",
    "Government Clerk",
    "Park Ranger",
    # Other
    "Real Estate Agent",
    "Insurance Agent",
    "Bank Teller",
    "Chef",
    "Photographer",
    "Artist",
    "Writer",
    "Consultant",
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


@dataclass
class PersonProfile:
    """Data class representing a person profile."""

    person_id: str
    first_name: str
    last_name: str
    full_name: str
    gender: str
    date_of_birth: date
    age: int
    email: str
    phone_number: str
    ssn: str

    # Address information
    street_address: str
    city: str
    state: str
    zip_code: str

    # Professional information (updated to use career helper)
    job_title: str
    career_level: str  # CL-1 through CL-8 equivalent
    employment_status: str
    annual_income: int

    # Digital footprint
    username: str
    ipv4_address: str
    user_agent: str

    # Personal details
    blood_type: str
    height_cm: int
    weight_kg: int
    marital_status: str
    education_level: str
    country: str = "United States"
    country_code: str = "US"

    # Metadata
    created_at: datetime = datetime.now(timezone.utc)
    created_by: str = "earth_generator"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


# Career level job titles by industry vertical
CAREER_TITLES = {
    "technology": {
        CareerLevel.CL_1: [
            "Software Engineer I",
            "Junior Developer",
            "QA Tester",
            "Technical Support Specialist",
        ],
        CareerLevel.CL_2: [
            "Software Engineer II",
            "Frontend Developer",
            "Backend Developer",
            "Data Analyst",
        ],
        CareerLevel.CL_3: [
            "Software Engineer III",
            "Full Stack Developer",
            "DevOps Engineer",
            "Product Analyst",
        ],
        CareerLevel.CL_4: [
            "Senior Software Engineer",
            "Technical Lead",
            "Senior Data Scientist",
            "Security Engineer",
        ],
        CareerLevel.CL_5: [
            "Engineering Manager",
            "Lead Developer",
            "Principal Engineer",
            "Team Lead",
        ],
        CareerLevel.CL_6: [
            "Senior Engineering Manager",
            "Director of Engineering",
            "Principal Architect",
        ],
        CareerLevel.CL_7: [
            "VP of Engineering",
            "Senior Director of Technology",
            "Chief Architect",
        ],
        CareerLevel.CL_8: [
            "Chief Technology Officer",
            "VP of Product",
            "Chief Data Officer",
        ],
    },
    "financial_services": {
        CareerLevel.CL_1: [
            "Financial Analyst I",
            "Banking Associate",
            "Investment Associate",
            "Credit Analyst",
        ],
        CareerLevel.CL_2: [
            "Financial Analyst II",
            "Investment Advisor",
            "Senior Banking Associate",
            "Portfolio Analyst",
        ],
        CareerLevel.CL_3: [
            "Senior Financial Analyst",
            "Investment Consultant",
            "Relationship Manager",
            "Risk Analyst",
        ],
        CareerLevel.CL_4: [
            "Finance Manager",
            "Senior Investment Advisor",
            "Portfolio Manager",
            "Branch Manager",
        ],
        CareerLevel.CL_5: [
            "Senior Finance Manager",
            "Investment Director",
            "Regional Manager",
            "Risk Manager",
        ],
        CareerLevel.CL_6: [
            "Finance Director",
            "VP of Investments",
            "Managing Director",
            "Chief Risk Officer",
        ],
        CareerLevel.CL_7: [
            "VP of Finance",
            "Senior Managing Director",
            "Regional President",
            "Chief Investment Officer",
        ],
        CareerLevel.CL_8: [
            "Chief Financial Officer",
            "President",
            "Chief Executive Officer",
            "Chairman",
        ],
    },
    "pharmaceuticals": {
        CareerLevel.CL_1: [
            "Research Associate",
            "Lab Technician",
            "Quality Control Analyst",
            "Clinical Research Coordinator",
        ],
        CareerLevel.CL_2: [
            "Research Scientist",
            "Clinical Research Associate",
            "Regulatory Affairs Specialist",
            "Biostatistician",
        ],
        CareerLevel.CL_3: [
            "Senior Research Scientist",
            "Principal Scientist",
            "Clinical Trial Manager",
            "Regulatory Affairs Manager",
        ],
        CareerLevel.CL_4: [
            "Lead Scientist",
            "Senior Clinical Manager",
            "Medical Affairs Manager",
            "Product Manager",
        ],
        CareerLevel.CL_5: [
            "Research Director",
            "Clinical Development Director",
            "Medical Director",
            "Senior Product Manager",
        ],
        CareerLevel.CL_6: [
            "VP of Research",
            "VP of Clinical Development",
            "Chief Medical Officer",
            "VP of Regulatory Affairs",
        ],
        CareerLevel.CL_7: [
            "Senior VP of R&D",
            "Chief Scientific Officer",
            "Executive Medical Director",
            "Global Head of Development",
        ],
        CareerLevel.CL_8: [
            "Chief Executive Officer",
            "President",
            "Chief Operating Officer",
            "Chairman & CEO",
        ],
    },
    "aerospace": {
        CareerLevel.CL_1: [
            "Aerospace Engineer I",
            "Design Engineer",
            "Test Technician",
            "Quality Inspector",
        ],
        CareerLevel.CL_2: [
            "Aerospace Engineer II",
            "Systems Engineer",
            "Test Engineer",
            "Project Engineer",
        ],
        CareerLevel.CL_3: [
            "Senior Aerospace Engineer",
            "Lead Engineer",
            "Systems Architect",
            "Program Engineer",
        ],
        CareerLevel.CL_4: [
            "Principal Engineer",
            "Engineering Manager",
            "Technical Lead",
            "Chief Engineer",
        ],
        CareerLevel.CL_5: [
            "Senior Engineering Manager",
            "Program Manager",
            "Director of Engineering",
            "Technical Director",
        ],
        CareerLevel.CL_6: [
            "VP of Engineering",
            "Senior Program Director",
            "Chief Engineer",
            "Director of Operations",
        ],
        CareerLevel.CL_7: [
            "Senior VP of Engineering",
            "Chief Technology Officer",
            "Executive Director",
            "Division President",
        ],
        CareerLevel.CL_8: [
            "Chief Executive Officer",
            "President",
            "Chief Operating Officer",
            "Chairman",
        ],
    },
    "energy": {
        CareerLevel.CL_1: [
            "Field Technician",
            "Junior Engineer",
            "Operations Technician",
            "Safety Coordinator",
        ],
        CareerLevel.CL_2: [
            "Energy Analyst",
            "Project Engineer",
            "Operations Specialist",
            "Environmental Specialist",
        ],
        CareerLevel.CL_3: [
            "Senior Energy Analyst",
            "Project Manager",
            "Operations Manager",
            "Environmental Manager",
        ],
        CareerLevel.CL_4: [
            "Principal Engineer",
            "Senior Project Manager",
            "Plant Manager",
            "Regional Manager",
        ],
        CareerLevel.CL_5: [
            "Engineering Manager",
            "Operations Director",
            "Business Development Manager",
            "Division Manager",
        ],
        CareerLevel.CL_6: [
            "VP of Operations",
            "Regional Director",
            "Asset Manager",
            "VP of Development",
        ],
        CareerLevel.CL_7: [
            "Senior VP of Operations",
            "Chief Operating Officer",
            "Executive VP",
            "Division President",
        ],
        CareerLevel.CL_8: [
            "Chief Executive Officer",
            "President",
            "Chairman & CEO",
            "Chief Operating Officer",
        ],
    },
    "telecommunications": {
        CareerLevel.CL_1: [
            "Network Technician",
            "Customer Service Rep",
            "Field Service Technician",
            "NOC Analyst",
        ],
        CareerLevel.CL_2: [
            "Network Engineer",
            "Systems Administrator",
            "Technical Support Specialist",
            "Network Analyst",
        ],
        CareerLevel.CL_3: [
            "Senior Network Engineer",
            "Solutions Architect",
            "Project Manager",
            "Product Manager",
        ],
        CareerLevel.CL_4: [
            "Principal Network Engineer",
            "Engineering Manager",
            "Senior Product Manager",
            "Operations Manager",
        ],
        CareerLevel.CL_5: [
            "Network Architecture Manager",
            "Director of Engineering",
            "VP of Product",
            "Regional Manager",
        ],
        CareerLevel.CL_6: [
            "VP of Engineering",
            "Chief Technology Officer",
            "VP of Operations",
            "Director of Strategy",
        ],
        CareerLevel.CL_7: [
            "Senior VP of Technology",
            "Chief Operating Officer",
            "Executive VP",
            "President of Operations",
        ],
        CareerLevel.CL_8: [
            "Chief Executive Officer",
            "President",
            "Chairman & CEO",
            "Chief Technology Officer",
        ],
    },
    "media": {
        CareerLevel.CL_1: [
            "Content Creator",
            "Production Assistant",
            "Junior Writer",
            "Media Coordinator",
        ],
        CareerLevel.CL_2: [
            "Content Producer",
            "Editor",
            "Writer",
            "Digital Media Specialist",
        ],
        CareerLevel.CL_3: [
            "Senior Producer",
            "Creative Director",
            "Senior Editor",
            "Content Manager",
        ],
        CareerLevel.CL_4: [
            "Executive Producer",
            "Creative Manager",
            "Editorial Director",
            "Brand Manager",
        ],
        CareerLevel.CL_5: [
            "Head of Content",
            "Creative Director",
            "VP of Programming",
            "Managing Editor",
        ],
        CareerLevel.CL_6: [
            "VP of Content",
            "Chief Creative Officer",
            "Editorial Director",
            "VP of Production",
        ],
        CareerLevel.CL_7: [
            "Senior VP of Content",
            "Chief Content Officer",
            "President of Programming",
            "Executive VP",
        ],
        CareerLevel.CL_8: [
            "Chief Executive Officer",
            "President",
            "Chairman & CEO",
            "Chief Operating Officer",
        ],
    },
    "real_estate": {
        CareerLevel.CL_1: [
            "Real Estate Agent",
            "Property Assistant",
            "Leasing Consultant",
            "Real Estate Analyst",
        ],
        CareerLevel.CL_2: [
            "Senior Real Estate Agent",
            "Property Manager",
            "Investment Analyst",
            "Development Coordinator",
        ],
        CareerLevel.CL_3: [
            "Real Estate Broker",
            "Senior Property Manager",
            "Asset Manager",
            "Development Manager",
        ],
        CareerLevel.CL_4: [
            "Senior Broker",
            "Portfolio Manager",
            "Regional Manager",
            "Project Manager",
        ],
        CareerLevel.CL_5: [
            "Brokerage Manager",
            "VP of Property Management",
            "Development Director",
            "Regional Director",
        ],
        CareerLevel.CL_6: [
            "VP of Real Estate",
            "Managing Director",
            "Chief Investment Officer",
            "President of Development",
        ],
        CareerLevel.CL_7: [
            "Senior VP of Real Estate",
            "Chief Operating Officer",
            "Executive VP",
            "Division President",
        ],
        CareerLevel.CL_8: [
            "Chief Executive Officer",
            "President",
            "Chairman & CEO",
            "Founder & CEO",
        ],
    },
    "healthcare": {
        CareerLevel.CL_1: [
            "Medical Assistant",
            "Healthcare Aide",
            "Medical Receptionist",
            "Lab Technician",
        ],
        CareerLevel.CL_2: [
            "Registered Nurse",
            "Physical Therapist",
            "Pharmacy Technician",
            "Medical Technologist",
        ],
        CareerLevel.CL_3: [
            "Senior Nurse",
            "Nurse Practitioner",
            "Clinical Specialist",
            "Healthcare Coordinator",
        ],
        CareerLevel.CL_4: [
            "Charge Nurse",
            "Senior Therapist",
            "Clinical Manager",
            "Department Supervisor",
        ],
        CareerLevel.CL_5: [
            "Nursing Manager",
            "Clinical Director",
            "Department Manager",
            "Program Manager",
        ],
        CareerLevel.CL_6: [
            "Director of Nursing",
            "Medical Director",
            "Senior Clinical Director",
            "VP of Patient Care",
        ],
        CareerLevel.CL_7: [
            "VP of Clinical Operations",
            "Chief Medical Officer",
            "Senior VP Healthcare",
        ],
        CareerLevel.CL_8: [
            "Chief Executive Officer",
            "President",
            "Chief Operating Officer",
            "System CEO",
        ],
    },
    "professional_services": {
        CareerLevel.CL_1: [
            "Junior Consultant",
            "Associate",
            "Analyst",
            "Staff Accountant",
        ],
        CareerLevel.CL_2: [
            "Consultant",
            "Senior Associate",
            "Senior Analyst",
            "Accountant",
        ],
        CareerLevel.CL_3: [
            "Senior Consultant",
            "Manager",
            "Principal Analyst",
            "Senior Manager",
        ],
        CareerLevel.CL_4: [
            "Principal Consultant",
            "Senior Manager",
            "Director",
            "Partner Track",
        ],
        CareerLevel.CL_5: [
            "Director",
            "Principal",
            "Managing Director",
            "Senior Director",
        ],
        CareerLevel.CL_6: [
            "Senior Director",
            "Partner",
            "VP of Consulting",
            "Managing Partner",
        ],
        CareerLevel.CL_7: [
            "Senior Partner",
            "Executive Director",
            "Regional Managing Partner",
            "Practice Leader",
        ],
        CareerLevel.CL_8: [
            "Managing Partner",
            "CEO",
            "Chairman",
            "Global Managing Partner",
        ],
    },
    "automotive": {
        CareerLevel.CL_1: [
            "Automotive Technician",
            "Assembly Worker",
            "Quality Inspector",
            "Junior Engineer",
        ],
        CareerLevel.CL_2: [
            "Senior Technician",
            "Process Engineer",
            "Quality Engineer",
            "Design Engineer",
        ],
        CareerLevel.CL_3: [
            "Lead Technician",
            "Senior Engineer",
            "Manufacturing Engineer",
            "Product Engineer",
        ],
        CareerLevel.CL_4: [
            "Engineering Manager",
            "Plant Supervisor",
            "Senior Product Engineer",
            "Quality Manager",
        ],
        CareerLevel.CL_5: [
            "Plant Manager",
            "Engineering Director",
            "Operations Manager",
            "Regional Manager",
        ],
        CareerLevel.CL_6: [
            "VP of Manufacturing",
            "VP of Engineering",
            "Operations Director",
            "General Manager",
        ],
        CareerLevel.CL_7: [
            "Senior VP of Operations",
            "Chief Operating Officer",
            "Division President",
            "Executive VP",
        ],
        CareerLevel.CL_8: [
            "Chief Executive Officer",
            "President",
            "Chairman & CEO",
            "Chief Operating Officer",
        ],
    },
    "general": {
        CareerLevel.CL_1: [
            "Customer Service Rep",
            "Administrative Assistant",
            "Clerk",
            "Support Specialist",
        ],
        CareerLevel.CL_2: [
            "Customer Success Specialist",
            "Administrative Coordinator",
            "Specialist",
            "Associate",
        ],
        CareerLevel.CL_3: [
            "Team Lead",
            "Operations Specialist",
            "Program Coordinator",
            "Senior Associate",
        ],
        CareerLevel.CL_4: [
            "Supervisor",
            "Operations Manager",
            "Senior Specialist",
            "Team Manager",
        ],
        CareerLevel.CL_5: [
            "Manager",
            "Operations Director",
            "Department Manager",
            "Program Manager",
        ],
        CareerLevel.CL_6: [
            "Senior Manager",
            "Director",
            "Regional Manager",
            "Senior Director",
        ],
        CareerLevel.CL_7: [
            "Vice President",
            "Executive Director",
            "Regional VP",
            "Senior VP",
        ],
        CareerLevel.CL_8: [
            "President",
            "Chief Executive Officer",
            "Chief Operating Officer",
            "Managing Director",
        ],
    },
    "government": {
        CareerLevel.CL_1: [
            "Administrative Assistant",
            "Program Assistant",
            "Clerk",
            "Customer Service Rep",
        ],
        CareerLevel.CL_2: [
            "Program Analyst",
            "Administrative Specialist",
            "Policy Analyst",
            "Public Affairs Specialist",
        ],
        CareerLevel.CL_3: [
            "Senior Program Analyst",
            "Program Manager",
            "Senior Policy Analyst",
            "Public Information Officer",
        ],
        CareerLevel.CL_4: [
            "Program Director",
            "Deputy Director",
            "Division Chief",
            "Senior Manager",
        ],
        CareerLevel.CL_5: [
            "Department Director",
            "Assistant Administrator",
            "Regional Director",
            "Bureau Chief",
        ],
        CareerLevel.CL_6: [
            "Deputy Administrator",
            "Assistant Secretary",
            "Executive Director",
            "Commissioner",
        ],
        CareerLevel.CL_7: [
            "Administrator",
            "Deputy Secretary",
            "Agency Director",
            "Deputy Commissioner",
        ],
        CareerLevel.CL_8: [
            "Secretary",
            "Director",
            "Administrator",
            "Commissioner",
        ],
    },
    "manufacturing": {
        CareerLevel.CL_1: [
            "Production Worker",
            "Assembly Technician",
            "Quality Inspector",
            "Machine Operator",
        ],
        CareerLevel.CL_2: [
            "Senior Production Worker",
            "Process Technician",
            "Quality Analyst",
            "Maintenance Technician",
        ],
        CareerLevel.CL_3: [
            "Team Lead",
            "Process Engineer",
            "Quality Engineer",
            "Shift Supervisor",
        ],
        CareerLevel.CL_4: [
            "Production Supervisor",
            "Manufacturing Engineer",
            "Quality Manager",
            "Plant Supervisor",
        ],
        CareerLevel.CL_5: [
            "Production Manager",
            "Operations Manager",
            "Plant Manager",
            "Engineering Manager",
        ],
        CareerLevel.CL_6: [
            "VP of Operations",
            "VP of Manufacturing",
            "General Manager",
            "Operations Director",
        ],
        CareerLevel.CL_7: [
            "Senior VP of Operations",
            "Chief Operations Officer",
            "Division President",
            "Executive VP",
        ],
        CareerLevel.CL_8: [
            "Chief Executive Officer",
            "President",
            "Chairman & CEO",
            "Chief Operating Officer",
        ],
    },
    "construction": {
        CareerLevel.CL_1: [
            "Construction Worker",
            "Apprentice",
            "Helper",
            "Laborer",
        ],
        CareerLevel.CL_2: [
            "Skilled Tradesperson",
            "Equipment Operator",
            "Carpenter",
            "Electrician",
        ],
        CareerLevel.CL_3: [
            "Crew Leader",
            "Site Supervisor",
            "Project Coordinator",
            "Estimator",
        ],
        CareerLevel.CL_4: [
            "Project Manager",
            "Construction Manager",
            "Site Manager",
            "Senior Estimator",
        ],
        CareerLevel.CL_5: [
            "Senior Project Manager",
            "Operations Manager",
            "Regional Manager",
            "Business Development Manager",
        ],
        CareerLevel.CL_6: [
            "VP of Operations",
            "Regional Director",
            "General Manager",
            "VP of Construction",
        ],
        CareerLevel.CL_7: [
            "Senior VP of Operations",
            "Executive VP",
            "Division President",
            "Chief Operating Officer",
        ],
        CareerLevel.CL_8: [
            "Chief Executive Officer",
            "President",
            "Chairman & CEO",
            "Owner",
        ],
    },
    "transportation": {
        CareerLevel.CL_1: [
            "Driver",
            "Warehouse Worker",
            "Dispatcher",
            "Logistics Coordinator",
        ],
        CareerLevel.CL_2: [
            "Senior Driver",
            "Logistics Specialist",
            "Fleet Coordinator",
            "Operations Specialist",
        ],
        CareerLevel.CL_3: [
            "Fleet Manager",
            "Operations Supervisor",
            "Logistics Manager",
            "Terminal Manager",
        ],
        CareerLevel.CL_4: [
            "Operations Manager",
            "Regional Manager",
            "Transportation Manager",
            "District Manager",
        ],
        CareerLevel.CL_5: [
            "VP of Operations",
            "Regional Director",
            "General Manager",
            "Director of Logistics",
        ],
        CareerLevel.CL_6: [
            "Senior VP of Operations",
            "Chief Operations Officer",
            "VP of Transportation",
            "Executive Director",
        ],
        CareerLevel.CL_7: [
            "Executive VP",
            "Division President",
            "Chief Operating Officer",
            "Senior VP",
        ],
        CareerLevel.CL_8: [
            "Chief Executive Officer",
            "President",
            "Chairman & CEO",
            "Chief Operating Officer",
        ],
    },
    "education": {
        CareerLevel.CL_1: [
            "Teaching Assistant",
            "Substitute Teacher",
            "Tutor",
            "Education Aide",
        ],
        CareerLevel.CL_2: ["Teacher", "Instructor", "Counselor", "Librarian"],
        CareerLevel.CL_3: [
            "Senior Teacher",
            "Department Chair",
            "Curriculum Specialist",
            "Academic Advisor",
        ],
        CareerLevel.CL_4: [
            "Lead Teacher",
            "Assistant Principal",
            "Instructional Coordinator",
            "Program Director",
        ],
        CareerLevel.CL_5: [
            "Principal",
            "Department Head",
            "Academic Director",
            "District Coordinator",
        ],
        CareerLevel.CL_6: [
            "Senior Principal",
            "Assistant Superintendent",
            "Director of Education",
            "Dean",
        ],
        CareerLevel.CL_7: [
            "Superintendent",
            "VP of Academic Affairs",
            "Provost",
            "Associate Dean",
        ],
        CareerLevel.CL_8: [
            "President",
            "Chancellor",
            "Chief Academic Officer",
            "Executive Director",
        ],
    },
    "retail": {
        CareerLevel.CL_1: [
            "Sales Associate",
            "Cashier",
            "Stock Associate",
            "Customer Service Rep",
        ],
        CareerLevel.CL_2: [
            "Senior Sales Associate",
            "Department Associate",
            "Shift Lead",
            "Sales Specialist",
        ],
        CareerLevel.CL_3: [
            "Team Lead",
            "Department Supervisor",
            "Assistant Manager",
            "Merchandiser",
        ],
        CareerLevel.CL_4: [
            "Store Manager",
            "Department Manager",
            "Regional Supervisor",
            "Buyer",
        ],
        CareerLevel.CL_5: [
            "District Manager",
            "Regional Manager",
            "Merchandising Manager",
            "Operations Manager",
        ],
        CareerLevel.CL_6: [
            "Regional Director",
            "VP of Operations",
            "VP of Merchandising",
            "General Manager",
        ],
        CareerLevel.CL_7: [
            "Senior VP of Retail",
            "Chief Merchandising Officer",
            "Executive VP",
            "Division President",
        ],
        CareerLevel.CL_8: [
            "Chief Executive Officer",
            "President",
            "Chairman & CEO",
            "Chief Operating Officer",
        ],
    },
    "hospitality": {
        CareerLevel.CL_1: [
            "Front Desk Associate",
            "Server",
            "Housekeeper",
            "Host/Hostess",
        ],
        CareerLevel.CL_2: [
            "Guest Services Coordinator",
            "Bartender",
            "Concierge",
            "Kitchen Staff",
        ],
        CareerLevel.CL_3: [
            "Shift Manager",
            "Assistant Manager",
            "Supervisor",
            "Event Coordinator",
        ],
        CareerLevel.CL_4: [
            "Hotel Manager",
            "Restaurant Manager",
            "Department Manager",
            "Food & Beverage Manager",
        ],
        CareerLevel.CL_5: [
            "General Manager",
            "Operations Manager",
            "Regional Manager",
            "Director of Operations",
        ],
        CareerLevel.CL_6: [
            "VP of Operations",
            "Regional Director",
            "Area Manager",
            "VP of Hospitality",
        ],
        CareerLevel.CL_7: [
            "Senior VP of Operations",
            "Division President",
            "Executive VP",
            "Chief Operating Officer",
        ],
        CareerLevel.CL_8: [
            "Chief Executive Officer",
            "President",
            "Chairman & CEO",
            "Owner",
        ],
    },
    "agriculture": {
        CareerLevel.CL_1: [
            "Farm Worker",
            "Ranch Hand",
            "Agricultural Technician",
            "Equipment Operator",
        ],
        CareerLevel.CL_2: [
            "Farm Supervisor",
            "Agricultural Specialist",
            "Crop Manager",
            "Livestock Manager",
        ],
        CareerLevel.CL_3: [
            "Farm Manager",
            "Agricultural Consultant",
            "Operations Supervisor",
            "Regional Coordinator",
        ],
        CareerLevel.CL_4: [
            "Regional Manager",
            "Operations Manager",
            "Agricultural Director",
            "Farm Owner",
        ],
        CareerLevel.CL_5: [
            "VP of Operations",
            "Agricultural Operations Director",
            "Regional Director",
            "General Manager",
        ],
        CareerLevel.CL_6: [
            "Senior VP of Agriculture",
            "Chief Agricultural Officer",
            "Executive Director",
            "Division President",
        ],
        CareerLevel.CL_7: [
            "Executive VP",
            "President of Agriculture",
            "Chief Operating Officer",
            "Senior VP",
        ],
        CareerLevel.CL_8: [
            "Chief Executive Officer",
            "President",
            "Chairman & CEO",
            "Owner & CEO",
        ],
    },
    "non_profit": {
        CareerLevel.CL_1: [
            "Program Assistant",
            "Volunteer Coordinator",
            "Administrative Assistant",
            "Outreach Coordinator",
        ],
        CareerLevel.CL_2: [
            "Program Coordinator",
            "Development Associate",
            "Case Manager",
            "Community Outreach Specialist",
        ],
        CareerLevel.CL_3: [
            "Program Manager",
            "Development Manager",
            "Senior Case Manager",
            "Community Relations Manager",
        ],
        CareerLevel.CL_4: [
            "Program Director",
            "Development Director",
            "Operations Manager",
            "Senior Program Manager",
        ],
        CareerLevel.CL_5: [
            "VP of Programs",
            "VP of Development",
            "Operations Director",
            "Regional Director",
        ],
        CareerLevel.CL_6: [
            "Senior VP of Programs",
            "Chief Development Officer",
            "Chief Operating Officer",
            "Executive Director",
        ],
        CareerLevel.CL_7: [
            "Executive VP",
            "Deputy Executive Director",
            "Chief Program Officer",
            "President",
        ],
        CareerLevel.CL_8: [
            "Chief Executive Officer",
            "Executive Director",
            "President & CEO",
            "Founder & CEO",
        ],
    },
}

# Base salary ranges by career level (2025 US market)
SALARY_RANGES = {
    CareerLevel.CL_1: (35000, 55000),  # Entry level
    CareerLevel.CL_2: (45000, 70000),  # Associate
    CareerLevel.CL_3: (60000, 90000),  # Mid-level
    CareerLevel.CL_4: (80000, 120000),  # Senior
    CareerLevel.CL_5: (100000, 150000),  # Lead/Manager
    CareerLevel.CL_6: (130000, 200000),  # Director
    CareerLevel.CL_7: (180000, 300000),  # VP
    CareerLevel.CL_8: (250000, 500000),  # C-Suite
}


class IndustryMetadata(Enum):
    """Industries and associated profitability multipliers"""

    # High profitability industries
    technology = 1.4
    financial_services = 1.3
    pharmaceuticals = 1.3
    aerospace = 1.3

    # Medium-high profitability
    energy = 1.2
    telecommunications = 1.1
    media = 1.1
    real_estate = 1.0
    healthcare = 1.0

    # Medium profitability
    professional_services = 0.9
    automotive = 0.9
    general = 0.9
    government = 0.9

    # Medium-low profitability
    manufacturing = 0.8
    construction = 0.8
    transportation = 0.8
    education = 0.8

    # Lower profitability
    retail = 0.7
    hospitality = 0.6
    agriculture = 0.5

    # Lowest profitability
    non_profit = 0.3

    @classmethod
    def _get_title_case_industry_names(cls) -> List[str]:
        return [member.name.replace("_", " ").title() for member in cls]

    # Helper function to get career titles for any industry
    @classmethod
    def _get_career_titles_for_industry(
        cls, industry_name: str, career_level: CareerLevel
    ) -> List[str]:
        """
        Get career titles for a specific industry and level.

        Args:
            industry_name: Industry name (can be title case or enum format)
            career_level: CareerLevel enum value

        Returns:
            List of job titles for that industry/level combination
        """
        # Convert title case to enum format if needed
        industry_key = industry_name.lower().replace(" ", "_")

        # Try exact match first
        if industry_key in CAREER_TITLES:
            return CAREER_TITLES[industry_key][career_level]

        # Fallback to general if industry not found
        print(f"Warning: Industry '{industry_name}' not found, using general titles")
        return CAREER_TITLES["general"][career_level]


EMPLOYMENT_STATUSES = [
    "Full-time",
    "Part-time",
    "Contract",
    "Freelance",
    "Unemployed",
    "Student",
    "Retired",
    "Self-employed",
]

EDUCATION_LEVELS = [
    "High School",
    "Some College",
    "Associate Degree",
    "Bachelor's Degree",
    "Master's Degree",
    "Doctoral Degree",
]

MARITAL_STATUSES = [
    "Single",
    "Married",
    "Divorced",
    "Widowed",
    "Separated",
]

COMPANY_SIZE_CATEGORIES = {
    "Startup": (1, 10),
    "Small": (11, 50),
    "Medium": (51, 250),
    "Large": (251, 1000),
    "Enterprise": (1001, 10000),
    "Mega Corp": (10001, 500000),
}

BUSINESS_TYPES = [
    "Corporation",
    "LLC",
    "Partnership",
    "Sole Proprietorship",
    "S Corporation",
    "B Corporation",
    "Non-Profit",
    "Cooperative",
]
LEGAL_SUFFIXES = ["Inc.", "LLC", "Corp.", "Ltd.", "Co.", "LP"]

REVENUE_RANGES = {
    "Startup": ("$0-1M", (0, 1000000)),
    "Small": ("$1M-10M", (1000000, 10000000)),
    "Medium": ("$10M-100M", (10000000, 100000000)),
    "Large": ("$100M-1B", (100000000, 1000000000)),
    "Enterprise": ("$1B-10B", (1000000000, 10000000000)),
    "Mega Corp": ("$10B+", (10000000000, 500000000000)),
}

CREDIT_RATINGS = [
    "AAA",
    "AA+",
    "AA",
    "AA-",
    "A+",
    "A",
    "A-",
    "BBB+",
    "BBB",
    "BBB-",
    "BB+",
    "BB",
    "BB-",
    "B+",
    "B",
    "B-",
    "CCC",
    "CC",
    "C",
    "D",
]

GROWTH_STAGES = ["Startup", "Growth", "Mature", "Decline"]
