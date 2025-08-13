"""
Person profile generator using Faker library with maximal use of faker.profile().
"""

from datetime import datetime, date, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from faker import Faker
import uuid
import random
import numpy as np
from utils import MIN_AGE, MAX_AGE


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
    country: str
    country_code: str
    
    # Professional information
    job_title: str
    company: str
    employment_status: str
    annual_income: int
    
    # Digital footprint
    username: str
    website: str
    ipv4_address: str
    user_agent: str
    
    # Personal details
    blood_type: str
    height_cm: int
    weight_kg: int
    marital_status: str
    education_level: str

    # Metadata 
    MIN_AGE: int = MIN_AGE
    MAX_AGE: int = MAX_AGE 
    created_at: datetime = datetime.now(timezone.utc)
    created_by: str = "earth_generator"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class PersonGenerator:
    """Generator class for creating realistic person profiles."""
    
    def __init__(self, locale: str = "en_US", seed: Optional[int] = None):
        """
        Initialize the generator.
        
        Args:
            locale: Faker locale for generated data
            seed: Random seed for reproducible results
        """
        self.fake = Faker(locale)
        if seed:
            Faker.seed(seed)
            random.seed(seed)
        
        # Employment status options
        self.employment_statuses = [
            "Full-time", "Part-time", "Contract", "Freelance", 
            "Unemployed", "Student", "Retired", "Self-employed"
        ]
        
        # Education levels
        self.education_levels = [
            "High School", "Some College", "Associate Degree",
            "Bachelor's Degree", "Master's Degree", "Doctoral Degree"
        ]
        
        # Marital statuses
        self.marital_statuses = [
            "Single", "Married", "Divorced", "Widowed", "Separated"
        ]
    
    def _calculate_age(self, birth_date: date) -> int:
        """Calculate age from birth date."""
        today = date.today()
        return today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
        )
    
    def _generate_income_by_age_education(self, age: int, education: str, employment_status: str) -> int:
        """Generate realistic income based on age, education, and employment status."""
        
        # Handle special employment cases first
        if employment_status in ["Unemployed"]:
            return random.randint(0, 5000)
        elif employment_status == "Student":
            return random.randint(0, 15000)
        elif employment_status == "Retired":
            return random.randint(20000, 60000)
        
        # Base income for employed individuals
        base_income = 35000
        
        # Education multiplier
        education_multipliers = {
            "High School": 1.0,
            "Some College": 1.1,
            "Associate Degree": 1.2,
            "Bachelor's Degree": 1.5,
            "Master's Degree": 1.8,
            "Doctoral Degree": 2.2
        }
        
        # Age-based income progression
        if age < 25:
            age_multiplier = 0.7
        elif age < 35:
            age_multiplier = 1.0
        elif age < 45:
            age_multiplier = 1.3
        elif age < 55:
            age_multiplier = 1.5
        elif age < 65:
            age_multiplier = 1.4
        else:
            age_multiplier = 0.8  # Retirement consideration
        
        # Employment status multiplier
        employment_multipliers = {
            "Full-time": 1.0,
            "Part-time": 0.4,
            "Contract": 1.2,
            "Freelance": 0.8,
            "Self-employed": 1.1
        }
        
        income = int(
            base_income * 
            education_multipliers.get(education, 1.0) * 
            age_multiplier * 
            employment_multipliers.get(employment_status, 1.0) *
            random.uniform(0.8, 1.5)  # Random variation
        )
        
        # Round to nearest 1000
        return round(income, -3)
    
    def _map_faker_gender(self, faker_sex: str) -> str:
        """Map Faker's sex field to our gender field."""
        gender_mapping = {
            'M': 'Male',
            'F': 'Female'
        }
        return gender_mapping.get(faker_sex, 'Non-binary')
    
    def _extract_address_parts(self, address: str) -> Dict[str, str]:
        """Extract address components from Faker's address field."""
        # Faker's address is typically multi-line
        lines = address.strip().split('\n')
        
        if len(lines) >= 2:
            street_address = lines[0]
            # Last line usually contains city, state, zip
            city_state_zip = lines[-1]
            
            # Try to parse "City, State ZIP"
            try:
                city_state, zip_code = city_state_zip.rsplit(' ', 1)
                city, state = city_state.rsplit(', ', 1)
                return {
                    'street_address': street_address,
                    'city': city,
                    'state': state,
                    'zip_code': zip_code
                }
            except ValueError:
                # Fallback if parsing fails
                return {
                    'street_address': street_address,
                    'city': self.fake.city(),
                    'state': self.fake.state(),
                    'zip_code': self.fake.zipcode()
                }
        else:
            # Single line address, generate components separately
            return {
                'street_address': address,
                'city': self.fake.city(),
                'state': self.fake.state(),
                'zip_code': self.fake.zipcode()
            }
    
    def generate_profile(self) -> PersonProfile:
        """Generate a single person profile using faker.profile() as foundation."""
        
        # Generate base profile using Faker's profile() function
        base_profile = self.fake.profile()
        
        # Extract and calculate age from birthdate
        birth_date = base_profile['birthdate']
        age = np.clip(self._calculate_age(birth_date),MIN_AGE, MAX_AGE)
        
        # Map gender from Faker's sex field
        gender = self._map_faker_gender(base_profile['sex'])
        
        # Extract address components
        address_parts = self._extract_address_parts(base_profile['address'])
        
        # Generate employment status and education
        employment_status = random.choice(self.employment_statuses)
        education = random.choice(self.education_levels)
        
        # Calculate income based on age, education, and employment
        income = self._generate_income_by_age_education(age, education, employment_status)
        
        # Generate additional fields not covered by faker.profile()
        phone_number = self.fake.phone_number()

        ipv4_address = self.fake.ipv4()
        user_agent = self.fake.user_agent()
        blood_type = random.choice(["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        height_cm = random.randint(150, 200)
        weight_kg = random.randint(50, 120)
        marital_status = random.choice(self.marital_statuses)
        
        # Create PersonProfile from faker profile + additional data
        profile = PersonProfile(
            person_id=str(uuid.uuid4()),
            first_name=base_profile['name'].split()[0],
            last_name=base_profile['name'].split()[-1],
            full_name=base_profile['name'],
            gender=gender,
            date_of_birth=birth_date,
            age=age,
            email=base_profile['mail'],
            phone_number=phone_number,
            ssn=base_profile['ssn'],
            
            # Address (parsed from faker profile)
            street_address=address_parts['street_address'],
            city=address_parts['city'],
            state=address_parts['state'],
            zip_code=address_parts['zip_code'],
            country=self.fake.country(),
            country_code=self.fake.country_code(),
            
            # Professional (job from faker + our additions)
            job_title=base_profile['job'],
            company=base_profile['company'],
            employment_status=employment_status,
            annual_income=income,
            
            # Digital (username and website from faker + additions)
            username=base_profile['username'],
            website=base_profile['website'][0] if base_profile['website'] else self.fake.url(),
            ipv4_address=ipv4_address,
            user_agent=user_agent,
            
            # Personal (blood_group from faker if available)
            blood_type=base_profile.get('blood_group', blood_type),
            height_cm=height_cm,
            weight_kg=weight_kg,
            marital_status=marital_status,
            education_level=education,
        )
        
        return profile


def generate_person(locale: str = "en_US", seed: Optional[int] = None) -> PersonProfile:
    """
    Generate a single person profile.
    
    Args:
        locale: Faker locale for generated data
        seed: Random seed for reproducible results
        
    Returns:
        PersonProfile object
    """
    generator = PersonGenerator(locale=locale, seed=seed)
    return generator.generate_profile()


def generate_multiple_persons(
    count: int, 
    locale: str = "en_US", 
    seed: Optional[int] = None
) -> List[PersonProfile]:
    """
    Generate multiple person profiles.
    
    Args:
        count: Number of profiles to generate
        locale: Faker locale for generated data
        seed: Random seed for reproducible results
        
    Returns:
        List of PersonProfile objects
    """
    generator = PersonGenerator(locale=locale, seed=seed)
    return [generator.generate_profile() for _ in range(count)]


# Example usage and testing
if __name__ == "__main__":
    # Generate a few sample profiles to test
    print("Generating sample profiles using faker.profile()...\n")
    
    for i in range(3):
        person = generate_person(seed=i)  # Use different seeds for variety
        print(f"Profile {i+1}:")
        print(f"Name: {person.full_name}")
        print(f"Age: {person.age}, Gender: {person.gender}")
        print(f"Email: {person.email}")
        print(f"Job: {person.job_title} at {person.company}")
        print(f"Income: ${person.annual_income:,} ({person.employment_status})")
        print(f"Education: {person.education_level}")
        print(f"Address: {person.street_address}, {person.city}, {person.state} {person.zip_code}")
        print(f"Username: {person.username}")
        print(f"Website: {person.website}")
        print(f"Blood Type: {person.blood_type}")
        print("-" * 70)