"""
Person profile generator with sanitization layer for realistic US data.
Updated to use career progression helper for realistic job/salary correlation.
"""

import re
from datetime import datetime, date, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from faker import Faker
import uuid
import random
import numpy as np
from utils import MIN_AGE, MAX_AGE, EMAIL_DOMAINS
from generators.career import generate_career_profile, CareerLevel


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


class PersonGenerator:
    """Generator class for creating realistic person profiles with sanitization."""
    
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
    
    def _clean_name(self, full_name: str) -> Dict[str, str]:
        """
        Clean and extract first/last name from full name, removing titles.
        
        Args:
            full_name: Full name string from faker
            
        Returns:
            Dict with first_name, last_name, and cleaned full_name
        """
        # Common titles to remove
        titles_pattern = r'^(Dr\.|Mr\.|Mrs\.|Ms\.|Prof\.|Rev\.|Hon\.|Sr\.|Jr\.)\s+'
        
        # Remove titles
        cleaned_name = re.sub(titles_pattern, '', full_name.strip())
        
        # Split into parts
        name_parts = cleaned_name.split()
        
        if len(name_parts) >= 2:
            first_name = name_parts[0]
            last_name = name_parts[-1]  # Use last part as surname
            full_name_clean = f"{first_name} {last_name}"
        else:
            # Edge case: single name
            first_name = name_parts[0] if name_parts else "John"
            last_name = "Doe"
            full_name_clean = f"{first_name} {last_name}"
        
        return {
            'first_name': first_name,
            'last_name': last_name,
            'full_name': full_name_clean
        }
    
    def _generate_realistic_email(self, first_name: str, last_name: str) -> str:
        """
        Generate realistic email based on name.
        
        Args:
            first_name: Person's first name
            last_name: Person's last name
            
        Returns:
            Realistic email address
        """
        # Clean names for email (remove special chars, convert to lowercase)
        clean_first = re.sub(r'[^a-zA-Z]', '', first_name).lower()
        clean_last = re.sub(r'[^a-zA-Z]', '', last_name).lower()
        
        # Various email formats
        formats = [
            f"{clean_first[0]}.{clean_last}",  # j.smith
            f"{clean_first}.{clean_last}",     # john.smith
            f"{clean_first}{clean_last}",      # johnsmith
            f"{clean_first}_{clean_last}",     # john_smith
            f"{clean_first}{clean_last[0]}",   # johns
        ]
        
        email_format = random.choice(formats)
        domain = random.choice(EMAIL_DOMAINS)
        
        return f"{email_format}@{domain}"
    
    def _clean_phone_number(self, raw_phone: str) -> str:
        """
        Clean phone number to standard US format.
        
        Args:
            raw_phone: Raw phone number from faker
            
        Returns:
            Cleaned phone number in (XXX) XXX-XXXX format
        """
        # Extract only digits
        digits = re.sub(r'\D', '', raw_phone)
        
        # Ensure we have 10 digits for US phone numbers
        if len(digits) == 11 and digits[0] == '1':
            digits = digits[1:]  # Remove country code
        elif len(digits) != 10:
            # Generate a new US phone number
            digits = f"{random.randint(200, 999)}{random.randint(200, 999)}{random.randint(1000, 9999)}"
        
        # Format as (XXX) XXX-XXXX
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    
    def _map_faker_gender(self, faker_sex: str) -> str:
        """Map Faker's sex field to our gender field."""
        gender_mapping = {
            'M': 'Male',
            'F': 'Female'
        }
        return gender_mapping.get(faker_sex, 'Non-binary')
    
    def _sanitize_us_address(self, address: str) -> Dict[str, str]:
        """
        Extract and sanitize US address components.
        
        Args:
            address: Address string from faker
            
        Returns:
            Dict with sanitized address components
        """
        # For US-only scope, use faker's US-specific methods for better accuracy
        return {
            'street_address': self.fake.street_address(),
            'city': self.fake.city(),
            'state': self.fake.state_abbr(),  # Use abbreviations (CA, NY, etc.)
            'zip_code': self.fake.zipcode()   # This generates realistic US ZIP codes
        }
    
    def _get_weighted_employment_status(self, age: int) -> str:
        """
        Get employment status with age-appropriate weighting.
        
        Args:
            age: Person's age
            
        Returns:
            Employment status string
        """
        if age < 22:
            # Young people more likely to be students or part-time
            return random.choices(
                ["Student", "Part-time", "Full-time"],
                weights=[50, 35, 15]
            )[0]
        elif age < 65:
            # Working age adults
            return random.choices(
                ["Full-time", "Part-time", "Contract", "Freelance", "Self-employed", "Unemployed"],
                weights=[70, 10, 8, 5, 5, 2]
            )[0]
        else:
            # Retirement age
            return random.choices(
                ["Retired", "Part-time", "Self-employed", "Full-time"],
                weights=[70, 15, 10, 5]
            )[0]
    
    def _get_age_appropriate_education(self, age: int) -> str:
        """
        Get education level with age-appropriate distribution.
        
        Args:
            age: Person's age
            
        Returns:
            Education level string
        """
        if age < 22:
            # Younger people less likely to have advanced degrees
            return random.choices(
                ["High School", "Some College", "Associate Degree"],
                weights=[40, 50, 10]
            )[0]
        elif age < 30:
            # Recent graduates
            return random.choices(
                ["High School", "Some College", "Associate Degree", "Bachelor's Degree", "Master's Degree"],
                weights=[20, 25, 15, 35, 5]
            )[0]
        else:
            # Full distribution for older adults
            return random.choice(self.education_levels)
    
    def generate_profile(self) -> PersonProfile:
        """Generate a single sanitized person profile for US residents."""
        
        # Generate base profile using Faker's profile() function
        base_profile = self.fake.profile()
        
        # Extract and clamp age
        birth_date = base_profile['birthdate']
        age = np.clip(self._calculate_age(birth_date), MIN_AGE, MAX_AGE)
        
        # Clean name and extract components
        name_data = self._clean_name(base_profile['name'])
        
        # Generate realistic email based on cleaned name
        email = self._generate_realistic_email(name_data['first_name'], name_data['last_name'])
        
        # Map gender from Faker's sex field
        gender = self._map_faker_gender(base_profile['sex'])
        
        # Get sanitized US address components
        address_parts = self._sanitize_us_address(base_profile['address'])
        
        # Generate age-appropriate employment status and education
        employment_status = self._get_weighted_employment_status(age)
        education = self._get_age_appropriate_education(age)
        
        # Generate career profile using helper
        career_profile = generate_career_profile(age)
        
        # Generate and clean phone number (ensure US format)
        raw_phone = self.fake.phone_number()
        phone_number = self._clean_phone_number(raw_phone)
        
        # Generate additional fields
        ipv4_address = self.fake.ipv4()
        user_agent = self.fake.user_agent()
        blood_type = random.choice(["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        height_cm = random.randint(150, 200)
        weight_kg = random.randint(50, 120)
        marital_status = random.choice(self.marital_statuses)
        
        # Create PersonProfile with sanitized data and career information
        profile = PersonProfile(
            person_id=str(uuid.uuid4()),
            first_name=name_data['first_name'],
            last_name=name_data['last_name'],
            full_name=name_data['full_name'],
            gender=gender,
            date_of_birth=birth_date,
            age=age,
            email=email,
            phone_number=phone_number,
            ssn=base_profile['ssn'],
            
            # Sanitized US address
            street_address=address_parts['street_address'],
            city=address_parts['city'],
            state=address_parts['state'],
            zip_code=address_parts['zip_code'],
            country="United States",
            country_code="US",
            
            # Professional information from career helper
            job_title=career_profile.job_title,
            career_level=career_profile.career_level.value,  # Convert enum to string
            employment_status=employment_status,
            annual_income=career_profile.annual_income,
            
            # Digital (username from faker)
            username=base_profile['username'],
            ipv4_address=ipv4_address,
            user_agent=user_agent,
            
            # Personal
            blood_type=blood_type,
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
    # Generate a few sample profiles to test career progression
    print("Generating realistic US person profiles with career progression...\n")
    
    for i in range(8):
        person = generate_person(seed=i)
        print(f"Profile {i+1}:")
        print(f"Name: {person.full_name} (Age: {person.age})")
        print(f"Email: {person.email}")
        print(f"Phone: {person.phone_number}")
        print(f"Career: {person.career_level} - {person.job_title}")
        print(f"Income: ${person.annual_income:,} ({person.employment_status})")
        print(f"Location: {person.city}, {person.state} {person.zip_code}")
        print(f"Education: {person.education_level}")
        print("-" * 80)