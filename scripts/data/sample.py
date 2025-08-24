#!/usr/bin/env python3
"""Generate sample data for testing and development."""

from argparse import ArgumentParser
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
    """Generate sample people data using quick generation."""
    try:
        from workflows import quick_generate_people

        print(f"👥 Generating {count} person records...")
        
        import time
        start_time = time.time()
        
        # Use the built-in quick generation function
        people_data = quick_generate_people(count=count, seed=42)
        
        execution_time = time.time() - start_time
        
        print(f"✅ Generated {len(people_data)} person records in {execution_time:.1f}s")
        
        if verbose:
            print(f"   Rate: {len(people_data) / execution_time:.0f} records/sec")
            print(f"   Sample record keys: {list(people_data[0].keys()) if people_data else 'None'}")
            
            # Show first record as example
            if people_data and len(people_data) > 0:
                print("   Sample person:")
                sample = people_data[0]
                print(f"     Name: {sample.get('first_name', 'N/A')} {sample.get('last_name', 'N/A')}")
                print(f"     Email: {sample.get('email', 'N/A')}")
                print(f"     Location: {sample.get('city', 'N/A')}, {sample.get('state', 'N/A')}")

    except Exception as e:
        print(f"❌ Error generating people data: {e}")
        sys.exit(1)


def generate_companies(count: int, verbose: bool = False) -> None:
    """Generate sample company data using quick generation."""
    try:
        from workflows import quick_generate_companies

        print(f"🏢 Generating {count} company records...")
        
        import time
        start_time = time.time()
        
        # Use the built-in quick generation function
        company_data = quick_generate_companies(count=count, seed=42)
        
        execution_time = time.time() - start_time
        
        print(f"✅ Generated {len(company_data)} company records in {execution_time:.1f}s")
        
        if verbose:
            print(f"   Rate: {len(company_data) / execution_time:.0f} records/sec")
            print(f"   Sample record keys: {list(company_data[0].keys()) if company_data else 'None'}")
            
            # Show first record as example
            if company_data and len(company_data) > 0:
                print("   Sample company:")
                sample = company_data[0]
                print(f"     Name: {sample.get('name', 'N/A')}")
                print(f"     Industry: {sample.get('industry', 'N/A')}")
                print(f"     Location: {sample.get('city', 'N/A')}, {sample.get('state', 'N/A')}")

    except Exception as e:
        print(f"❌ Error generating company data: {e}")
        sys.exit(1)


def generate_full_dataset(
    people_count: int = 100, 
    companies_count: int = 20, 
    verbose: bool = False,
    template: str = None
) -> None:
    """Generate a complete dataset using the quick generation function."""
    try:
        from workflows import quick_generate_full_dataset
        
        print(f"📊 Generating complete dataset...")
        if template:
            print(f"   Using template: {template}")
        else:
            print(f"   Custom counts - People: {people_count}, Companies: {companies_count}")
        
        import time
        start_time = time.time()
        
        # Use the built-in quick dataset generation function
        if template:
            dataset = quick_generate_full_dataset(template=template, seed=42)
        else:
            dataset = quick_generate_full_dataset(
                seed=42, 
                people=people_count, 
                companies=companies_count
            )
        
        execution_time = time.time() - start_time
        
        # Report results
        total_records = sum(len(records) for records in dataset.values())
        print(f"✅ Generated complete dataset in {execution_time:.1f}s")
        print(f"   Total records: {total_records}")
        
        for entity_type, records in dataset.items():
            print(f"   {entity_type}: {len(records)} records")
        
        if verbose:
            print(f"   Rate: {total_records / execution_time:.0f} records/sec")
            
            # Show sample records
            for entity_type, records in dataset.items():
                if records:
                    print(f"\n   Sample {entity_type}:")
                    sample = records[0]
                    if entity_type == 'person':
                        print(f"     Name: {sample.get('first_name', 'N/A')} {sample.get('last_name', 'N/A')}")
                        print(f"     Email: {sample.get('email', 'N/A')}")
                    elif entity_type == 'company':
                        print(f"     Name: {sample.get('name', 'N/A')}")
                        print(f"     Industry: {sample.get('industry', 'N/A')}")

    except Exception as e:
        print(f"❌ Error generating dataset: {e}")
        sys.exit(1)


def list_templates(verbose: bool = False) -> None:
    """List available dataset templates."""
    try:
        from workflows import list_dataset_templates, get_template_info
        
        templates = list_dataset_templates()
        print(f"📋 Available dataset templates ({len(templates)}):")
        
        for template_name in templates:
            if verbose:
                try:
                    info = get_template_info(template_name)
                    print(f"  • {template_name}: {info.get('description', 'No description')}")
                    workflows = info.get('workflows', {})
                    workflow_summary = ", ".join([f"{k}: {v}" for k, v in workflows.items()])
                    print(f"    [{workflow_summary}]")
                except Exception as e:
                    print(f"  • {template_name}: (error getting info - {e})")
            else:
                print(f"  • {template_name}")
                
    except Exception as e:
        print(f"❌ Error listing templates: {e}")
        sys.exit(1)


def show_system_info() -> None:
    """Show comprehensive system information."""
    try:
        from workflows import print_system_summary
        print_system_summary()
        
    except Exception as e:
        print(f"❌ Error showing system info: {e}")
        sys.exit(1)


def main():
    parser = ArgumentParser(description="Generate sample data using built-in quick functions")
    parser.add_argument(
        "--type",
        choices=["people", "companies", "dataset", "list-templates", "system-info"],
        required=True,
        help="Type of data to generate or action to perform",
    )
    parser.add_argument(
        "--count", 
        type=int, 
        help="Number of records to generate (for people/companies)"
    )
    parser.add_argument(
        "--people", 
        type=int, 
        default=100, 
        help="Number of people for dataset generation"
    )
    parser.add_argument(
        "--companies", 
        type=int, 
        default=20, 
        help="Number of companies for dataset generation"
    )
    parser.add_argument(
        "--template",
        type=str,
        help="Dataset template to use (overrides --people and --companies)"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Verbose output with sample data"
    )

    args = parser.parse_args()

    # Handle different action types
    if args.type == "people":
        count = args.count if args.count is not None else 100
        generate_people(count, args.verbose)
        
    elif args.type == "companies":
        count = args.count if args.count is not None else 20
        generate_companies(count, args.verbose)
        
    elif args.type == "dataset":
        generate_full_dataset(
            people_count=args.people,
            companies_count=args.companies,
            verbose=args.verbose,
            template=args.template
        )
        
    elif args.type == "list-templates":
        list_templates(args.verbose)
        
    elif args.type == "system-info":
        show_system_info()


if __name__ == "__main__":
    main()