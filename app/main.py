#!/usr/bin/env python3
"""
Earth Data Generator - Main Application Entry Point

Interactive CLI for generating synthetic data using the new workflow system.
Enhanced to support multiple workflow types and scalable entity generation.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any

# Add src to path for package imports
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root / "src"))

# Import from earth package
from earth.core.loader import (
    DatabaseConfig,
    connect_to_duckdb,
    get_table_info,
    log,
)

# Import workflow system from app layer
from workflows import (
    WorkflowConfig,
    DatasetSpec,
    AVAILABLE_WORKFLOWS,
    get_workflow_info,
    create_workflow_from_name,
)


class EarthCLI:
    """Enhanced command-line interface for Earth data generator with workflow support."""

    def __init__(self):
        self.conn = None
        self.db_config = DatabaseConfig.for_dev()

    def initialize_database(self) -> None:
        """Initialize database connection and ensure schemas exist."""
        try:
            self.conn = connect_to_duckdb(self.db_config)
            log("Database connection established successfully")
        except Exception as e:
            log(f"Failed to initialize database: {e}", "error")
            sys.exit(1)

    def display_welcome(self) -> None:
        """Display welcome message and available workflows."""
        print("\n" + "=" * 70)
        print("🌍 EARTH - Synthetic Data Generator")
        print("=" * 70)
        print("\n📋 Available Data Generation Workflows:")

        for i, (name, info) in enumerate(AVAILABLE_WORKFLOWS.items(), 1):
            print(f"   {i}. {name.replace('_', ' ').title()}")
            print(f"      {info['description']}")
            if info["default_count"]:
                print(f"      Default records: {info['default_count']:,}")
            print()

    def get_workflow_choice(self) -> str:
        """Get user's workflow choice."""
        workflows = list(AVAILABLE_WORKFLOWS.keys())

        while True:
            print("🔄 Select a workflow:")
            for i, name in enumerate(workflows, 1):
                display_name = name.replace("_", " ").title()
                print(f"   {i}. {display_name}")

            try:
                choice = input(f"\nEnter choice (1-{len(workflows)}): ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(workflows):
                    return workflows[idx]
                else:
                    print(f"❌ Please enter a number between 1 and {len(workflows)}")
            except ValueError:
                print("❌ Please enter a valid number")

    def get_workflow_parameters(self, workflow_name: str) -> tuple:
        """
        Get workflow-specific parameters from user.

        Returns:
            Tuple of (record_count_or_spec, write_mode)
        """
        workflow_info = get_workflow_info(workflow_name)

        if workflow_name == "full_dataset":
            return self._get_full_dataset_parameters()
        else:
            return self._get_single_workflow_parameters(workflow_name, workflow_info)

    def _get_full_dataset_parameters(self) -> tuple:
        """Get parameters for full dataset generation."""
        print("\n📊 Full Dataset Configuration:")
        print(
            "   This will generate a complete synthetic dataset with multiple entity types"
        )

        # Check existing data across all tables
        tables_to_check = ["persons", "companies"]
        existing_data = {}

        for table in tables_to_check:
            table_info = get_table_info(self.conn, "raw", table)
            if table_info["exists"] and table_info["row_count"] > 0:
                existing_data[table] = table_info["row_count"]

        if existing_data:
            print(f"\n📈 Existing data found:")
            for table, count in existing_data.items():
                print(f"   • {table}: {count:,} records")

            print("\n🔄 Data Management Options:")
            print("   1. Replace all existing data with new dataset")
            print("   2. Cancel and run individual workflows instead")

            while True:
                choice = input("\nSelect option (1 or 2): ").strip()
                if choice == "1":
                    write_mode = "truncate"
                    break
                elif choice == "2":
                    print(
                        "💡 Tip: Choose 'people' or 'companies' workflow for individual entity generation"
                    )
                    return None, None
                else:
                    print("❌ Please enter 1 or 2")
        else:
            write_mode = "truncate"

        # Get dataset specifications
        print(f"\n📋 Dataset Size Configuration:")

        # People count
        while True:
            try:
                people_input = input(
                    "Number of people to generate (default: 1000): "
                ).strip()
                people_count = int(people_input) if people_input else 1000
                if people_count <= 0:
                    print("❌ Please enter a positive number")
                    continue
                break
            except ValueError:
                print("❌ Please enter a valid number")

        # Companies count
        while True:
            try:
                companies_input = input(
                    "Number of companies to generate (default: 100): "
                ).strip()
                companies_count = int(companies_input) if companies_input else 100
                if companies_count <= 0:
                    print("❌ Please enter a positive number")
                    continue
                break
            except ValueError:
                print("❌ Please enter a valid number")

        # Validate ratio
        ratio = people_count / companies_count
        if ratio < 5 or ratio > 50:
            print(f"⚠️  Warning: People-to-companies ratio is {ratio:.1f}")
            print(f"   Realistic range is 5-50 people per company")
            confirm = input("Continue anyway? (y/N): ").strip().lower()
            if confirm not in ["y", "yes"]:
                return self._get_full_dataset_parameters()  # Restart

        dataset_spec = DatasetSpec(
            people_count=people_count, companies_count=companies_count
        )

        return dataset_spec, write_mode

    def _get_single_workflow_parameters(
        self, workflow_name: str, workflow_info: dict
    ) -> tuple:
        """Get parameters for single workflow generation."""
        schema_name = workflow_info["schema"]
        table_name = workflow_info["table"]
        default_count = workflow_info["default_count"]

        # Check existing data
        table_info = get_table_info(self.conn, schema_name, table_name)

        if table_info["exists"] and table_info["row_count"] > 0:
            print(f"\n📊 Current {workflow_name} data:")
            print(f"   • Table: {schema_name}.{table_name}")
            print(f"   • Existing records: {table_info['row_count']:,}")

            print("\n🔄 Data Management Options:")
            print("   1. Append new records to existing data")
            print("   2. Replace all existing data with new records")

            while True:
                choice = input("\nSelect option (1 or 2): ").strip()
                if choice in ["1", "2"]:
                    write_mode = "append" if choice == "1" else "truncate"
                    break
                print("❌ Please enter 1 or 2")
        else:
            print(
                f"\n📊 {workflow_name.title()} generation - new table will be created"
            )
            write_mode = "truncate"

        # Get record count
        while True:
            try:
                prompt = f"\n📈 How many {workflow_name} records to generate"
                if default_count:
                    prompt += f" (default: {default_count:,})"
                prompt += "? "

                count_input = input(prompt).strip()
                record_count = int(count_input) if count_input else default_count

                if record_count <= 0:
                    print("❌ Please enter a positive number")
                    continue
                if record_count > 100000:
                    confirm = (
                        input(
                            f"⚠️  Generating {record_count:,} records may take time. Continue? (y/N): "
                        )
                        .strip()
                        .lower()
                    )
                    if confirm not in ["y", "yes"]:
                        continue
                break
            except ValueError:
                print("❌ Please enter a valid number")

        return record_count, write_mode

    def execute_workflow(
        self, workflow_name: str, parameters: Any, write_mode: str
    ) -> None:
        """Execute the selected workflow with given parameters."""
        try:
            # Create workflow configuration
            config = WorkflowConfig(
                batch_size=1000,
                max_records=1000000,
                seed=42,  # For reproducible results
                write_mode=write_mode,
            )

            # Create and execute workflow
            if workflow_name == "full_dataset":
                dataset_spec = parameters
                workflow = create_workflow_from_name(
                    workflow_name, config, self.db_config, dataset_spec=dataset_spec
                )

                print(f"\n🚀 Starting full dataset generation...")
                print(f"   • People: {dataset_spec.people_count:,}")
                print(f"   • Companies: {dataset_spec.companies_count:,}")

                result = workflow.execute()

                if result.success:
                    summary = workflow.get_execution_summary()
                    self._display_full_dataset_results(summary)
                else:
                    print(f"❌ Full dataset generation failed: {result.error_message}")

            else:
                record_count = parameters
                workflow = create_workflow_from_name(
                    workflow_name, config, self.db_config
                )

                action_text = (
                    "appending to existing data"
                    if write_mode == "append"
                    else "replacing existing data"
                )
                print(f"\n🚀 Starting {workflow_name} generation...")
                print(f"   • Records: {record_count:,}")
                print(f"   • Mode: {action_text}")

                result = workflow.execute(record_count)

                if result.success:
                    self._display_single_workflow_results(
                        workflow_name, result, workflow
                    )
                else:
                    print(
                        f"❌ {workflow_name} generation failed: {result.error_message}"
                    )

        except Exception as e:
            log(f"Error executing workflow: {e}", "error")
            print(f"❌ Workflow execution error: {e}")

    def _display_single_workflow_results(
        self, workflow_name: str, result, workflow
    ) -> None:
        """Display results for single workflow execution."""
        print(f"\n✅ {workflow_name.title()} generation complete!")
        print(f"   • Records generated: {result.records_generated:,}")
        print(f"   • Records stored: {result.records_stored:,}")
        print(f"   • Execution time: {result.execution_time:.1f} seconds")
        print(
            f"   • Rate: {result.records_generated/result.execution_time:.0f} records/second"
        )

        # Show statistics if available
        if hasattr(workflow, "get_statistics"):
            try:
                # Reconnect for statistics (workflow closes connection)
                workflow.conn = connect_to_duckdb(self.db_config)
                stats = workflow.get_statistics()
                if stats:
                    self._display_workflow_statistics(workflow_name, stats)
            except Exception as e:
                log(f"Error getting statistics: {e}", "warning")

    def _display_full_dataset_results(self, summary: Dict[str, Any]) -> None:
        """Display results for full dataset generation."""
        print(f"\n✅ Full dataset generation complete!")

        overall_stats = summary["overall_stats"]
        print(f"   • Total records: {overall_stats['total_records_generated']:,}")
        print(f"   • Total time: {overall_stats['total_duration']:.1f} seconds")
        print(
            f"   • Average rate: {overall_stats['average_records_per_second']:.0f} records/second"
        )

        print(f"\n📊 Workflow breakdown:")
        for step in summary["workflow_steps"]:
            status_icon = "✅" if step["success"] else "❌"
            print(
                f"   {status_icon} {step['workflow_name'].title()}: "
                f"{step['records_generated']:,} records in {step['duration']:.1f}s"
            )

    def _display_workflow_statistics(
        self, workflow_name: str, stats: Dict[str, Any]
    ) -> None:
        """Display detailed workflow statistics."""
        print(f"\n📈 {workflow_name.title()} Statistics:")

        if "basic_stats" in stats and stats["basic_stats"]:
            basic = stats["basic_stats"]
            for key, value in basic.items():
                if isinstance(value, (int, float)):
                    if key.endswith("_count") or key.startswith("total_"):
                        print(f"   • {key.replace('_', ' ').title()}: {value:,}")
                    elif "avg" in key:
                        print(f"   • {key.replace('_', ' ').title()}: {value:.1f}")
                    else:
                        print(f"   • {key.replace('_', ' ').title()}: {value}")

        # Show top distributions
        for dist_key in [
            "gender_distribution",
            "industry_distribution",
            "size_distribution",
        ]:
            if dist_key in stats and stats[dist_key]:
                dist_name = dist_key.replace("_distribution", "").title()
                print(f"\n   Top {dist_name}s:")
                for item in stats[dist_key][:5]:  # Top 5
                    name_key = [k for k in item.keys() if k != "count"][0]
                    print(f"     - {item[name_key]}: {item['count']:,}")

    def run(self) -> None:
        """Main application runner with enhanced workflow support."""
        print("Initializing Earth Data Generator...")

        # Initialize database
        self.initialize_database()

        # Display welcome and workflow options
        self.display_welcome()

        # Get user's workflow choice
        workflow_name = self.get_workflow_choice()

        # Get workflow-specific parameters
        parameters, write_mode = self.get_workflow_parameters(workflow_name)

        if parameters is None:  # User cancelled
            print("❌ Operation cancelled by user")
            return

        # Confirm execution
        if workflow_name == "full_dataset":
            dataset_spec = parameters
            print(f"\n🚀 Ready to generate full dataset:")
            print(f"   • People: {dataset_spec.people_count:,}")
            print(f"   • Companies: {dataset_spec.companies_count:,}")
            print(f"   • Mode: {write_mode}")
        else:
            record_count = parameters
            action_text = (
                "append to existing data"
                if write_mode == "append"
                else "replace existing data"
            )
            print(
                f"\n🚀 Ready to generate {record_count:,} {workflow_name} records and {action_text}"
            )

        confirm = input("Continue? (Y/n): ").strip().lower()

        if confirm in ["", "y", "yes"]:
            # Execute the workflow
            self.execute_workflow(workflow_name, parameters, write_mode)

            print(f"\n🎉 Earth data generation complete!")
            print(f"   Database location: {os.path.abspath('earth.duckdb')}")
            print(f"   Logs location: {os.path.abspath('logs/loader/')}")
        else:
            print("❌ Generation cancelled by user")

        # Close connection
        if self.conn:
            self.conn.close()
            log("Database connection closed")


def main() -> None:
    """Main entry point."""
    try:
        cli = EarthCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n\n❌ Generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        log(f"Unexpected error in main: {e}", "error")
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
