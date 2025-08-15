"""
People workflow for generating person profiles.

Implements the people generation workflow using the existing person generator.
"""

from typing import List, Dict, Any
from workflows.base import BaseWorkflow, register_workflow, WorkflowConfig
from earth.generators.person import generate_multiple_persons


@register_workflow("people")
class PeopleWorkflow(BaseWorkflow):
    """Workflow for generating person profiles."""

    @property
    def workflow_name(self) -> str:
        """Return the name of this workflow."""
        return "People Generation"

    @property
    def schema_name(self) -> str:
        """Return the target schema name."""
        return "raw"

    @property
    def table_name(self) -> str:
        """Return the target table name."""
        return "persons"

    def generate_batch(self, batch_size: int) -> List[Dict[str, Any]]:
        """
        Generate a batch of person records.

        Args:
            batch_size: Number of person records to generate

        Returns:
            List of person record dictionaries
        """
        # Generate person profiles using existing generator
        persons = generate_multiple_persons(count=batch_size, seed=self.config.seed)

        # Convert to dictionaries
        return [person.to_dict() for person in persons]

    def get_statistics(self) -> Dict[str, Any]:
        """Get detailed statistics about generated people data."""
        if not self.conn:
            return {}

        try:
            # Basic stats
            basic_stats = self.conn.execute(
                f"""
                SELECT 
                    COUNT(*) as total_persons,
                    MIN(age) as min_age,
                    MAX(age) as max_age,
                    AVG(age) as avg_age,
                    COUNT(DISTINCT state) as unique_states,
                    COUNT(DISTINCT job_title) as unique_job_titles
                FROM {self.schema_name}.{self.table_name}
            """
            ).df()

            # Gender distribution
            gender_dist = self.conn.execute(
                f"""
                SELECT gender, COUNT(*) as count
                FROM {self.schema_name}.{self.table_name}
                GROUP BY gender
                ORDER BY count DESC
            """
            ).df()

            # Top cities
            top_cities = self.conn.execute(
                f"""
                SELECT city, state, COUNT(*) as count
                FROM {self.schema_name}.{self.table_name}
                GROUP BY city, state
                ORDER BY count DESC
                LIMIT 10
            """
            ).df()

            # Career level distribution
            career_dist = self.conn.execute(
                f"""
                SELECT career_level, COUNT(*) as count
                FROM {self.schema_name}.{self.table_name}
                GROUP BY career_level
                ORDER BY career_level
            """
            ).df()

            return {
                "basic_stats": (
                    basic_stats.to_dict("records")[0] if not basic_stats.empty else {}
                ),
                "gender_distribution": gender_dist.to_dict("records"),
                "top_cities": top_cities.to_dict("records"),
                "career_distribution": career_dist.to_dict("records"),
            }

        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            return {}
