"""
Base workflow infrastructure for Earth data generation.

This module provides the base classes and patterns for scalable workflow management.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Type
from dataclasses import dataclass
from enum import Enum
import logging

from earth.core.loader import (
    DatabaseConfig,
    connect_to_duckdb,
    operate_on_table,
    get_table_info,
)


class WorkflowStatus(Enum):
    """Workflow execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class WorkflowConfig:
    """Configuration for workflow execution."""

    batch_size: int = 1000
    max_records: int = 100000
    seed: Optional[int] = None
    write_mode: str = "append"  # append or truncate

    def validate(self) -> None:
        """Validate configuration parameters."""
        if self.batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if self.max_records <= 0:
            raise ValueError("max_records must be positive")
        if self.write_mode not in ["append", "truncate"]:
            raise ValueError("write_mode must be 'append' or 'truncate'")


@dataclass
class WorkflowResult:
    """Result of workflow execution."""

    status: WorkflowStatus
    records_generated: int = 0
    records_stored: int = 0
    error_message: Optional[str] = None
    execution_time: float = 0.0

    @property
    def success(self) -> bool:
        """Check if workflow completed successfully."""
        return self.status == WorkflowStatus.COMPLETED


class BaseWorkflow(ABC):
    """
    Abstract base class for all Earth data generation workflows.

    Provides common functionality and enforces interface consistency.
    """

    def __init__(
        self, config: WorkflowConfig, db_config: Optional[DatabaseConfig] = None
    ):
        """
        Initialize workflow.

        Args:
            config: Workflow configuration
            db_config: Database configuration (uses dev default if None)
        """
        self.config = config
        self.config.validate()

        self.db_config = db_config or DatabaseConfig.for_dev()
        self.conn = None
        self.logger = logging.getLogger(f"earth.workflow.{self.__class__.__name__}")

    @property
    @abstractmethod
    def workflow_name(self) -> str:
        """Return the name of this workflow."""
        pass

    @property
    @abstractmethod
    def schema_name(self) -> str:
        """Return the target schema name."""
        pass

    @property
    @abstractmethod
    def table_name(self) -> str:
        """Return the target table name."""
        pass

    @abstractmethod
    def generate_batch(self, batch_size: int) -> List[Dict[str, Any]]:
        """
        Generate a batch of records.

        Args:
            batch_size: Number of records to generate

        Returns:
            List of record dictionaries
        """
        pass

    def setup_database(self) -> None:
        """Initialize database connection and ensure schema exists."""
        try:
            self.conn = connect_to_duckdb(self.db_config)
            self.logger.info(
                f"Database connection established for {self.workflow_name}"
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise

    def get_current_status(self) -> Dict[str, Any]:
        """Get current table status and statistics."""
        if not self.conn:
            return {"exists": False, "row_count": 0}

        return get_table_info(self.conn, self.schema_name, self.table_name)

    def execute_batch(
        self, batch_data: List[Dict[str, Any]], is_first_batch: bool = False
    ) -> None:
        """
        Store a batch of data in the database.

        Args:
            batch_data: List of record dictionaries
            is_first_batch: Whether this is the first batch (affects write mode)
        """
        if not self.conn:
            raise RuntimeError("Database connection not established")

        import pandas as pd

        df = pd.DataFrame(batch_data)

        # Determine write method
        write_mode = self.config.write_mode if is_first_batch else "append"

        operate_on_table(
            conn=self.conn,
            schema_name=self.schema_name,
            table_name=self.table_name,
            action="write",
            object_data=df,
            how=write_mode,
        )

        self.logger.info(f"Stored batch of {len(batch_data)} records")

    def execute(self, target_records: int) -> WorkflowResult:
        """
        Execute the workflow to generate specified number of records.

        Args:
            target_records: Number of records to generate

        Returns:
            WorkflowResult with execution details
        """
        import time

        start_time = time.time()

        result = WorkflowResult(status=WorkflowStatus.PENDING)

        try:
            result.status = WorkflowStatus.RUNNING
            self.logger.info(
                f"Starting {self.workflow_name} workflow for {target_records} records"
            )

            # Setup database
            self.setup_database()

            # Generate and store data in batches
            total_generated = 0
            batch_count = 0

            while total_generated < target_records:
                batch_size = min(
                    self.config.batch_size, target_records - total_generated
                )

                self.logger.info(
                    f"Generating batch {batch_count + 1}, size: {batch_size}"
                )

                # Generate batch
                batch_data = self.generate_batch(batch_size)

                # Store batch
                self.execute_batch(batch_data, is_first_batch=(batch_count == 0))

                total_generated += len(batch_data)
                batch_count += 1

                # Progress logging
                progress = (total_generated / target_records) * 100
                self.logger.info(
                    f"Progress: {progress:.1f}% ({total_generated}/{target_records})"
                )

            # Final status
            final_info = self.get_current_status()

            result.status = WorkflowStatus.COMPLETED
            result.records_generated = total_generated
            result.records_stored = final_info.get("row_count", 0)

            self.logger.info(
                f"Workflow completed successfully: {total_generated} records generated"
            )

        except Exception as e:
            result.status = WorkflowStatus.FAILED
            result.error_message = str(e)
            self.logger.error(f"Workflow failed: {e}")

        finally:
            if self.conn:
                self.conn.close()

            result.execution_time = time.time() - start_time

        return result

    def cleanup(self) -> None:
        """Clean up workflow resources."""
        if self.conn:
            self.conn.close()
            self.conn = None


class WorkflowRegistry:
    """
    Registry for managing available workflows.

    Provides a scalable way to register and discover workflows.
    """

    _workflows: Dict[str, Type[BaseWorkflow]] = {}

    @classmethod
    def register(cls, name: str, workflow_class: Type[BaseWorkflow]) -> None:
        """
        Register a workflow class.

        Args:
            name: Unique workflow name
            workflow_class: Workflow class to register
        """
        cls._workflows[name] = workflow_class

    @classmethod
    def get_workflow(cls, name: str) -> Optional[Type[BaseWorkflow]]:
        """
        Get a workflow class by name.

        Args:
            name: Workflow name

        Returns:
            Workflow class or None if not found
        """
        return cls._workflows.get(name)

    @classmethod
    def list_workflows(cls) -> List[str]:
        """Get list of registered workflow names."""
        return list(cls._workflows.keys())

    @classmethod
    def create_workflow(
        cls,
        name: str,
        config: WorkflowConfig,
        db_config: Optional[DatabaseConfig] = None,
    ) -> BaseWorkflow:
        """
        Create a workflow instance by name.

        Args:
            name: Workflow name
            config: Workflow configuration
            db_config: Database configuration

        Returns:
            Workflow instance

        Raises:
            ValueError: If workflow name not found
        """
        workflow_class = cls.get_workflow(name)
        if not workflow_class:
            raise ValueError(f"Unknown workflow: {name}")

        return workflow_class(config, db_config)


# Decorator for easy workflow registration
def register_workflow(name: str):
    """
    Decorator to automatically register workflows.

    Usage:
        @register_workflow("people")
        class PeopleWorkflow(BaseWorkflow):
            ...
    """

    def decorator(workflow_class: Type[BaseWorkflow]):
        WorkflowRegistry.register(name, workflow_class)
        return workflow_class

    return decorator
