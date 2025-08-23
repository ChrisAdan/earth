"""
Dataset orchestration system for coordinating multiple workflow executions.

This module provides a more flexible and scalable approach to generating
complete datasets by orchestrating multiple workflows based on specifications.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base import (
    BaseWorkflow,
    WorkflowConfig,
    WorkflowResult,
    WorkflowStatus,
    register_workflow,
)
from .config import AVAILABLE_WORKFLOWS
from .unified_workflow import UnifiedWorkflowRegistry
from earth.core.loader import DatabaseConfig
from earth.core.utils import (
    MIN_RATIO_PEOPLE_TO_COMPANIES,
    MAX_RATIO_PEOPLE_TO_COMPANIES,
)


class WorkflowStepStatus(Enum):
    """Status of individual workflow steps."""

    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """Individual workflow step in dataset generation."""

    workflow_name: str
    target_records: int
    depends_on: List[str] = field(default_factory=list)
    config_overrides: Dict[str, Any] = field(default_factory=dict)
    parallel_ok: bool = True  # Can this step run in parallel with others?

    # Runtime state (populated during execution)
    result: Optional[WorkflowResult] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    status: WorkflowStepStatus = WorkflowStepStatus.PENDING
    error_message: Optional[str] = None

    @property
    def duration(self) -> float:
        """Get execution duration in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0

    def mark_ready(self):
        """Mark this step as ready to execute."""
        self.status = WorkflowStepStatus.READY

    def mark_running(self):
        """Mark this step as currently running."""
        self.status = WorkflowStepStatus.RUNNING
        self.start_time = time.time()

    def mark_completed(self, result: WorkflowResult):
        """Mark this step as completed."""
        self.status = WorkflowStepStatus.COMPLETED
        self.result = result
        self.end_time = time.time()

    def mark_failed(self, error_message: str):
        """Mark this step as failed."""
        self.status = WorkflowStepStatus.FAILED
        self.error_message = error_message
        self.end_time = time.time()


# File: app/workflows/dataset_orchestrator.py - Updated DatasetSpec class

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base import (
    BaseWorkflow,
    WorkflowConfig,
    WorkflowResult,
    WorkflowStatus,
    register_workflow,
)
from .config import (
    AVAILABLE_WORKFLOWS,
    get_workflow_dependencies,
    validate_full_dataset_ratios,
)
from .unified_workflow import UnifiedWorkflowRegistry
from earth.core.loader import DatabaseConfig


