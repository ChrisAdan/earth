"""
DuckDB interface module for CRUD operations and database management.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Union, Optional, Any, Dict, List
from dataclasses import dataclass

import duckdb
import pandas as pd


@dataclass
class DatabaseConfig:
    """Configuration for DuckDB connection."""
    db_path: str = "earth.duckdb"
    schema_name: str = "raw"
    
    @classmethod
    def for_testing(cls, db_path: str = "earth_test.duckdb") -> "DatabaseConfig":
        """Create a test configuration."""
        return cls(db_path=db_path, schema_name="test")
    
    @classmethod
    def for_raw(cls, db_path: str = "earth.duckdb") -> "DatabaseConfig":
        """Create a raw/production configuration."""
        return cls(db_path=db_path, schema_name="raw")   

def setup_logging() -> logging.Logger:
    """Set up logging configuration."""
    # Create logs directory structure
    log_dir = Path("logs/loader")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("earth.loader")
    logger.setLevel(logging.INFO)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create file handler
    log_file = log_dir / f"loader_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def log(message: str, level: str = "info") -> None:
    """
    Utility function for logging messages.
    
    Args:
        message: Message to log
        level: Log level ('info', 'warning', 'error', 'debug')
    """
    logger = setup_logging()
    
    level_map = {
        "info": logger.info,
        "warning": logger.warning,
        "error": logger.error,
        "debug": logger.debug,
    }
    
    log_func = level_map.get(level.lower(), logger.info)
    log_func(message)


def connect_to_duckdb(config: Optional[DatabaseConfig] = None) -> duckdb.DuckDBPyConnection:
    """
    Create and return DuckDB connection to earth.duckdb.
    
    Args:
        config: Database configuration object
        
    Returns:
        DuckDB connection object
    """
    if config is None:
        config = DatabaseConfig()
    
    try:
        log(f"Connecting to DuckDB database: {config.db_path}")
        conn = duckdb.connect(config.db_path)
        
        # Create schema if it doesn't exist
        conn.execute(f"CREATE SCHEMA IF NOT EXISTS {config.schema_name}")
        log(f"Ensured schema '{config.schema_name}' exists")
        
        return conn
        
    except Exception as e:
        log(f"Failed to connect to DuckDB: {str(e)}", "error")
        raise


def operate_on_table(
    conn: duckdb.DuckDBPyConnection,
    schema_name: str,
    table_name: str,
    action: str,
    object_data: Optional[Union[pd.DataFrame,
                                List[Dict[str, Any]],
                                Dict[str, Any]]] = None,
    query: Optional[str] = None,
    how: str = "append"
) -> Union[bool, pd.DataFrame, None]:
    """
    Control database table operations based on action parameter.
    
    Args:
        conn: DuckDB connection object
        schema_name: Schema name
        table_name: Table name
        action: Action to perform ('ping', 'read', 'write', 'clear')
        object_data: Data object for write operations
        query: SQL query string for read operations
        how: Write method ('append' or 'truncate')
        
    Returns:
        - bool for 'ping' action
        - pd.DataFrame for 'read' action
        - None for 'write' and 'clear' actions
    """
    full_table_name = f"{schema_name}.{table_name}"
    
    try:
        if action == "ping":
            # Check if table exists
            try:
                result = conn.execute(
                    f"SELECT COUNT(*) FROM information_schema.tables "
                    f"WHERE table_schema = '{schema_name}' AND table_name = '{table_name}'"
                ).fetchone()
                exists = result[0] > 0 if result else False
                log(f"Table {full_table_name} exists: {exists}")
                return exists
            except Exception:
                log(f"Table {full_table_name} does not exist")
                return False
                
        elif action == "read":
            # Read data from table
            if query is None:
                query = f"SELECT * FROM {full_table_name}"
            
            log(f"Reading from {full_table_name} with query: {query}")
            df = conn.execute(query).df()
            log(f"Read {len(df)} rows from {full_table_name}")
            return df
            
        elif action == "write":
            # Write data to table
            if object_data is None:
                raise ValueError("object_data is required for write operations")
            
            # Convert data to DataFrame if needed
            if isinstance(object_data, dict):
                df = pd.DataFrame([object_data])
            elif isinstance(object_data, list):
                df = pd.DataFrame(object_data)
            elif isinstance(object_data, pd.DataFrame):
                df = object_data
            else:
                raise ValueError(f"Unsupported object_data type: {type(object_data)}")
            
            if how == "truncate":
                log(f"Truncating and writing {len(df)} rows to {full_table_name}")
                conn.execute(f"DROP TABLE IF EXISTS {full_table_name}")
            else:
                log(f"Appending {len(df)} rows to {full_table_name}")
            
            # Register DataFrame as temporary table and insert
            conn.register("temp_df", df)
            
            if how == "truncate" or not operate_on_table(conn, schema_name, table_name, "ping"):
                # Create table from DataFrame
                conn.execute(f"CREATE TABLE {full_table_name} AS SELECT * FROM temp_df")
            else:
                # Insert into existing table
                conn.execute(f"INSERT INTO {full_table_name} SELECT * FROM temp_df")
            
            conn.unregister("temp_df")
            log(f"Successfully wrote data to {full_table_name}")
            
        elif action == "clear":
            # Truncate table
            if operate_on_table(conn, schema_name, table_name, "ping"):
                conn.execute(f"DELETE FROM {full_table_name}")
                log(f"Cleared all data from {full_table_name}")
            else:
                log(f"Table {full_table_name} does not exist, nothing to clear")
                
        else:
            raise ValueError(f"Unknown action: {action}")
            
    except Exception as e:
        log(f"Error in operate_on_table: {str(e)}", "error")
        raise


def get_table_info(
    conn: duckdb.DuckDBPyConnection,
    schema_name: str,
    table_name: str
) -> Dict[str, Any]:
    """
    Get information about a table including row count and schema.
    
    Args:
        conn: DuckDB connection object
        schema_name: Schema name
        table_name: Table name
        
    Returns:
        Dictionary with table information
    """
    full_table_name = f"{schema_name}.{table_name}"
    
    if not operate_on_table(conn, schema_name, table_name, "ping"):
        return {"exists": False, "row_count": 0, "columns": []}
    
    try:
        # Get row count
        row_count = conn.execute(f"SELECT COUNT(*) FROM {full_table_name}").fetchone()[0]
        
        # Get column information
        columns = conn.execute(f"DESCRIBE {full_table_name}").df()
        
        return {
            "exists": True,
            "row_count": row_count,
            "columns": columns.to_dict("records")
        }
        
    except Exception as e:
        log(f"Error getting table info: {str(e)}", "error")
        return {"exists": False, "row_count": 0, "columns": []}