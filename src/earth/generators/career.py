"""
Career helper module for generating realistic career progression data.
Maps age to career level, then determines appropriate job title and salary.
"""

from earth.core.utils import (
    CareerProfile,
    CareerLevel,
    CAREER_TITLES,
    SALARY_RANGES,
    INDUSTRY_MULTIPLIERS,
)
import random


def determine_career_level(age: int) -> CareerLevel:
    """
    Determine career level based on age with some randomness.

    Args:
        age: Person's age

    Returns:
        CareerLevel enum value
    """
    if age < 22:
        # College age - entry level only
        return CareerLevel.CL_1
    elif age < 25:
        # Early career - mostly entry, some associate
        return random.choices([CareerLevel.CL_1, CareerLevel.CL_2], weights=[0.8, 0.2])[
            0
        ]
    elif age < 30:
        # Building experience
        return random.choices(
            [CareerLevel.CL_1, CareerLevel.CL_2, CareerLevel.CL_3],
            weights=[0.2, 0.6, 0.2],
        )[0]
    elif age < 35:
        # Establishing career
        return random.choices(
            [CareerLevel.CL_2, CareerLevel.CL_3, CareerLevel.CL_4],
            weights=[0.2, 0.6, 0.2],
        )[0]
    elif age < 40:
        # Mid-career progression
        return random.choices(
            [CareerLevel.CL_3, CareerLevel.CL_4, CareerLevel.CL_5],
            weights=[0.3, 0.5, 0.2],
        )[0]
    elif age < 45:
        # Senior roles emerging
        return random.choices(
            [CareerLevel.CL_3, CareerLevel.CL_4, CareerLevel.CL_5, CareerLevel.CL_6],
            weights=[0.2, 0.4, 0.3, 0.1],
        )[0]
    elif age < 50:
        # Leadership roles
        return random.choices(
            [CareerLevel.CL_4, CareerLevel.CL_5, CareerLevel.CL_6, CareerLevel.CL_7],
            weights=[0.2, 0.4, 0.3, 0.1],
        )[0]
    elif age < 55:
        # Peak career years
        return random.choices(
            [CareerLevel.CL_5, CareerLevel.CL_6, CareerLevel.CL_7, CareerLevel.CL_8],
            weights=[0.2, 0.4, 0.3, 0.1],
        )[0]
    elif age < 60:
        # Senior leadership
        return random.choices(
            [CareerLevel.CL_6, CareerLevel.CL_7, CareerLevel.CL_8],
            weights=[0.4, 0.4, 0.2],
        )[0]
    else:
        # Near retirement - mix of senior roles and some stepping down
        return random.choices(
            [CareerLevel.CL_5, CareerLevel.CL_6, CareerLevel.CL_7, CareerLevel.CL_8],
            weights=[0.2, 0.3, 0.3, 0.2],
        )[0]


def select_industry() -> str:
    """
    Select an industry with realistic distribution.

    Returns:
        Industry key
    """
    industries = [
        "tech",
        "business",
        "sales_marketing",
        "healthcare",
        "education",
        "general",
    ]
    weights = [0.15, 0.20, 0.20, 0.15, 0.10, 0.20]  # Realistic US job distribution
    return random.choices(industries, weights=weights)[0]


def calculate_salary(career_level: CareerLevel, industry: str, age: int) -> int:
    """
    Calculate salary based on career level, industry, and age.

    Args:
        career_level: Career level enum
        industry: Industry key
        age: Person's age for experience adjustments

    Returns:
        Annual salary
    """
    base_min, base_max = SALARY_RANGES[career_level]

    # Industry multiplier
    industry_mult = INDUSTRY_MULTIPLIERS.get(industry, 1.0)

    # Experience within level (age-based fine-tuning)
    experience_mult = 1.0
    if age > 30:
        experience_mult += min(0.3, (age - 30) * 0.02)  # Up to 30% bonus for experience

    # Calculate final range with multipliers
    final_min = int(base_min * industry_mult * experience_mult)
    final_max = int(base_max * industry_mult * experience_mult)

    # Add some randomness within the range
    salary = random.randint(final_min, final_max)

    # Round to nearest $1000
    return round(salary, -3)


def generate_career_profile(age: int) -> CareerProfile:
    """
    Generate a complete career profile based on age.

    Args:
        age: Person's age

    Returns:
        CareerProfile with level, title, and salary
    """
    # Determine career level based on age
    career_level = determine_career_level(age)

    # Select industry
    industry = select_industry()

    # Get job title for this level and industry
    job_titles = CAREER_TITLES[industry][career_level]
    job_title = random.choice(job_titles)

    # Calculate appropriate salary
    annual_income = calculate_salary(career_level, industry, age)

    return CareerProfile(
        career_level=career_level, job_title=job_title, annual_income=annual_income
    )


def generate_unemployment_profile(age: int, employment_status: str) -> CareerProfile:
    """
    Generate career profile for non-standard employment situations.

    Args:
        age: Person's age
        employment_status: Employment status (Unemployed, Student, Retired, etc.)

    Returns:
        CareerProfile with appropriate adjustments
    """
    if employment_status == "Unemployed":
        # Unemployed - use their last career level but zero/minimal income
        career_level = determine_career_level(age)
        job_title = "Unemployed"
        annual_income = random.randint(0, 15000)  # Unemployment benefits, etc.

    elif employment_status == "Student":
        # Students are typically entry level with minimal income
        career_level = CareerLevel.CL_1
        job_title = "Student"
        annual_income = random.randint(0, 25000)  # Part-time work, stipends

    elif employment_status == "Retired":
        # Retired - assume they had a senior career, now on fixed income
        career_level = random.choices(
            [CareerLevel.CL_5, CareerLevel.CL_6, CareerLevel.CL_7, CareerLevel.CL_8],
            weights=[0.4, 0.3, 0.2, 0.1],
        )[0]
        job_title = "Retired"
        annual_income = random.randint(30000, 80000)  # Retirement income

    else:
        # For other statuses, generate normal profile
        return generate_career_profile(age)

    return CareerProfile(
        career_level=career_level, job_title=job_title, annual_income=annual_income
    )


# Example usage and testing
if __name__ == "__main__":
    print("Testing Career Profile Generation:")
    print("=" * 50)

    test_ages = [22, 28, 35, 42, 50, 60]

    for age in test_ages:
        print(f"\nAge {age} examples:")
        for i in range(3):
            profile = generate_career_profile(age)
            print(
                f"  CL-{profile.career_level}: {profile.job_title} - ${profile.annual_income:,}"
            )

    print(f"\nSpecial Employment Status Examples:")
    print(f"Unemployed (35): {generate_unemployment_profile(35, 'Unemployed')}")
    print(f"Student (20): {generate_unemployment_profile(20, 'Student')}")
    print(f"Retired (67): {generate_unemployment_profile(67, 'Retired')}")
