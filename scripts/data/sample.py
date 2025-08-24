#!/usr/bin/env python3
"""Generate sample data for testing and development."""

from argparse import ArgumentParser
from typing import Tuple, List, Any
import sys
from pathlib import Path

# Add src and app to path
sys.path.extend(
    [
        str(Path(__file__).parent.parent.parent / "src"),
        str(Path(__file__).parent.parent.parent / "app"),
    ]
)


def generate_people(count: int, verbose: bool = False) -> None:
    """Generate sample people data."""
    try:
        from workflows import quick_generate_people, WorkflowConfig, PeopleWorkflow, WorkflowResult
        from earth.core.loader import DatabaseConfig

        print(f"👥 Generating {count} person records...")

        config: WorkflowConfig = WorkflowConfig(
            batch_size=min(50, count), seed=42, write_mode="truncate"
        )
        workflow: PeopleWorkflow = PeopleWorkflow(config, DatabaseConfig.for_dev())

        result: WorkflowResult = workflow.execute(count)

        print(
            f"✅ Generated {result.records_generated} person records in {result.execution_time:.1f}s"
        )

        if verbose:
            print(f"   Batch size: {config.batch_size}")
            print(
                f"   Rate: {result.records_generated / result.execution_time:.0f} records/sec"
            )

    except Exception as e:
        print(f"❌ Error generating people data: {e}")
        sys.exit(1)


def generate_companies(count: int, verbose: bool = False) -> None:
    """Generate sample company data."""
    try:
        from workflows import WorkflowConfig, CompaniesWorkflow, WorkflowResult
        from earth.core.loader import DatabaseConfig

        print(f"🏢 Generating {count} company records...")

        config: WorkflowConfig = WorkflowConfig(
            batch_size=min(10, count), seed=42, write_mode="truncate"
        )
        workflow: CompaniesWorkflow = CompaniesWorkflow(
            config, DatabaseConfig.for_dev()
        )

        result: WorkflowResult = workflow.execute(count)

        print(
            f"✅ Generated {result.records_generated} company records in {result.execution_time:.1f}s"
        )

        if verbose:
            print(f"   Batch size: {config.batch_size}")
            print(
                f"   Rate: {result.records_generated / result.execution_time:.0f} records/sec"
            )

    except Exception as e:
        print(f"❌ Error generating company data: {e}")
        sys.exit(1)


def main():
    parser: ArgumentParser = ArgumentParser(description="Generate sample data")
    parser.add_argument(
        "--type",
        choices=["people", "companies", "dataset"],
        required=True,
        help="Type of data to generate",
    )
    parser.add_argument("--count", type=int, help="Number of records to generate")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args: Tuple[Any, List] = parser.parse_args()

    # Set default counts if not specified
    if args.count is None:
        defaults = {"people": 100, "companies": 20, "dataset": None}
        args.count = defaults[args.type]

    if args.type == "people":
        generate_people(args.count, args.verbose)
    elif args.type == "companies":
        generate_companies(args.count, args.verbose)
    elif args.type == "dataset":
        # Generate complete dataset
        generate_people(args.count or 100, args.verbose)
        generate_companies(args.count or 20, args.verbose)



if __name__ == "__main__":
    main()
