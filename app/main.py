#!/usr/bin/env python3
"""
Earth Data Generator - Main Application Entry Point

Interactive CLI for generating synthetic person data and managing the Earth database.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd
from earth.loader import connect_to_duckdb, operate_on_table, get_table_info, log
from earth.generators.person import generate_multiple_persons


class EarthCLI:
    """Command-line interface for Earth data generator."""
    
    def __init__(self):
        self.conn = None
        self.schema_name = "raw"
        self.table_name = "persons"
        
    def initialize_database(self) -> None:
        """Initialize database connection and ensure schema exists."""
        try:
            self.conn = connect_to_duckdb()
            log("Database connection established successfully")
        except Exception as e:
            log(f"Failed to initialize database: {e}", "error")
            sys.exit(1)
    
    def get_user_input(self) -> tuple[int, str]:
        """
        Get user input for record generation preferences.
        
        Returns:
            Tuple of (record_count, action_choice)
        """
        print("\n" + "="*60)
        print("🌍 EARTH - Synthetic Data Generator")
        print("="*60)
        
        # Check existing data
        table_info = get_table_info(self.conn, self.schema_name, self.table_name)
        
        if table_info["exists"] and table_info["row_count"] > 0:
            print(f"\n📊 Current database status:")
            print(f"   • Table: {self.schema_name}.{self.table_name}")
            print(f"   • Existing records: {table_info['row_count']:,}")
            print(f"   • Columns: {len(table_info['columns'])}")
            
            print("\n🔄 Data Management Options:")
            print("   1. Append new records to existing data")
            print("   2. Replace all existing data with new records")
            
            while True:
                choice = input("\nSelect option (1 or 2): ").strip()
                if choice in ["1", "2"]:
                    action_choice = "append" if choice == "1" else "truncate"
                    break
                print("❌ Please enter 1 or 2")
        else:
            print(f"\n📊 Database status: New table will be created")
            action_choice = "truncate"  # First time setup
        
        # Get number of records to generate
        while True:
            try:
                count_input = input("\n📈 How many person records to generate? ").strip()
                record_count = int(count_input)
                if record_count <= 0:
                    print("❌ Please enter a positive number")
                    continue
                if record_count > 100000:
                    confirm = input(f"⚠️  Generating {record_count:,} records may take time. Continue? (y/N): ").strip().lower()
                    if confirm not in ["y", "yes"]:
                        continue
                break
            except ValueError:
                print("❌ Please enter a valid number")
        
        return record_count, action_choice
    
    def generate_and_store_data(self, count: int, how: str) -> None:
        """
        Generate person data and store in database.
        
        Args:
            count: Number of records to generate
            how: Write method ('append' or 'truncate')
        """
        print(f"\n🔄 Generating {count:,} person records...")
        
        try:
            # Generate data in batches for better memory management
            batch_size = min(1000, count)
            batches = (count + batch_size - 1) // batch_size
            
            total_generated = 0
            
            for batch_num in range(batches):
                current_batch_size = min(batch_size, count - total_generated)
                
                print(f"   Batch {batch_num + 1}/{batches}: Generating {current_batch_size} records...")
                
                # Generate batch of person profiles
                persons = generate_multiple_persons(current_batch_size)
                
                # Convert to DataFrame
                df = pd.DataFrame([person.to_dict() for person in persons])
                
                # Determine write method for this batch
                batch_how = how if batch_num == 0 else "append"
                
                # Store in database
                operate_on_table(
                    conn=self.conn,
                    schema_name=self.schema_name,
                    table_name=self.table_name,
                    action="write",
                    object_data=df,
                    how=batch_how
                )
                
                total_generated += current_batch_size
                
                # Progress update
                progress = (total_generated / count) * 100
                print(f"   Progress: {progress:.1f}% ({total_generated:,}/{count:,})")
            
            # Final status
            final_info = get_table_info(self.conn, self.schema_name, self.table_name)
            
            print(f"\n✅ Generation complete!")
            print(f"   • Total records in database: {final_info['row_count']:,}")
            print(f"   • Records added this session: {count:,}")
            print(f"   • Database file: earth.duckdb")
            
            # Show sample of generated data
            sample_df = operate_on_table(
                conn=self.conn,
                schema_name=self.schema_name,
                table_name=self.table_name,
                action="read",
                query=f"SELECT person_id, full_name, age, city, job_title FROM {self.schema_name}.{self.table_name} ORDER BY created_at DESC LIMIT 5"
            )
            
            print(f"\n📋 Sample of generated data:")
            print(sample_df.to_string(index=False))
            
        except Exception as e:
            log(f"Error during data generation: {e}", "error")
            print(f"❌ Error during generation: {e}")
            sys.exit(1)
    
    def display_database_stats(self) -> None:
        """Display comprehensive database statistics."""
        try:
            # Basic table info
            table_info = get_table_info(self.conn, self.schema_name, self.table_name)
            
            if not table_info["exists"]:
                print("\n📊 Database is empty - no person records found")
                return
            
            print(f"\n📊 Database Statistics:")
            print(f"   • Total persons: {table_info['row_count']:,}")
            
            # Age distribution
            age_stats = operate_on_table(
                conn=self.conn,
                schema_name=self.schema_name,
                table_name=self.table_name,
                action="read",
                query=f"SELECT MIN(age) as min_age, MAX(age) as max_age, AVG(age) as avg_age FROM {self.schema_name}.{self.table_name}"
            )
            
            if not age_stats.empty:
                print(f"   • Age range: {int(age_stats['min_age'].iloc[0])} - {int(age_stats['max_age'].iloc[0])} years")
                print(f"   • Average age: {age_stats['avg_age'].iloc[0]:.1f} years")
            
            # Gender distribution
            gender_dist = operate_on_table(
                conn=self.conn,
                schema_name=self.schema_name,
                table_name=self.table_name,
                action="read",
                query=f"SELECT gender, COUNT(*) as count FROM {self.schema_name}.{self.table_name} GROUP BY gender ORDER BY count DESC"
            )
            
            if not gender_dist.empty:
                print(f"   • Gender distribution:")
                for _, row in gender_dist.iterrows():
                    percentage = (row['count'] / table_info['row_count']) * 100
                    print(f"     - {row['gender']}: {row['count']:,} ({percentage:.1f}%)")
            
            # Top cities
            top_cities = operate_on_table(
                conn=self.conn,
                schema_name=self.schema_name,
                table_name=self.table_name,
                action="read",
                query=f"SELECT city, state, COUNT(*) as count FROM {self.schema_name}.{self.table_name} GROUP BY city, state ORDER BY count DESC LIMIT 5"
            )
            
            if not top_cities.empty:
                print(f"   • Top cities:")
                for _, row in top_cities.iterrows():
                    print(f"     - {row['city']}, {row['state']}: {row['count']} persons")
            
        except Exception as e:
            log(f"Error displaying stats: {e}", "error")
            print(f"❌ Error retrieving statistics: {e}")
    
    def run(self) -> None:
        """Main application runner."""
        print("Initializing Earth Data Generator...")
        
        # Initialize database
        self.initialize_database()
        
        # Get user preferences
        count, how = self.get_user_input()
        
        # Confirm generation
        action_text = "append to existing data" if how == "append" else "replace existing data"
        print(f"\n🚀 Ready to generate {count:,} records and {action_text}")
        confirm = input("Continue? (Y/n): ").strip().lower()
        
        if confirm in ["", "y", "yes"]:
            # Generate and store data
            self.generate_and_store_data(count, how)
            
            # Display final statistics
            self.display_database_stats()
            
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