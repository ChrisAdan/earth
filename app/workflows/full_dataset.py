"""
Full dataset workflow for orchestrating multiple data generation workflows.

This workflow coordinates the generation of a complete synthetic dataset
by running multiple individual workflows in sequence or parallel.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import time

from workflows.base import (
    BaseWorkflow,
    WorkflowConfig,
    WorkflowResult,
    WorkflowStatus,
    WorkflowRegistry,
    register_workflow,
)
from earth.core.loader import DatabaseConfig


@dataclass
class DatasetSpec:
    """Specification for a complete dataset generation."""

    people_count: int = 1000
    companies_count: int = 100
    # Future entities can be added here
    # transactions_count: int = 5000
    # events_count: int = 2000

    # Ratios for validation (people to companies ratio should be realistic)
    min_people_per_company: float = 5.0
    max_people_per_company: float = 50.0

    def validate(self) -> None:
        """Validate dataset specifications."""
        if self.people_count <= 0:
            raise ValueError("people_count must be positive")
        if self.companies_count <= 0:
            raise ValueError("companies_count must be positive")

        # Check realistic ratios
        ratio = self.people_count / self.companies_count
        if ratio < self.min_people_per_company:
            raise ValueError(f"Too few people per company (ratio: {ratio:.1f})")
        if ratio > self.max_people_per_company:
            raise ValueError(f"Too many people per company (ratio: {ratio:.1f})")


@dataclass
class WorkflowStep:
    """Individual workflow step in the full dataset generation."""

    workflow_name: str
    target_records: int
    depends_on: List[str] = field(default_factory=list)
    config_overrides: Dict[str, Any] = field(default_factory=dict)

    # Results (populated after execution)
    result: Optional[WorkflowResult] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None

    @property
    def duration(self) -> float:
        """Get execution duration in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0

    @property
    def status(self) -> WorkflowStatus:
        """Get current status of this step."""
        if self.result:
            return self.result.status
        return WorkflowStatus.PENDING


