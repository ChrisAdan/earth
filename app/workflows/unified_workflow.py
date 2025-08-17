"""
Unified workflow implementation using the base generator pattern.

This module provides a clean, unified approach to entity workflows that
works seamlessly with the new dataset orchestration system.
"""

from typing import List, Dict, Any, Optional
from .base import BaseWorkflow, WorkflowConfig, WorkflowRegistry
from earth.generators.base import GeneratorConfig
from earth.generators.factory import create_generator
from earth.core.loader import DatabaseConfig


class EntityWorkflow(BaseWorkflow):
    """
    Unified workflow for generating any type of entity.

    Uses the BaseGenerator interface to work with different entity types
    while maintaining consistent workflow behavior and database operations.
    """

    def __init__(
        self,
        entity_type: str,
        config: WorkflowConfig,
        db_config: Optional[DatabaseConfig] = None,
        generator_config: Optional[GeneratorConfig] = None,
    ):
        """
        Initialize entity workflow.

        Args:
            entity_type: Type of entity to generate ("person", "company", etc.)
            config: Workflow configuration
            db_config: Database configuration
            generator_config: Generator-specific configuration
        """
        super().__init__(config, db_config)

        self.entity_type = entity_type.lower()

        # Create generator configuration, inheriting seed from workflow config
        if generator_config is None:
            generator_config = GeneratorConfig(
                locale="en_US", seed=config.seed, batch_size=config.batch_size
            )

        # Create the appropriate generator
        try:
            self.generator = create_generator(self.entity_type, generator_config)
        except Exception as e:
            raise ValueError(
                f"Failed to create generator for '{self.entity_type}': {e}"
            )

        # Set up entity-specific properties
        self._setup_entity_properties()

    def _setup_entity_properties(self):
        """Setup entity-specific workflow properties."""
        # Entity type to table mapping - centralized configuration
        entity_mappings = {
            "person": {
                "table": "persons",
                "workflow_name": "People Generation",
                "description": "Individual person profiles with demographics and career data",
            },
            "company": {
                "table": "companies",
                "workflow_name": "Companies Generation",
                "description": "Company profiles with business and financial data",
            },
        }

        mapping = entity_mappings.get(self.entity_type)
        if not mapping:
            raise ValueError(
                f"No mapping found for entity type: {self.entity_type}. "
                f"Available: {list(entity_mappings.keys())}"
            )

        self._table_name = mapping["table"]
        self._workflow_name = mapping["workflow_name"]
        self._description = mapping["description"]

    @property
    def workflow_name(self) -> str:
        """Return the name of this workflow."""
        return self._workflow_name

    @property
    def schema_name(self) -> str:
        """Return the target schema name."""
        return "raw"

    @property
    def table_name(self) -> str:
        """Return the target table name."""
        return self._table_name

    @property
    def description(self) -> str:
        """Return workflow description."""
        return self._description

    def generate_batch(self, batch_size: int) -> List[Dict[str, Any]]:
        """
        Generate a batch of entity records.

        Args:
            batch_size: Number of records to generate

        Returns:
            List of entity record dictionaries ready for database insertion
        """
        try:
            # Generate batch using the generator
            batch_dicts = self.generator.generate_batch_dicts(batch_size)

            # Validate the generated batch
            if not self._validate_batch(batch_dicts):
                raise RuntimeError(
                    f"Generated {self.entity_type} batch failed validation"
                )

            self.logger.debug(
                f"Successfully generated {len(batch_dicts)} {self.entity_type} records"
            )
            return batch_dicts

        except Exception as e:
            self.logger.error(f"Failed to generate {self.entity_type} batch: {e}")
            raise

    def _validate_batch(self, batch_data: List[Dict[str, Any]]) -> bool:
        """
        Validate generated batch data.

        Args:
            batch_data: List of entity records to validate

        Returns:
            True if valid, False otherwise
        """
        if not batch_data:
            self.logger.warning("Empty batch data")
            return False

        try:
            # Check required fields for each record
            for i, record in enumerate(batch_data):
                if not self._validate_record(record):
                    self.logger.error(f"Record {i} failed validation")
                    return False

            # Additional batch-level validations
            return self._validate_batch_consistency(batch_data)

        except Exception as e:
            self.logger.error(f"Batch validation failed: {e}")
            return False

    def _validate_record(self, record: Dict[str, Any]) -> bool:
        """
        Validate a single record.

        Args:
            record: Record dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        # Check required fields exist and are not None
        for field in self.generator.required_fields:
            if field not in record:
                self.logger.error(f"Missing required field: {field}")
                return False
            if record[field] is None:
                self.logger.error(f"Required field {field} is None")
                return False

        # Entity-specific validations
        return self._validate_record_business_rules(record)

    def _validate_record_business_rules(self, record: Dict[str, Any]) -> bool:
        """
        Apply entity-specific business rule validations.

        Args:
            record: Record dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        if self.entity_type == "person":
            # Person-specific validations
            if "age" in record and (record["age"] < 18 or record["age"] > 120):
                self.logger.error(f"Invalid age: {record['age']}")
                return False

            if "annual_income" in record and record["annual_income"] < 0:
                self.logger.error(f"Negative income: {record['annual_income']}")
                return False

            if "email" in record and "@" not in record["email"]:
                self.logger.error(f"Invalid email format: {record['email']}")
                return False

        elif self.entity_type == "company":
            # Company-specific validations
            if "employee_count" in record and record["employee_count"] <= 0:
                self.logger.error(f"Invalid employee count: {record['employee_count']}")
                return False

            if "annual_revenue" in record and record["annual_revenue"] < 0:
                self.logger.error(f"Negative revenue: {record['annual_revenue']}")
                return False

        return True

    def _validate_batch_consistency(self, batch_data: List[Dict[str, Any]]) -> bool:
        """
        Validate consistency across the batch.

        Args:
            batch_data: List of entity records

        Returns:
            True if consistent, False otherwise
        """
        # Check for duplicate IDs
        id_field = f"{self.entity_type}_id"
        if id_field in batch_data[0]:  # Only check if ID field exists
            ids = [record[id_field] for record in batch_data]
            if len(ids) != len(set(ids)):
                self.logger.error("Duplicate IDs found in batch")
                return False

        # Check for consistent field structure
        expected_fields = set(batch_data[0].keys())
        for record in batch_data[1:]:
            if set(record.keys()) != expected_fields:
                self.logger.error("Inconsistent field structure in batch")
                return False

        return True

    def get_generation_statistics(
        self, batch_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get detailed statistics about generated data.

        Args:
            batch_data: Generated batch data

        Returns:
            Dictionary containing various statistics
        """
        if not batch_data:
            return {"error": "No data provided"}

        try:
            stats = {
                "entity_type": self.entity_type,
                "batch_size": len(batch_data),
                "workflow_name": self.workflow_name,
                "table_target": f"{self.schema_name}.{self.table_name}",
                "fields": list(batch_data[0].keys()),
                "field_count": len(batch_data[0].keys()),
            }

            # Add entity-specific statistics
            if self.entity_type == "person":
                ages = [record.get("age", 0) for record in batch_data]
                incomes = [record.get("annual_income", 0) for record in batch_data]

                stats["person_stats"] = {
                    "age_range": {
                        "min": min(ages),
                        "max": max(ages),
                        "avg": sum(ages) / len(ages),
                    },
                    "income_range": {
                        "min": min(incomes),
                        "max": max(incomes),
                        "avg": sum(incomes) / len(incomes),
                    },
                    "unique_job_titles": len(
                        set(record.get("job_title", "") for record in batch_data)
                    ),
                }

            elif self.entity_type == "company":
                employees = [record.get("employee_count", 0) for record in batch_data]
                revenues = [record.get("annual_revenue", 0) for record in batch_data]

                stats["company_stats"] = {
                    "employee_range": {
                        "min": min(employees),
                        "max": max(employees),
                        "avg": sum(employees) / len(employees),
                    },
                    "revenue_range": {
                        "min": min(revenues),
                        "max": max(revenues),
                        "avg": sum(revenues) / len(revenues),
                    },
                    "unique_industries": len(
                        set(record.get("industry", "") for record in batch_data)
                    ),
                }

            # Sample record for inspection (remove sensitive data if any)
            sample_record = batch_data[0].copy()
            stats["sample_record"] = sample_record

            return stats

        except Exception as e:
            self.logger.error(f"Error generating statistics: {e}")
            return {"error": str(e)}

    def execute_with_detailed_stats(self, target_records: int) -> Dict[str, Any]:
        """
        Execute workflow and return detailed statistics along with result.

        Args:
            target_records: Number of records to generate

        Returns:
            Dictionary with result and detailed statistics
        """
        result = self.execute(target_records)

        # Get final table statistics
        final_stats = self.get_current_status() if self.conn else {}

        return {
            "workflow_result": {
                "success": result.success,
                "status": result.status.value,
                "records_generated": result.records_generated,
                "records_stored": result.records_stored,
                "execution_time": result.execution_time,
                "error_message": result.error_message,
            },
            "workflow_info": {
                "entity_type": self.entity_type,
                "workflow_name": self.workflow_name,
                "description": self.description,
                "target_table": f"{self.schema_name}.{self.table_name}",
            },
            "final_table_stats": final_stats,
            "configuration": {
                "batch_size": self.config.batch_size,
                "write_mode": self.config.write_mode,
                "seed": self.config.seed,
            },
        }


# Concrete workflow implementations for backward compatibility
class PeopleWorkflow(EntityWorkflow):
    """People-specific workflow implementation."""

    def __init__(
        self, config: WorkflowConfig, db_config: Optional[DatabaseConfig] = None
    ):
        """Initialize people workflow."""
        super().__init__("person", config, db_config)


class CompaniesWorkflow(EntityWorkflow):
    """Companies-specific workflow implementation."""

    def __init__(
        self, config: WorkflowConfig, db_config: Optional[DatabaseConfig] = None
    ):
        """Initialize companies workflow."""
        super().__init__("company", config, db_config)


# Factory function for creating workflows
def create_entity_workflow(
    entity_type: str,
    config: WorkflowConfig,
    db_config: Optional[DatabaseConfig] = None,
    generator_config: Optional[GeneratorConfig] = None,
) -> EntityWorkflow:
    """
    Factory function to create entity workflows.

    Args:
        entity_type: Type of entity ("person", "company", etc.)
        config: Workflow configuration
        db_config: Database configuration
        generator_config: Generator-specific configuration

    Returns:
        EntityWorkflow instance
    """
    return EntityWorkflow(entity_type, config, db_config, generator_config)


# Enhanced Workflow Registry
class UnifiedWorkflowRegistry:
    """
    Enhanced workflow registry supporting both class-based and factory patterns.

    This registry provides a unified interface for creating any type of workflow,
    whether it's a simple entity workflow or a complex orchestrated dataset workflow.
    """

    # Registry of special workflow factories
    _special_workflows = {}

    @classmethod
    def register_special_workflow(cls, name: str, factory_func):
        """Register a special workflow factory function."""
        cls._special_workflows[name] = factory_func

    @classmethod
    def create_workflow(
        cls, workflow_name: str, config: WorkflowConfig, db_config=None, **kwargs
    ) -> BaseWorkflow:
        """
        Create workflow instance with unified interface.

        Args:
            workflow_name: Name of workflow to create
            config: Workflow configuration
            db_config: Database configuration
            **kwargs: Additional workflow-specific arguments

        Returns:
            Workflow instance

        Raises:
            ValueError: If workflow name not recognized
        """
        # Check for special workflows first
        if workflow_name in cls._special_workflows:
            return cls._special_workflows[workflow_name](config, db_config, **kwargs)

        # Handle dataset workflows
        if workflow_name == "dataset":
            from .dataset_orchestrator import DatasetWorkflow

            return DatasetWorkflow(config, db_config, **kwargs)

        # Check base registry for registered classes
        workflow_class = WorkflowRegistry.get_workflow(workflow_name)
        if workflow_class:
            return workflow_class(config, db_config)

        # Try to create as entity workflow
        entity_mappings = {"people": "person", "companies": "company"}
        entity_type = entity_mappings.get(workflow_name)

        if entity_type:
            return create_entity_workflow(entity_type, config, db_config)

        # Workflow not found
        available_workflows = (
            list(cls._special_workflows.keys())
            + WorkflowRegistry.list_workflows()
            + list(entity_mappings.keys())
            + ["dataset"]
        )
        raise ValueError(
            f"Unknown workflow '{workflow_name}'. Available: {available_workflows}"
        )


# Register concrete workflow classes with the base registry
def _register_workflows():
    """Register all workflow classes with the registry."""
    WorkflowRegistry.register("people", PeopleWorkflow)
    WorkflowRegistry.register("companies", CompaniesWorkflow)


# Call registration when module is imported
_register_workflows()


# Register dataset workflow factory
def _create_dataset_workflow(config: WorkflowConfig, db_config=None, **kwargs):
    """Factory function for dataset workflows."""
    from .dataset_orchestrator import DatasetWorkflow

    return DatasetWorkflow(config, db_config, **kwargs)


UnifiedWorkflowRegistry.register_special_workflow("dataset", _create_dataset_workflow)