@dataclass
class DatasetSpec:
    """Specification for dataset generation with dependency management."""

    # Primary way to specify workflows - this is the main interface
    workflows: Dict[str, int] = field(default_factory=dict)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)

    # Legacy support - will be converted to workflows dict
    people_count: Optional[int] = None
    companies_count: Optional[int] = None

    # Additional configuration
    parallel_groups: List[List[str]] = field(default_factory=list)
    description: str = "Custom dataset"

    # Validation rules
    min_ratio_people_to_companies: float = 5.0
    max_ratio_people_to_companies: float = 50.0

    def __post_init__(self):
        """Post-initialization to handle legacy parameters and set defaults."""
        # Handle legacy people_count/companies_count parameters
        if self.people_count is not None or self.companies_count is not None:
            if self.workflows:
                raise ValueError(
                    "Cannot specify both workflows dict and legacy people_count/companies_count"
                )

            # Convert legacy parameters to workflows dict
            if self.companies_count is not None:
                self.workflows["companies"] = self.companies_count
            if self.people_count is not None:
                self.workflows["people"] = self.people_count

            # Clear legacy parameters after conversion
            self.people_count = None
            self.companies_count = None

        # Set default dependencies if not specified
        if not self.dependencies and self.workflows:
            default_deps = get_workflow_dependencies()
            for workflow_name in self.workflows:
                if workflow_name in default_deps:
                    self.dependencies[workflow_name] = default_deps[workflow_name]

    @classmethod
    def from_template(cls, template_name: str) -> "DatasetSpec":
        """
        Create DatasetSpec from a predefined template.

        Args:
            template_name: Name of template from DATASET_TEMPLATES

        Returns:
            DatasetSpec instance
        """
        from .config import DATASET_TEMPLATES

        if template_name not in DATASET_TEMPLATES:
            available = list(DATASET_TEMPLATES.keys())
            raise ValueError(
                f"Unknown template '{template_name}'. Available: {available}"
            )

        template = DATASET_TEMPLATES[template_name]

        return cls(
            workflows=template["workflows"].copy(),
            dependencies=template.get("dependencies", {}).copy(),
            description=template["description"],
        )

    @classmethod
    def from_counts(cls, **workflow_counts) -> "DatasetSpec":
        """
        Create DatasetSpec from workflow counts.

        Args:
            **workflow_counts: Keyword arguments like people=1000, companies=100

        Returns:
            DatasetSpec instance
        """
        # Convert workflow counts to workflows dict
        workflows = {}
        for workflow_name, count in workflow_counts.items():
            if workflow_name in AVAILABLE_WORKFLOWS:
                workflows[workflow_name] = count
            else:
                available = list(AVAILABLE_WORKFLOWS.keys())
                raise ValueError(
                    f"Unknown workflow '{workflow_name}'. Available: {available}"
                )

        return cls(workflows=workflows)

    @classmethod
    def for_full_dataset(cls, **workflow_counts) -> "DatasetSpec":
        """
        Create DatasetSpec specifically for full dataset generation.
        Uses defaults if counts not provided.

        Args:
            **workflow_counts: Optional workflow counts (people=1000, companies=100, etc.)

        Returns:
            DatasetSpec instance with full dataset configuration
        """
        from .config import get_full_dataset_defaults

        # Start with defaults
        defaults = get_full_dataset_defaults()
        workflows = defaults["workflows"].copy()
        dependencies = defaults["dependencies"].copy()

        # Override with provided counts
        for workflow_name, count in workflow_counts.items():
            if workflow_name in AVAILABLE_WORKFLOWS:
                workflows[workflow_name] = count
            else:
                available = list(AVAILABLE_WORKFLOWS.keys())
                raise ValueError(
                    f"Unknown workflow '{workflow_name}'. Available: {available}"
                )

        return cls(
            workflows=workflows,
            dependencies=dependencies,
            description="Full synthetic dataset",
        )

    def validate(self) -> None:
        """Validate dataset specification."""
        if not self.workflows:
            raise ValueError("Must specify at least one workflow")

        for workflow_name, count in self.workflows.items():
            if count <= 0:
                raise ValueError(f"Record count must be positive for {workflow_name}")
            if workflow_name not in AVAILABLE_WORKFLOWS:
                supported_workflows = list(AVAILABLE_WORKFLOWS.keys())
                supported_workflows.remove(
                    "full_dataset"
                )  # full_dataset is not a leaf workflow
                raise ValueError(
                    f"Unknown workflow '{workflow_name}'. Available workflows: {supported_workflows}"
                )

        # Validate dependencies reference actual workflows
        for workflow_name, deps in self.dependencies.items():
            if workflow_name not in self.workflows:
                raise ValueError(
                    f"Dependency target '{workflow_name}' not in workflows"
                )
            for dep in deps:
                if dep not in self.workflows:
                    raise ValueError(f"Dependency '{dep}' not in workflows")

        # Check workflow ratios and warn if needed
        warnings = validate_full_dataset_ratios(self.workflows)
        if warnings:
            import warnings as warn_module

            for warning in warnings:
                warn_module.warn(warning, UserWarning)

    def get_total_records(self) -> int:
        """Get total number of records that will be generated."""
        return sum(self.workflows.values())

    def get_execution_order(self) -> List[List[str]]:
        """
        Get the execution order of workflows based on dependencies.

        Returns:
            List of workflow groups, where each group can be executed in parallel
        """
        # Build dependency graph
        remaining_workflows = set(self.workflows.keys())
        execution_groups = []

        while remaining_workflows:
            # Find workflows with no unmet dependencies
            ready_workflows = []
            for workflow in remaining_workflows:
                deps = self.dependencies.get(workflow, [])
                if all(dep not in remaining_workflows for dep in deps):
                    ready_workflows.append(workflow)

            if not ready_workflows:
                # Circular dependency or missing dependency
                remaining = list(remaining_workflows)
                raise ValueError(
                    f"Circular dependency detected or missing workflows: {remaining}"
                )

            execution_groups.append(ready_workflows)
            remaining_workflows -= set(ready_workflows)

        return execution_groups

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "workflows": self.workflows,
            "dependencies": self.dependencies,
            "description": self.description,
            "total_records": self.get_total_records(),
            "execution_order": self.get_execution_order(),
        }

    def __str__(self) -> str:
        """String representation."""
        workflows_str = ", ".join(
            [f"{name}: {count:,}" for name, count in self.workflows.items()]
        )
        return f"DatasetSpec({self.description}) - {workflows_str}"