@register_workflow("full_dataset")
class FullDatasetWorkflow(BaseWorkflow):
    """
    Orchestrates generation of a complete synthetic dataset.

    This workflow manages multiple individual workflows to create
    a cohesive dataset with proper relationships and dependencies.
    """

    def __init__(
        self,
        config: WorkflowConfig,
        db_config: Optional[DatabaseConfig] = None,
        dataset_spec: Optional[DatasetSpec] = None,
    ):
        """
        Initialize full dataset workflow.

        Args:
            config: Base workflow configuration
            db_config: Database configuration
            dataset_spec: Dataset specification (uses default if None)
        """
        super().__init__(config, db_config)
        self.dataset_spec = dataset_spec or DatasetSpec()
        self.dataset_spec.validate()

        # Build workflow steps based on specification
        self.workflow_steps = self._build_workflow_steps()

        # Track overall progress
        self.completed_steps = 0
        self.total_steps = len(self.workflow_steps)

    def _build_workflow_steps(self) -> List[WorkflowStep]:
        """Build the list of workflow steps to execute."""
        steps = []

        # Step 1: Generate companies (foundational data)
        steps.append(
            WorkflowStep(
                workflow_name="companies",
                target_records=self.dataset_spec.companies_count,
                depends_on=[],  # No dependencies
                config_overrides={"write_mode": "truncate"},  # Start fresh
            )
        )

        # Step 2: Generate people (depends on companies existing)
        steps.append(
            WorkflowStep(
                workflow_name="people",
                target_records=self.dataset_spec.people_count,
                depends_on=["companies"],  # Wait for companies to complete
                config_overrides={"write_mode": "truncate"},  # Start fresh
            )
        )

        # Future workflow steps can be added here as new generators are created
        # Example:
        # steps.append(WorkflowStep(
        #     workflow_name="transactions",
        #     target_records=self.dataset_spec.transactions_count,
        #     depends_on=["people", "companies"],
        #     config_overrides={"write_mode": "truncate"}
        # ))

        return steps

    @property
    def workflow_name(self) -> str:
        """Return the name of this workflow."""
        return "Full Dataset Generation"

    @property
    def schema_name(self) -> str:
        """Return the target schema name."""
        return "raw"  # Uses multiple tables in raw schema

    @property
    def table_name(self) -> str:
        """Return the target table name."""
        return "dataset_metadata"  # Metadata about the full dataset

    def generate_batch(self, batch_size: int) -> List[Dict[str, Any]]:
        """
        Generate batch - not used for full dataset workflow.

        This method is required by BaseWorkflow but not used since
        FullDatasetWorkflow orchestrates other workflows.
        """
        # Generate metadata about the dataset generation process
        return [
            {
                "dataset_id": f"dataset_{int(time.time())}",
                "total_steps": self.total_steps,
                "completed_steps": self.completed_steps,
                "people_target": self.dataset_spec.people_count,
                "companies_target": self.dataset_spec.companies_count,
                "status": (
                    "in_progress"
                    if self.completed_steps < self.total_steps
                    else "completed"
                ),
            }
        ]

    def _check_dependencies(self, step: WorkflowStep) -> bool:
        """
        Check if all dependencies for a workflow step are satisfied.

        Args:
            step: Workflow step to check

        Returns:
            True if all dependencies are satisfied
        """
        for dep_name in step.depends_on:
            dep_step = next(
                (s for s in self.workflow_steps if s.workflow_name == dep_name), None
            )
            if not dep_step or dep_step.status != WorkflowStatus.COMPLETED:
                return False
        return True

    def _execute_workflow_step(self, step: WorkflowStep) -> WorkflowResult:
        """
        Execute a single workflow step.

        Args:
            step: Workflow step to execute

        Returns:
            WorkflowResult from the step execution
        """
        self.logger.info(f"Starting workflow step: {step.workflow_name}")

        # Create workflow configuration with overrides
        step_config = WorkflowConfig(
            batch_size=self.config.batch_size,
            max_records=self.config.max_records,
            seed=self.config.seed,
            write_mode=self.config.write_mode,
        )

        # Apply configuration overrides
        for key, value in step.config_overrides.items():
            setattr(step_config, key, value)

        # Create and execute the workflow
        try:
            workflow = WorkflowRegistry.create_workflow(
                step.workflow_name, step_config, self.db_config
            )

            step.start_time = time.time()
            result = workflow.execute(step.target_records)
            step.end_time = time.time()

            step.result = result

            if result.success:
                self.logger.info(
                    f"Completed workflow step: {step.workflow_name} "
                    f"({result.records_generated} records in {step.duration:.1f}s)"
                )
                self.completed_steps += 1
            else:
                self.logger.error(
                    f"Failed workflow step: {step.workflow_name} - {result.error_message}"
                )

            return result

        except Exception as e:
            step.end_time = time.time()
            error_result = WorkflowResult(
                status=WorkflowStatus.FAILED, error_message=str(e)
            )
            step.result = error_result
            self.logger.error(f"Exception in workflow step {step.workflow_name}: {e}")
            return error_result

    def execute(self, target_records: int = None) -> WorkflowResult:
        """
        Execute the full dataset generation workflow.

        Args:
            target_records: Ignored for full dataset workflow

        Returns:
            WorkflowResult with overall execution details
        """
        start_time = time.time()

        result = WorkflowResult(status=WorkflowStatus.RUNNING)

        try:
            self.logger.info(
                f"Starting full dataset generation with {self.total_steps} workflow steps"
            )

            # Setup database
            self.setup_database()

            # Execute workflow steps in dependency order
            remaining_steps = self.workflow_steps.copy()

            while remaining_steps:
                # Find steps that are ready to execute (dependencies satisfied)
                ready_steps = [
                    step for step in remaining_steps if self._check_dependencies(step)
                ]

                if not ready_steps:
                    # Check if we have any failed dependencies
                    failed_deps = [
                        step
                        for step in self.workflow_steps
                        if step.status == WorkflowStatus.FAILED
                    ]
                    if failed_deps:
                        raise Exception(
                            f"Cannot proceed due to failed dependencies: "
                            f"{[s.workflow_name for s in failed_deps]}"
                        )
                    else:
                        raise Exception(
                            "Circular dependency detected or no ready steps"
                        )

                # Execute ready steps (could be parallelized in the future)
                for step in ready_steps:
                    step_result = self._execute_workflow_step(step)

                    if not step_result.success:
                        raise Exception(
                            f"Workflow step '{step.workflow_name}' failed: "
                            f"{step_result.error_message}"
                        )

                    remaining_steps.remove(step)

            # Generate final dataset metadata
            metadata_batch = self.generate_batch(1)
            self.execute_batch(metadata_batch, is_first_batch=True)

            # Calculate totals
            total_records_generated = sum(
                step.result.records_generated
                for step in self.workflow_steps
                if step.result and step.result.success
            )

            total_records_stored = sum(
                step.result.records_stored
                for step in self.workflow_steps
                if step.result and step.result.success
            )

            result.status = WorkflowStatus.COMPLETED
            result.records_generated = total_records_generated
            result.records_stored = total_records_stored

            self.logger.info(
                f"Full dataset generation completed successfully: "
                f"{total_records_generated} total records generated across all workflows"
            )

        except Exception as e:
            result.status = WorkflowStatus.FAILED
            result.error_message = str(e)
            self.logger.error(f"Full dataset generation failed: {e}")

        finally:
            if self.conn:
                self.conn.close()

            result.execution_time = time.time() - start_time

        return result

    def get_execution_summary(self) -> Dict[str, Any]:
        """Get detailed summary of workflow execution."""
        summary = {
            "dataset_spec": {
                "people_count": self.dataset_spec.people_count,
                "companies_count": self.dataset_spec.companies_count,
            },
            "overall_progress": {
                "completed_steps": self.completed_steps,
                "total_steps": self.total_steps,
                "progress_percentage": (self.completed_steps / self.total_steps) * 100,
            },
            "workflow_steps": [],
        }

        total_duration = 0
        total_records = 0

        for step in self.workflow_steps:
            step_info = {
                "workflow_name": step.workflow_name,
                "target_records": step.target_records,
                "status": step.status.value,
                "duration": step.duration,
                "depends_on": step.depends_on,
            }

            if step.result:
                step_info.update(
                    {
                        "records_generated": step.result.records_generated,
                        "records_stored": step.result.records_stored,
                        "success": step.result.success,
                        "error_message": step.result.error_message,
                    }
                )

                if step.result.success:
                    total_records += step.result.records_generated

            summary["workflow_steps"].append(step_info)
            total_duration += step.duration

        summary["overall_stats"] = {
            "total_duration": total_duration,
            "total_records_generated": total_records,
            "average_records_per_second": (
                total_records / total_duration if total_duration > 0 else 0
            ),
        }

        return summary
