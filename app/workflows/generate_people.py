"""
People Generation Workflow

Handles the orchestration of generating large batches of person records.
This is your existing workflow that generates 150k+ people efficiently.
"""

import time
from typing import List, Optional
import pandas as pd

# Import from earth package
from earth import generate_multiple_persons, PersonProfile
from earth.core.loader import DuckDBLoader


class PeopleWorkflow:
    """Workflow for generating people data."""
    
    def __init__(self, loader: DuckDBLoader, logger):
        self.loader = loader
        self.logger = logger
        self.batch_size = 10_000  # Adjust based on memory constraints
        
    def create_people_table(self):
        """Create or recreate the people table."""
        create_sql = """
        CREATE OR REPLACE TABLE people (
            person_id VARCHAR PRIMARY KEY,
            first_name VARCHAR NOT NULL,
            last_name VARCHAR NOT NULL, 
            full_name VARCHAR NOT NULL,
            gender VARCHAR,
            date_of_birth DATE,
            age INTEGER,
            email VARCHAR,
            phone_number VARCHAR,
            ssn VARCHAR,
            street_address VARCHAR,
            city VARCHAR,
            state VARCHAR,
            zip_code VARCHAR,
            country VARCHAR,
            country_code VARCHAR,
            job_title VARCHAR,
            employment_status VARCHAR,
            annual_income INTEGER,
            username VARCHAR,
            ipv4_address VARCHAR,
            user_agent VARCHAR,
            blood_type VARCHAR,
            height_cm INTEGER,
            weight_kg INTEGER,
            marital_status VARCHAR,
            education_level VARCHAR,
            created_at TIMESTAMP,
            created_by VARCHAR
        )
        """
        
        self.loader.execute_query(create_sql)
        self.logger.info("Created people table")
        
    def generate_batch(self, batch_size: int, seed_offset: int = 0) -> List[PersonProfile]:
        """Generate a batch of person profiles."""
        self.logger.debug(f"Generating batch of {batch_size} people (seed offset: {seed_offset})")
        
        # Generate with different seeds to ensure variety
        people = generate_multiple_persons(
            count=batch_size,
            seed=seed_offset if seed_offset > 0 else None
        )
        
        return people
        
    def batch_to_dataframe(self, people: List[PersonProfile]) -> pd.DataFrame:
        """Convert batch of people to DataFrame for efficient loading."""
        records = []
        
        for person in people:
            record = person.to_dict()
            # Convert date objects to strings for DuckDB compatibility
            if record['date_of_birth']:
                record['date_of_birth'] = record['date_of_birth'].isoformat()
            if record['created_at']:
                record['created_at'] = record['created_at'].isoformat()
            records.append(record)
            
        return pd.DataFrame(records)
        
    def load_batch(self, df: pd.DataFrame):
        """Load a batch DataFrame into the database."""
        self.loader.load_dataframe(df, 'people')
        
    def execute(self, total_count: int) -> bool:
        """
        Execute the people generation workflow.
        
        Args:
            total_count: Total number of people to generate
            
        Returns:
            bool: Success status
        """
        start_time = time.time()
        
        try:
            # Create table
            self.logger.info(f"Starting people generation workflow: {total_count:,} records")
            self.create_people_table()
            
            # Calculate batching
            full_batches = total_count // self.batch_size
            remaining = total_count % self.batch_size
            
            self.logger.info(f"Processing {full_batches} full batches of {self.batch_size:,} + {remaining} remaining")
            
            generated_count = 0
            
            # Process full batches
            for batch_num in range(full_batches):
                batch_start = time.time()
                
                # Generate batch
                people = self.generate_batch(self.batch_size, seed_offset=batch_num * 100)
                
                # Convert to DataFrame
                df = self.batch_to_dataframe(people)
                
                # Load to database
                self.load_batch(df)
                
                generated_count += len(people)
                batch_time = time.time() - batch_start
                
                # Progress logging
                progress = (generated_count / total_count) * 100
                rate = len(people) / batch_time
                
                self.logger.info(
                    f"Batch {batch_num + 1}/{full_batches} complete: "
                    f"{generated_count:,}/{total_count:,} ({progress:.1f}%) "
                    f"- {rate:.0f} records/sec"
                )
                
            # Process remaining records
            if remaining > 0:
                batch_start = time.time()
                
                people = self.generate_batch(remaining, seed_offset=full_batches * 100)
                df = self.batch_to_dataframe(people)
                self.load_batch(df)
                
                generated_count += len(people)
                batch_time = time.time() - batch_start
                rate = len(people) / batch_time
                
                self.logger.info(
                    f"Final batch complete: {generated_count:,}/{total_count:,} (100.0%) "
                    f"- {rate:.0f} records/sec"
                )
                
            # Final statistics
            total_time = time.time() - start_time
            overall_rate = generated_count / total_time
            
            self.logger.info(
                f"People generation workflow complete: "
                f"{generated_count:,} records in {total_time:.1f}s "
                f"({overall_rate:.0f} records/sec average)"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"People generation workflow failed: {e}")
            return False
            
    def get_statistics(self) -> dict:
        """Get statistics about generated people data."""
        try:
            stats_query = """
            SELECT 
                COUNT(*) as total_count,
                COUNT(DISTINCT gender) as unique_genders,
                COUNT(DISTINCT state) as unique_states,
                COUNT(DISTINCT job_title) as unique_job_titles,
                AVG(age) as avg_age,
                AVG(annual_income) as avg_income,
                MIN(created_at) as earliest_created,
                MAX(created_at) as latest_created
            FROM people
            """
            
            result = self.loader.execute_query(stats_query).fetchone()
            
            return {
                'total_count': result[0],
                'unique_genders': result[1], 
                'unique_states': result[2],
                'unique_job_titles': result[3],
                'avg_age': round(result[4], 1) if result[4] else None,
                'avg_income': round(result[5], 0) if result[5] else None,
                'earliest_created': result[6],
                'latest_created': result[7]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting people statistics: {e}")
            return {}
            
    def validate_data(self) -> dict:
        """Validate the generated people data."""
        validation_results = {
            'duplicate_ids': 0,
            'missing_required_fields': 0,
            'invalid_emails': 0,
            'invalid_ages': 0,
            'data_quality_score': 0.0
        }
        
        try:
            # Check for duplicate IDs
            duplicate_query = """
            SELECT COUNT(*) - COUNT(DISTINCT person_id) as duplicates
            FROM people
            """
            validation_results['duplicate_ids'] = self.loader.execute_query(duplicate_query).fetchone()[0]
            
            # Check for missing required fields
            missing_query = """
            SELECT COUNT(*) 
            FROM people 
            WHERE first_name IS NULL 
               OR last_name IS NULL 
               OR email IS NULL 
               OR age IS NULL
            """
            validation_results['missing_required_fields'] = self.loader.execute_query(missing_query).fetchone()[0]
            
            # Check for invalid ages
            invalid_age_query = """
            SELECT COUNT(*) 
            FROM people 
            WHERE age < 18 OR age > 100
            """
            validation_results['invalid_ages'] = self.loader.execute_query(invalid_age_query).fetchone()[0]
            
            # Calculate data quality score
            total_records = self.loader.execute_query("SELECT COUNT(*) FROM people").fetchone()[0]
            
            if total_records > 0:
                issues = (validation_results['duplicate_ids'] + 
                         validation_results['missing_required_fields'] + 
                         validation_results['invalid_ages'])
                validation_results['data_quality_score'] = ((total_records - issues) / total_records) * 100
                
        except Exception as e:
            self.logger.error(f"Error validating people data: {e}")
            
        return validation_results