class DatasetOrchestrator:
    """
    Orchestrates the execution of multiple workflows to generate complete datasets.

    This class handles dependency resolution, parallel execution where possible,
    and comprehensive progress tracking.
    """

    def __init__(
        self,
        dataset_spec: DatasetSpec,
        base_config: WorkflowConfig,
        db_config: Optional[DatabaseConfig] = None,
        max_parallel_workflows: int = 3,
    ):
        """
        Initialize dataset orchestrator.

        Args:
            dataset_spec: Specification for the dataset to generate
            base_config: Base configuration for all workflows
            db_config: Database configuration
            max_parallel_workflows: Maximum number of workflows to run in parallel
        """
        self.dataset_spec = dataset_spec
        self.dataset_spec.validate()

        self.base_config = base_config
        self.db_config = db_config or DatabaseConfig.for_dev()
        self.max_parallel_workflows = max_parallel_workflows

        self.logger = logging.getLogger("earth.orchestrator")

        # Build workflow steps
        self.workflow_steps = self._build_workflow_steps()
        self.execution_groups = self.dataset_spec.get_execution_order()

        # Execution state
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.overall_status = WorkflowStepStatus.PENDING

    def _build_workflow_steps(self) -> Dict[str, WorkflowStep]:
        """Build workflow steps from dataset specification."""
        steps = {}

        for workflow_name, target_records in self.dataset_spec.workflows.items():
            # Determine config overrides (first workflow should truncate)
            config_overrides = {}
            if workflow_name == list(self.dataset_spec.workflows.keys())[0]:
                config_overrides["write_mode"] = "truncate"
            else:
                config_overrides["write_mode"] = "append"

            step = WorkflowStep(
                workflow_name=workflow_name,
                target_records=target_records,
                depends_on=self.dataset_spec.dependencies.get(workflow_name, []),
                config_overrides=config_overrides,
            )

            steps[workflow_name] = step

        return steps

    def _execute_workflow_step(self, step: WorkflowStep) -> WorkflowResult:
        """
        Execute a single workflow step.

        Args:
            step: Workflow step to execute

        Returns:
            WorkflowResult from the step execution
        """
        self.logger.info(f"Starting workflow step: {step.workflow_name}")

        try:
            step.mark_running()

            # Create workflow configuration with overrides
            step_config = WorkflowConfig(
                batch_size=self.base_config.batch_size,
                max_records=self.base_config.max_records,
                seed=self.base_config.seed,
                write_mode=self.base_config.write_mode,
            )

            # Apply configuration overrides
            for key, value in step.config_overrides.items():
                setattr(step_config, key, value)

            # Create and execute the workflow
            workflow = UnifiedWorkflowRegistry.create_workflow(
                step.workflow_name, step_config, self.db_config
            )

            result = workflow.execute(step.target_records)

            if result.success:
                step.mark_completed(result)
                self.logger.info(
                    f"Completed workflow step: {step.workflow_name} "
                    f"({result.records_generated:,} records in {step.duration:.1f}s)"
                )
            else:
                step.mark_failed(result.error_message or "Unknown error")
                self.logger.error(
                    f"Failed workflow step: {step.workflow_name} - {result.error_message}"
                )

            return result

        except Exception as e:
            error_msg = str(e)
            step.mark_failed(error_msg)
            self.logger.error(f"Exception in workflow step {step.workflow_name}: {e}")

            return WorkflowResult(status=WorkflowStatus.FAILED, error_message=error_msg)

    def execute(self, use_parallel: bool = True) -> Dict[str, Any]:
        """
        Execute the complete dataset generation.

        Args:
            use_parallel: Whether to use parallel execution where possible

        Returns:
            Dictionary with execution results and statistics
        """
        self.start_time = time.time()
        self.overall_status = WorkflowStepStatus.RUNNING

        total_workflows = len(self.workflow_steps)
        completed_workflows = 0
        failed_workflows = 0

        try:
            self.logger.info(
                f"Starting dataset generation with {total_workflows} workflows "
                f"in {len(self.execution_groups)} execution groups"
            )

            # Execute workflow groups in order
            for group_idx, workflow_group in enumerate(self.execution_groups):
                group_size = len(workflow_group)
                self.logger.info(
                    f"Executing group {group_idx + 1}/{len(self.execution_groups)} "
                    f"with {group_size} workflows: {', '.join(workflow_group)}"
                )

                if use_parallel and group_size > 1:
                    # Execute group in parallel
                    completed_workflows += self._execute_group_parallel(workflow_group)
                else:
                    # Execute group sequentially
                    completed_workflows += self._execute_group_sequential(
                        workflow_group
                    )

                # Check if any workflows failed in this group
                group_failures = [
                    name
                    for name in workflow_group
                    if self.workflow_steps[name].status == WorkflowStepStatus.FAILED
                ]

                if group_failures:
                    failed_workflows += len(group_failures)
                    raise Exception(
                        f"Workflows failed in group {group_idx + 1}: {', '.join(group_failures)}"
                    )

            # All workflows completed successfully
            self.overall_status = WorkflowStepStatus.COMPLETED

        except Exception as e:
            self.overall_status = WorkflowStepStatus.FAILED
            self.logger.error(f"Dataset generation failed: {e}")

            # Count actual failures
            failed_workflows = sum(
                1
                for step in self.workflow_steps.values()
                if step.status == WorkflowStepStatus.FAILED
            )

        finally:
            self.end_time = time.time()

        return self.get_execution_summary()

    def _execute_group_sequential(self, workflow_group: List[str]) -> int:
        """Execute a group of workflows sequentially."""
        completed = 0

        for workflow_name in workflow_group:
            step = self.workflow_steps[workflow_name]
            result = self._execute_workflow_step(step)

            if result.success:
                completed += 1
            else:
                raise Exception(
                    f"Workflow '{workflow_name}' failed: {result.error_message}"
                )

        return completed

    def _execute_group_parallel(self, workflow_group: List[str]) -> int:
        """Execute a group of workflows in parallel."""
        completed = 0

        # Limit parallel execution
        max_workers = min(len(workflow_group), self.max_parallel_workflows)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all workflows in the group
            future_to_workflow = {
                executor.submit(
                    self._execute_workflow_step, self.workflow_steps[name]
                ): name
                for name in workflow_group
            }

            # Collect results
            for future in as_completed(future_to_workflow):
                workflow_name = future_to_workflow[future]

                try:
                    result = future.result()
                    if result.success:
                        completed += 1
                    else:
                        raise Exception(
                            f"Workflow '{workflow_name}' failed: {result.error_message}"
                        )

                except Exception as e:
                    # This will propagate up and stop the entire dataset generation
                    raise Exception(f"Workflow '{workflow_name}' crashed: {e}")

        return completed

    def get_execution_summary(self) -> Dict[str, Any]:
        """Get comprehensive execution summary."""
        total_duration = 0
        total_records = 0

        # Calculate totals
        for step in self.workflow_steps.values():
            total_duration += step.duration
            if step.result and step.result.success:
                total_records += step.result.records_generated

        # Overall duration (wall clock time)
        overall_duration = 0
        if self.start_time and self.end_time:
            overall_duration = self.end_time - self.start_time

        # Workflow step details
        step_details = []
        for step in self.workflow_steps.values():
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

            if step.error_message:
                step_info["error_message"] = step.error_message

            step_details.append(step_info)

        return {
            "dataset_spec": {
                "description": self.dataset_spec.description,
                "workflows": self.dataset_spec.workflows,
                "total_target_records": sum(self.dataset_spec.workflows.values()),
            },
            "execution_summary": {
                "overall_status": self.overall_status.value,
                "overall_duration": overall_duration,
                "total_workflow_time": total_duration,
                "time_saved_by_parallelism": max(0, total_duration - overall_duration),
                "total_records_generated": total_records,
                "execution_groups": self.execution_groups,
                "parallel_efficiency": (
                    total_duration / overall_duration if overall_duration > 0 else 1.0
                ),
            },
            "workflow_steps": step_details,
            "performance_metrics": {
                "average_records_per_second": (
                    total_records / overall_duration if overall_duration > 0 else 0
                ),
                "workflows_completed": sum(
                    1
                    for step in self.workflow_steps.values()
                    if step.status == WorkflowStepStatus.COMPLETED
                ),
                "workflows_failed": sum(
                    1
                    for step in self.workflow_steps.values()
                    if step.status == WorkflowStepStatus.FAILED
                ),
            },
        }


