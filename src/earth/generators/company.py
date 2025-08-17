"""
Refactored company generator using the BaseGenerator pattern.

Updates the existing CompanyGenerator to inherit from BaseGenerator
while maintaining all existing functionality.
"""

from typing import List, Dict, Any, Optional, Tuple, cast
from datetime import datetime, timezone, date
from dataclasses import dataclass
import uuid
import random

from earth.generators.base import BaseGenerator, GeneratorConfig
from earth.core.utils import (
    IndustryMetadata,
    COMPANY_SIZE_CATEGORIES,
    BUSINESS_TYPES,
    REVENUE_RANGES,
    CREDIT_RATINGS,
    GROWTH_STAGES,
    LEGAL_SUFFIXES,
)


@dataclass
class CompanyProfile:
    """Data class representing a comprehensive company profile."""

    company_id: str
    company_name: str
    legal_name: str
    industry: str
    sector: str
    company_size: str
    employee_count: int
    founded_year: int
    revenue_range: str
    annual_revenue: int

    # Contact information
    headquarters_address: str
    headquarters_city: str
    headquarters_state: str
    headquarters_zip: str
    phone: str
    website: str
    email_domain: str

    # Business details
    business_type: str  # Corporation, LLC, Partnership, etc.
    stock_symbol: Optional[str]
    is_public: bool
    description: str

    # Geographic presence
    office_locations: int
    operates_internationally: bool
    primary_market: str

    # Financial indicators
    credit_rating: str
    years_in_business: int
    growth_stage: str  # Startup, Growth, Mature, Decline

    # Metadata
    created_at: datetime = datetime.now(timezone.utc)
    created_by: str = "earth_generator"

    def __post_init__(self) -> None:
        """Set default created_at if not provided."""
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Convert company profile to dictionary for database storage."""
        result = {}
        for field, value in self.__dict__.items():
            if isinstance(value, date):
                result[field] = value.isoformat()
            elif isinstance(value, datetime):
                result[field] = value.isoformat()
            else:
                result[field] = value
        return result


class CompanyGenerator(BaseGenerator[CompanyProfile]):
    """
    Company generator implementing the BaseGenerator interface.

    Creates comprehensive business data including financial metrics,
    geographic presence, and industry-specific characteristics.
    """

    def __init__(self, config: Optional[GeneratorConfig] = None):
        """Initialize company generator."""
        super().__init__(config)

        # Industry categories aligned with NAICS sectors
        self.industries = IndustryMetadata._get_title_case_industry_names()

        # Company size categories with employee ranges
        self.size_categories = COMPANY_SIZE_CATEGORIES

        # Business entity types
        self.business_types = BUSINESS_TYPES

        # Revenue ranges by company size
        self.revenue_ranges = REVENUE_RANGES

        # Credit rating scale
        self.credit_ratings = CREDIT_RATINGS

        # Business growth stages
        self.growth_stages = GROWTH_STAGES

    @property
    def entity_name(self) -> str:
        """Return the name of the entity this generator creates."""
        return "company"

    @property
    def required_fields(self) -> List[str]:
        """Return list of required fields for validation."""
        return [
            "company_id",
            "company_name",
            "legal_name",
            "industry",
            "employee_count",
            "annual_revenue",
            "founded_year",
        ]

    def _generate_company_name(self) -> Tuple[str, str]:
        """
        Generate company name and legal name.

        Returns:
            Tuple of (company_name, legal_name)
        """
        # Various company name patterns
        patterns = [
            lambda: f"{self.fake.company()}",
            lambda: f"{self.fake.last_name()} {random.choice(['Technologies', 'Solutions', 'Systems', 'Group'])}",
            lambda: f"{self.fake.city()} {random.choice(['Corp', 'Industries', 'Company', 'Enterprises'])}",
            lambda: f"{random.choice(['Innovative', 'Advanced', 'Global', 'Premier', 'Dynamic'])} {self.fake.company()}",
            lambda: f"{self.fake.company().replace('Ltd', '').replace('Inc', '').strip()}",
        ]

        company_name = random.choice(patterns)()

        # Generate legal name with appropriate suffix
        legal_suffixes = LEGAL_SUFFIXES
        if not any(suffix in company_name for suffix in legal_suffixes):
            legal_name = f"{company_name} {random.choice(legal_suffixes)}"
        else:
            legal_name = company_name

        return company_name, legal_name

    def _determine_company_size_and_employees(self) -> Tuple[str, int]:
        """
        Determine company size category and employee count.

        Uses realistic market distribution favoring smaller companies.

        Returns:
            Tuple of (size_category, employee_count)
        """
        # Realistic distribution - most companies are small
        size_weights = {
            "Startup": 0.25,
            "Small": 0.35,
            "Medium": 0.20,
            "Large": 0.12,
            "Enterprise": 0.06,
            "Mega Corp": 0.02,
        }

        size_category = random.choices(
            list(size_weights.keys()), weights=list(size_weights.values())
        )[0]

        min_emp, max_emp = self.size_categories[size_category]
        employee_count = random.randint(min_emp, max_emp)

        return size_category, employee_count

    def _generate_revenue(self, company_size: str, industry: str) -> Tuple[str, int]:
        """
        Generate revenue based on company size and industry.

        Args:
            company_size: Size category of the company
            industry: Industry sector

        Returns:
            Tuple of (revenue_range_text, annual_revenue)
        """
        revenue_range_text, (min_rev, max_rev) = self.revenue_ranges[company_size]

        # Apply industry-specific revenue multiplier
        industry_key = industry.lower().replace(" ", "_")
        industry_multiplier = getattr(IndustryMetadata, industry_key).value

        # Add randomness to multiplier (±20%)
        adjusted_min = int(min_rev * industry_multiplier * random.uniform(0.8, 1.2))
        adjusted_max = int(max_rev * industry_multiplier * random.uniform(0.8, 1.2))

        annual_revenue = random.randint(adjusted_min, adjusted_max)

        return revenue_range_text, annual_revenue

    def _generate_website_and_email(self, company_name: str) -> Tuple[str, str]:
        """
        Generate website URL and email domain based on company name.

        Args:
            company_name: Name of the company

        Returns:
            Tuple of (website_url, email_domain)
        """
        # Clean company name for domain (alphanumeric only, max 15 chars)
        clean_name = "".join(c.lower() for c in company_name if c.isalnum())[:15]

        # Common domain patterns for businesses
        domain_patterns = [
            f"{clean_name}.com",
            f"{clean_name}corp.com",
            f"{clean_name}inc.com",
            f"get{clean_name}.com",
            f"{clean_name}solutions.com",
        ]

        email_domain = random.choice(domain_patterns)
        website = f"https://www.{email_domain}"

        return website, email_domain

    def _determine_stock_status(
        self, company_size: str, company_name: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Determine if company is public and generate stock symbol.

        Args:
            company_size: Size category of company
            company_name: Name of company

        Returns:
            Tuple of (is_public, stock_symbol)
        """
        # Larger companies more likely to be public
        public_probability = {
            "Startup": 0.01,
            "Small": 0.02,
            "Medium": 0.05,
            "Large": 0.15,
            "Enterprise": 0.30,
            "Mega Corp": 0.70,
        }

        is_public = random.random() < public_probability[company_size]
        stock_symbol = None

        if is_public:
            # Generate realistic stock symbol patterns
            symbol_patterns = [
                company_name[:3].upper(),
                company_name[:4].upper(),
                f"{company_name[:2].upper()}{random.choice(['X', 'Z', 'T'])}",
            ]
            stock_symbol = random.choice(symbol_patterns)

        return is_public, stock_symbol

    def _determine_growth_stage(self, years_in_business: int) -> str:
        """
        Determine growth stage based on company age.

        Args:
            years_in_business: Number of years since founding

        Returns:
            Growth stage classification
        """
        if years_in_business < 3:
            return "Startup"
        elif years_in_business < 10:
            return random.choice(["Startup", "Growth"])
        elif years_in_business < 25:
            return random.choice(["Growth", "Mature"])
        else:
            return random.choice(["Mature", "Decline"])

    def generate_profile(self) -> CompanyProfile:
        """
        Generate a complete company profile with realistic data.

        Returns:
            CompanyProfile object with all company information
        """
        # Basic company information
        company_name, legal_name = self._generate_company_name()
        industry = random.choice(self.industries)
        company_size, employee_count = self._determine_company_size_and_employees()

        # Financial information
        revenue_range, annual_revenue = self._generate_revenue(company_size, industry)

        # Company age - bias towards recent companies for startups
        current_year = datetime.now().year
        if company_size == "Startup":
            founded_year = random.randint(current_year - 5, current_year)
        elif company_size in ["Small", "Medium"]:
            founded_year = random.randint(current_year - 20, current_year)
        else:
            founded_year = random.randint(current_year - 50, current_year)

        years_in_business = current_year - founded_year

        # Headquarters location (US-focused)
        hq_address = self.fake.street_address()
        hq_city = self.fake.city()
        hq_state = self.fake.state_abbr()
        hq_zip = self.fake.zipcode()

        # Contact information
        phone = self.fake.phone_number()
        website, email_domain = self._generate_website_and_email(company_name)

        # Business structure and public status
        business_type = random.choice(self.business_types)
        is_public, stock_symbol = self._determine_stock_status(
            company_size, company_name
        )

        # Geographic presence
        office_locations = random.randint(1, min(50, employee_count // 20 + 1))
        operates_internationally = (
            company_size in ["Enterprise", "Mega Corp"] and random.random() < 0.6
        )

        # Market focus
        primary_markets = ["B2B", "B2C", "B2G", "B2B2C"]
        primary_market = random.choice(primary_markets)

        # Financial indicators
        credit_rating = random.choice(self.credit_ratings)
        growth_stage = self._determine_growth_stage(years_in_business)

        # Business description
        description = self.fake.catch_phrase()

        # Sector mapping from industry
        sector_mapping = {
            "Technology": "Information Technology",
            "Healthcare": "Healthcare",
            "Financial Services": "Financial Services",
            "Manufacturing": "Industrials",
            "Retail": "Consumer Discretionary",
            "Energy": "Energy",
            "Real Estate": "Real Estate",
            "Telecommunications": "Communication Services",
            "Utilities": "Utilities",
        }
        sector = sector_mapping.get(industry, "Miscellaneous")

        return CompanyProfile(
            company_id=str(uuid.uuid4()),
            company_name=company_name,
            legal_name=legal_name,
            industry=industry,
            sector=sector,
            company_size=company_size,
            employee_count=employee_count,
            founded_year=founded_year,
            revenue_range=revenue_range,
            annual_revenue=annual_revenue,
            headquarters_address=hq_address,
            headquarters_city=hq_city,
            headquarters_state=hq_state,
            headquarters_zip=hq_zip,
            phone=phone,
            website=website,
            email_domain=email_domain,
            business_type=business_type,
            stock_symbol=stock_symbol,
            is_public=is_public,
            description=description,
            office_locations=office_locations,
            operates_internationally=operates_internationally,
            primary_market=primary_market,
            credit_rating=credit_rating,
            years_in_business=years_in_business,
            growth_stage=growth_stage,
        )

    def _custom_validation(self, profile_dict: Dict[str, Any]) -> bool:
        """
        Custom validation for company profiles.

        Args:
            profile_dict: Profile dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        # Validate employee count
        employees = profile_dict.get("employee_count", 0)
        if not isinstance(employees, int) or employees < 1:
            return False

        # Validate revenue
        revenue = profile_dict.get("annual_revenue", 0)
        if not isinstance(revenue, int) or revenue < 0:
            return False

        # Validate founded year
        founded = profile_dict.get("founded_year", 0)
        current_year = datetime.now().year
        if not isinstance(founded, int) or founded < 1800 or founded > current_year:
            return False

        return True

    def _get_custom_stats(self, profiles: List[CompanyProfile]) -> Dict[str, Any]:
        """
        Get company-specific statistics.

        Args:
            profiles: List of generated company profiles

        Returns:
            Dictionary with company statistics
        """
        if not profiles:
            return {}

        # Employee statistics
        employees = [p.employee_count for p in profiles]
        employee_stats = {
            "min_employees": min(employees),
            "max_employees": max(employees),
            "avg_employees": sum(employees) / len(employees),
        }

        # Revenue statistics
        revenues = [p.annual_revenue for p in profiles]
        revenue_stats = {
            "min_revenue": min(revenues),
            "max_revenue": max(revenues),
            "avg_revenue": sum(revenues) / len(revenues),
        }

        # Industry distribution
        industry_counts: dict[str, int] = cast(dict, {})
        for profile in profiles:
            industry = profile.industry
            industry_counts[industry] = industry_counts.get(industry, 0) + 1

        # Size distribution
        size_counts: dict[str, int] = cast(dict, {})
        for profile in profiles:
            size = profile.company_size
            size_counts[size] = size_counts.get(size, 0) + 1

        # Public/private split
        public_count = sum(1 for p in profiles if p.is_public)
        private_count = len(profiles) - public_count

        return {
            "employee_stats": employee_stats,
            "revenue_stats": revenue_stats,
            "industry_distribution": industry_counts,
            "size_distribution": size_counts,
            "public_private": {"public": public_count, "private": private_count},
        }
