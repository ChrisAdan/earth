#!/usr/bin/env python3
"""
Earth Data Generator - Application Orchestrator

This is the main application entry point that orchestrates data generation workflows.
It imports from the earth package (src/earth/) to perform complex data generation tasks.

Usage:
    python app/main.py                    # Interactive menu
    python app/main.py --generate-people 150000
    python app/main.py --generate-companies
    python app/main.py --generate-all
"""

import argparse
import sys
from pathlib import Path

# Add src to path so we can import from earth package during development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import from earth package
from earth import generate_multiple_persons, check_module_availability, info as earth_info
from earth.core.loader import DuckDBLoader
from earth.core.utils import setup_logging

# Import application-specific workflows
from workflows.generate_people import PeopleWorkflow
# from workflows.generate_companies import CompaniesWorkflow  # Will be implemented
# from workflows.full_dataset import FullDatasetWorkflow    # Will be implemented


class EarthApp:
    """Main application orchestrator for Earth data generation."""
    
    def __init__(self):
        self.logger = setup_logging("earth_app")
        self.loader = DuckDBLoader()
        self.module_availability = check_module_availability()
        
    def show_banner(self):
        """Display application banner."""
        print("=" * 60)
        print("🌍 Earth Data Generator - Application Orchestrator")
        print("=" * 60)
        earth_info()
        print()
        
    def show_menu(self):
        """Display interactive menu."""
        print("📋 Available Operations:")
        print("1. Generate People (150k records)")
        print("2. Generate Companies" + (" ✅" if self.module_availability['companies'] else " ❌ (install earth[companies])"))
        print("3. Generate Campaigns" + (" ✅" if self.module_availability['campaigns'] else " ❌ (install earth[campaigns])"))
        print("4. Generate Automotive Data" + (" ✅" if self.module_availability['automotive'] else " ❌ (install earth[automotive])"))
        print("5. Generate Full Dataset" + (" ✅" if all(self.module_availability.values()) else " ❌ (install earth[all])"))
        print("6. Database Status")
        print("7. Clear Database")
        print("0. Exit")
        print()
        
    def generate_people_workflow(self, count: int = 150_000):
        """Execute people generation workflow."""
        self.logger.info(f"Starting people generation workflow: {count:,} records")
        
        workflow = PeopleWorkflow(self.loader, self.logger)
        success = workflow.execute(count)
        
        if success:
            print(f"✅ Successfully generated {count:,} person records")
            self.show_database_status()
        else:
            print("❌ People generation workflow failed")
            
    def generate_companies_workflow(self):
        """Execute companies generation workflow."""
        if not self.module_availability['companies']:
            print("❌ Companies module not available. Install with: pip install earth[companies]")
            return
            
        self.logger.info("Starting companies generation workflow")
        
        workflow = CompaniesWorkflow(self.loader, self.logger)
        success = workflow.execute()
        
        if success:
            print("✅ Successfully generated company records")
            self.show_database_status()
        else:
            print("❌ Companies generation workflow failed")
            
    def generate_full_dataset(self):
        """Generate complete dataset with all modules."""
        if not all(self.module_availability.values()):
            missing = [k for k, v in self.module_availability.items() if not v]
            print(f"❌ Missing modules: {', '.join(missing)}")
            print("Install all modules with: pip install earth[all]")
            return
            
        self.logger.info("Starting full dataset generation")
        
        workflow = FullDatasetWorkflow(self.loader, self.logger)
        success = workflow.execute()
        
        if success:
            print("✅ Successfully generated complete dataset")
            self.show_database_status()
        else:
            print("❌ Full dataset generation failed")
            
    def show_database_status(self):
        """Show current database status."""
        print("\n📊 Database Status:")
        
        try:
            # Check people table
            people_count = self.loader.execute_query("SELECT COUNT(*) FROM people").fetchone()[0]
            print(f"   People: {people_count:,} records")
        except:
            print("   People: Not found")
            
        # Check optional tables if modules are available
        if self.module_availability['companies']:
            try:
                companies_count = self.loader.execute_query("SELECT COUNT(*) FROM companies").fetchone()[0]
                print(f"   Companies: {companies_count:,} records")
            except:
                print("   Companies: Not found")
                
        if self.module_availability['campaigns']:
            try:
                campaigns_count = self.loader.execute_query("SELECT COUNT(*) FROM campaigns").fetchone()[0]
                print(f"   Campaigns: {campaigns_count:,} records")
            except:
                print("   Campaigns: Not found")
                
        if self.module_availability['automotive']:
            try:
                vehicles_count = self.loader.execute_query("SELECT COUNT(*) FROM vehicles").fetchone()[0]
                print(f"   Vehicles: {vehicles_count:,} records")
            except:
                print("   Vehicles: Not found")
        print()
        
    def clear_database(self):
        """Clear all database tables."""
        confirm = input("⚠️  Are you sure you want to clear all data? (yes/no): ")
        if confirm.lower() == 'yes':
            self.logger.info("Clearing database")
            # Implementation depends on your loader's capabilities
            try:
                self.loader.execute_query("DROP TABLE IF EXISTS people")
                self.loader.execute_query("DROP TABLE IF EXISTS companies")
                self.loader.execute_query("DROP TABLE IF EXISTS campaigns") 
                self.loader.execute_query("DROP TABLE IF EXISTS vehicles")
                print("✅ Database cleared")
            except Exception as e:
                print(f"❌ Error clearing database: {e}")
        else:
            print("Database clear cancelled")
            
    def interactive_mode(self):
        """Run in interactive menu mode."""
        self.show_banner()
        
        while True:
            self.show_menu()
            try:
                choice = input("Select option: ").strip()
                
                if choice == '0':
                    print("Goodbye! 👋")
                    break
                elif choice == '1':
                    count = input("Enter number of people to generate (default 150000): ").strip()
                    count = int(count) if count else 150_000
                    self.generate_people_workflow(count)
                elif choice == '2':
                    self.generate_companies_workflow()
                elif choice == '3':
                    print("Campaigns module coming in v0.3.0!")
                elif choice == '4':
                    print("Automotive module coming in v0.4.0!")
                elif choice == '5':
                    self.generate_full_dataset()
                elif choice == '6':
                    self.show_database_status()
                elif choice == '7':
                    self.clear_database()
                else:
                    print("Invalid option. Please try again.")
                    
            except KeyboardInterrupt:
                print("\n\nExiting... 👋")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
    def run_command_line(self, args):
        """Run with command line arguments."""
        if args.generate_people:
            self.generate_people_workflow(args.generate_people)
        elif args.generate_companies:
            self.generate_companies_workflow()
        elif args.generate_all:
            self.generate_full_dataset()
        elif args.status:
            self.show_database_status()
        else:
            print("No valid command specified. Use --help for options or run without args for interactive mode.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Earth Data Generator Application")
    
    # Generation commands
    parser.add_argument('--generate-people', type=int, metavar='N',
                       help='Generate N person records (default: 150000)')
    parser.add_argument('--generate-companies', action='store_true',
                       help='Generate company records')
    parser.add_argument('--generate-all', action='store_true', 
                       help='Generate complete dataset (requires all modules)')
    
    # Utility commands
    parser.add_argument('--status', action='store_true',
                       help='Show database status')
    parser.add_argument('--clear', action='store_true',
                       help='Clear database (interactive confirmation)')
                       
    args = parser.parse_args()
    
    # Create application instance
    app = EarthApp()
    
    # Run in appropriate mode
    if len(sys.argv) == 1:
        # No arguments - interactive mode
        app.interactive_mode()
    else:
        # Command line mode
        if args.clear:
            app.clear_database()
        else:
            app.run_command_line(args)


if __name__ == "__main__":
    main()