@register_workflow("dataset")
class DatasetWorkflow(BaseWorkflow):
    """
    Workflow wrapper around DatasetOrchestrator for consistency with BaseWorkflow interface.
    """

    def __init__(
        self,
        config: WorkflowConfig,
        db_config: Optional[DatabaseConfig] = None,
        dataset_spec: Optional[DatasetSpec] = None,
        **kwargs,
    ):
        """
        Initialize dataset workflow.

        Args:
            config: Base workflow configuration
            db_config: Database configuration
            dataset_spec: Dataset specification
            **kwargs: Additional arguments for orchestrator
        """
        super().__init__(config, db_config)

        if dataset_spec is None:
            # Default small dataset
            dataset_spec = DatasetSpec(
                workflows={"companies": 50, "people": 500},
                dependencies={"people": ["companies"]},
                description="Default dataset",
            )

        self.dataset_spec = dataset_spec
        self.orchestrator = DatasetOrchestrator(
            dataset_spec, config, db_config, **kwargs
        )

    @property
    def workflow_name(self) -> str:
        """Return the name of this workflow."""
        return f"Dataset Generation: {self.dataset_spec.description}"

    @property
    def schema_name(self) -> str:
        """Return the target schema name."""
        return "raw"

    @property
    def table_name(self) -> str:
        """Return the target table name."""
        return "dataset_metadata"

    def generate_batch(self, batch_size: int) -> List[Dict[str, Any]]:
        """Generate metadata batch about the dataset."""
        return [
            {
                "dataset_id": f"dataset_{int(time.time())}",
                "description": self.dataset_spec.description,
                "total_workflows": len(self.dataset_spec.workflows),
                "target_records": sum(self.dataset_spec.workflows.values()),
                "workflows": list(self.dataset_spec.workflows.keys()),
            }
        ]

    def execute(self, target_records: int = None) -> WorkflowResult:
        """
        Execute the dataset generation workflow.

        Args:
            target_records: Ignored for dataset workflows

        Returns:
            WorkflowResult with overall execution details
        """
        start_time = time.time()

        try:
            # Setup database connection for metadata
            self.setup_database()

            # Execute the orchestrator
            summary = self.orchestrator.execute()

            # Store metadata
            metadata_batch = self.generate_batch(1)
            self.execute_batch(metadata_batch, is_first_batch=True)

            # Build result based on orchestrator summary
            execution_summary = summary["execution_summary"]
            performance_metrics = summary["performance_metrics"]

            if execution_summary["overall_status"] == "completed":
                result = WorkflowResult(
                    status=WorkflowStatus.COMPLETED,
                    records_generated=execution_summary["total_records_generated"],
                    records_stored=execution_summary["total_records_generated"],
                    execution_time=time.time() - start_time,
                )

                self.logger.info(
                    f"Dataset generation completed successfully: "
                    f"{execution_summary['total_records_generated']:,} total records "
                    f"across {performance_metrics['workflows_completed']} workflows "
                    f"in {execution_summary['overall_duration']:.1f}s"
                )
            else:
                failed_count = performance_metrics["workflows_failed"]
                result = WorkflowResult(
                    status=WorkflowStatus.FAILED,
                    records_generated=execution_summary["total_records_generated"],
                    records_stored=execution_summary["total_records_generated"],
                    execution_time=time.time() - start_time,
                    error_message=f"{failed_count} workflow(s) failed during dataset generation",
                )

                self.logger.error(f"Dataset generation failed: {result.error_message}")

            return result

        except Exception as e:
            result = WorkflowResult(
                status=WorkflowStatus.FAILED,
                execution_time=time.time() - start_time,
                error_message=str(e),
            )
            self.logger.error(f"Dataset generation crashed: {e}")
            return result

        finally:
            if self.conn:
                self.conn.close()

    def get_execution_summary(self) -> Dict[str, Any]:
        """Get detailed execution summary from orchestrator."""
        return self.orchestrator.get_execution_summary()
