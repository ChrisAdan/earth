"""
Companies workflow for generating company profiles.

Implements the companies generation workflow using the earth package generator.
Focuses on orchestration and database operations while delegating data generation
to the dedicated CompanyGenerator.
"""

from typing import List, Dict, Any
from workflows.base import BaseWorkflow, register_workflow, WorkflowConfig
from earth.generators.company import CompanyGenerator


@register_workflow("companies")
class CompaniesWorkflow(BaseWorkflow):
    """Workflow for generating company profiles using the earth package."""

    def __init__(self, config: WorkflowConfig, db_config=None):
        """
        Initialize companies workflow.

        Args:
            config: Workflow configuration
            db_config: Database configuration
        """
        super().__init__(config, db_config)
        self.generator = CompanyGenerator(seed=config.seed)

    @property
    def workflow_name(self) -> str:
        """Return the name of this workflow."""
        return "Companies Generation"

    @property
    def schema_name(self) -> str:
        """Return the target schema name."""
        return "raw"

    @property
    def table_name(self) -> str:
        """Return the target table name."""
        return "companies"

    def generate_batch(self, batch_size: int) -> List[Dict[str, Any]]:
        """
        Generate a batch of company records.

        Args:
            batch_size: Number of company records to generate

        Returns:
            List of company record dictionaries ready for database insertion
        """
        # Use the earth package generator to create company profiles
        company_profiles = self.generator.generate_batch(batch_size)

        # Convert profiles to dictionaries for database storage
        companies = [profile.to_dict() for profile in company_profiles]

        return companies

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get detailed statistics about generated companies data.

        Returns:
            Dictionary containing various statistics about the generated data
        """
        if not self.conn:
            return {}

        try:
            # Basic company statistics
            basic_stats = self.conn.execute(
                f"""
                SELECT 
                    COUNT(*) as total_companies,
                    COUNT(DISTINCT industry) as unique_industries,
                    AVG(employee_count) as avg_employees,
                    AVG(annual_revenue) as avg_revenue,
                    COUNT(*) FILTER (WHERE is_public = true) as public_companies,
                    MIN(founded_year) as oldest_company_year,
                    MAX(founded_year) as newest_company_year
                FROM {self.schema_name}.{self.table_name}
            """
            ).df()

            # Industry distribution
            industry_dist = self.conn.execute(
                f"""
                SELECT industry, COUNT(*) as count
                FROM {self.schema_name}.{self.table_name}
                GROUP BY industry
                ORDER BY count DESC
            """
            ).df()

            # Company size distribution
            size_dist = self.conn.execute(
                f"""
                SELECT company_size, COUNT(*) as count
                FROM {self.schema_name}.{self.table_name}
                GROUP BY company_size
                ORDER BY count DESC
            """
            ).df()

            # Geographic distribution (top states by headquarters)
            state_dist = self.conn.execute(
                f"""
                SELECT headquarters_state, COUNT(*) as count
                FROM {self.schema_name}.{self.table_name}
                GROUP BY headquarters_state
                ORDER BY count DESC
                LIMIT 10
            """
            ).df()

            # Business type distribution
            business_type_dist = self.conn.execute(
                f"""
                SELECT business_type, COUNT(*) as count
                FROM {self.schema_name}.{self.table_name}
                GROUP BY business_type
                ORDER BY count DESC
            """
            ).df()

            # Growth stage distribution
            growth_stage_dist = self.conn.execute(
                f"""
                SELECT growth_stage, COUNT(*) as count
                FROM {self.schema_name}.{self.table_name}
                GROUP BY growth_stage
                ORDER BY count DESC
            """
            ).df()

            # Revenue analysis by company size
            revenue_by_size = self.conn.execute(
                f"""
                SELECT 
                    company_size,
                    AVG(annual_revenue) as avg_revenue,
                    MIN(annual_revenue) as min_revenue,
                    MAX(annual_revenue) as max_revenue,
                    COUNT(*) as count
                FROM {self.schema_name}.{self.table_name}
                GROUP BY company_size
                ORDER BY avg_revenue DESC
            """
            ).df()

            return {
                "basic_stats": (
                    basic_stats.to_dict("records")[0] if not basic_stats.empty else {}
                ),
                "industry_distribution": industry_dist.to_dict("records"),
                "size_distribution": size_dist.to_dict("records"),
                "state_distribution": state_dist.to_dict("records"),
                "business_type_distribution": business_type_dist.to_dict("records"),
                "growth_stage_distribution": growth_stage_dist.to_dict("records"),
                "revenue_by_size": revenue_by_size.to_dict("records"),
            }

        except Exception as e:
            self.logger.error(f"Error getting companies statistics: {e}")
            return {}

    def validate_generated_data(self, companies: List[Dict[str, Any]]) -> bool:
        """
        Validate generated company data before database insertion.

        Args:
            companies: List of company records to validate

        Returns:
            True if all data is valid, False otherwise
        """
        required_fields = [
            "company_id",
            "company_name",
            "legal_name",
            "industry",
            "employee_count",
            "annual_revenue",
            "founded_year",
        ]

        for company in companies:
            # Check required fields exist
            for field in required_fields:
                if field not in company or company[field] is None:
                    self.logger.error(f"Missing required field: {field}")
                    return False

            # Validate data types and ranges
            if (
                not isinstance(company["employee_count"], int)
                or company["employee_count"] < 1
            ):
                self.logger.error(
                    f"Invalid employee_count: {company['employee_count']}"
                )
                return False

            if (
                not isinstance(company["annual_revenue"], int)
                or company["annual_revenue"] < 0
            ):
                self.logger.error(
                    f"Invalid annual_revenue: {company['annual_revenue']}"
                )
                return False

            current_year = 2024  # Could be dynamic
            if (
                not isinstance(company["founded_year"], int)
                or company["founded_year"] < 1800
                or company["founded_year"] > current_year
            ):
                self.logger.error(f"Invalid founded_year: {company['founded_year']}")
                return False

        return True

    def pre_generation_setup(self) -> None:
        """Setup tasks before generation starts."""
        super().pre_generation_setup()
        self.logger.info(
            f"Initialized {self.workflow_name} with seed: {self.config.seed}"
        )
        self.logger.info(f"Target: {self.schema_name}.{self.table_name}")

    def post_generation_cleanup(self) -> None:
        """Cleanup tasks after generation completes."""
        super().post_generation_cleanup()
        self.logger.info(f"{self.workflow_name} completed successfully")
