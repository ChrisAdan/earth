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


def operate_on_table(
    conn: duckdb.DuckDBPyConnection,
    schema_name: str,
    table_name: str,
    action: str,
    object_data: Optional[
        Union[pd.DataFrame, List[Dict[str, Any]], Dict[str, Any]]
    ] = None,
    query: Optional[str] = None,
    how: str = "append",
) -> Union[
    bool,
    pd.DataFrame,
    None,
]:
    """
    Control database table operations based on action parameter.

    Args:
        conn: DuckDB connection object
        schema_name: Schema name
        table_name: Table name
        action: Action to perform ('ping', 'read', 'write', 'clear', 'drop')
        object_data: Data object for write operations
        query: SQL query string for read operations
        how: Write method ('append' or 'truncate')

    Returns:
        - bool for 'ping' action
        - pd.DataFrame for 'read' action
        - None for 'write' and 'clear' or 'drop' actions
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
                df = object_data.copy()  # Make a copy to avoid modifying original
            else:
                raise ValueError(f"Unsupported object_data type: {type(object_data)}")

            # **FIX: Prepare DataFrame with explicit types for DuckDB**
            df = _prepare_dataframe_for_duckdb(df)

            if how == "truncate":
                log(f"Truncating and writing {len(df)} rows to {full_table_name}")
                conn.execute(f"DROP TABLE IF EXISTS {full_table_name}")
            else:
                log(f"Appending {len(df)} rows to {full_table_name}")

            # **FIX: Use explicit table creation with proper column types**
            if how == "truncate" or not operate_on_table(
                conn, schema_name, table_name, "ping"
            ):
                # Create table with explicit schema to prevent type inference issues
                _create_table_with_explicit_schema(conn, full_table_name, df)

            # **FIX: Use pandas to_sql with explicit dtype mapping**
            _write_dataframe_to_duckdb(conn, df, schema_name, table_name, how)

            log(f"Successfully wrote data to {full_table_name}")
            return None

        elif action == "clear":
            # Truncate table
            if operate_on_table(conn, schema_name, table_name, "ping"):
                conn.execute(f"DELETE FROM {full_table_name}")
                log(f"Cleared all data from {full_table_name}")
            else:
                log(f"Table {full_table_name} does not exist, nothing to clear")
            return None
        elif action == "drop":
            try:
                conn.execute(f"DROP TABLE {full_table_name}")
                log(f"Dropped {full_table_name}")
            except Exception as e:
                print(f"Failed to drop {full_table_name}: {str(e)}")
                return None
        else:
            raise ValueError(f"Unknown action: {action}")
        return None

    except Exception as e:
        log(f"Error in operate_on_table: {str(e)}", "error")
        raise


def _prepare_dataframe_for_duckdb(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare DataFrame for DuckDB by ensuring proper column types.

    This prevents DuckDB from incorrectly inferring types, especially
    for string columns that contain numeric-looking values.
    """
    df_prepared = df.copy()

    # Force specific columns to remain as strings
    string_columns = [
        "person_id",
        "company_id",
        "customer_id",
        "product_id",  # ID fields
        "stock_symbol",
        "ticker_symbol",  # Stock symbols
        "phone",
        "mobile_phone",
        "work_phone",
        "fax",  # Phone numbers
        "zip_code",
        "postal_code",
        "zipcode",  # Postal codes
        "ssn",
        "tax_id",
        "ein",  # Government IDs
        "account_number",
        "routing_number",  # Financial numbers
        "vin",
        "license_plate",  # Vehicle identifiers
        "confirmation_code",
        "reference_number",  # Codes
    ]

    # Also check for columns ending with common ID patterns
    id_patterns = ["_id", "_code", "_number", "_symbol"]

    for column in df_prepared.columns:
        column_lower = column.lower()

        # Check if column should be treated as string
        should_be_string = (
            column_lower in [col.lower() for col in string_columns]
            or any(column_lower.endswith(pattern) for pattern in id_patterns)
            or column_lower in ["phone", "mobile", "fax", "zip", "postal"]
        )

        if should_be_string and column in df_prepared.columns:
            # Convert to pandas string type (better than object for DuckDB)
            if df_prepared[column].dtype == "object":
                # Only convert if it's not already a string type
                df_prepared[column] = df_prepared[column].astype("string")
    return df_prepared


def _get_duckdb_column_type(series: pd.Series) -> str:
    """
    Get appropriate DuckDB column type for a pandas Series.
    """
    dtype = series.dtype

    # Handle pandas extension types
    if pd.api.types.is_string_dtype(series):
        return "VARCHAR"
    elif pd.api.types.is_integer_dtype(series):
        return "BIGINT"
    elif pd.api.types.is_float_dtype(series):
        return "DOUBLE"
    elif pd.api.types.is_bool_dtype(series):
        return "BOOLEAN"
    elif pd.api.types.is_datetime64_any_dtype(series):
        return "TIMESTAMP"
    elif dtype == "object":
        # For object dtype, check the actual values
        non_null = series.dropna()
        if len(non_null) > 0:
            first_val = non_null.iloc[0]
            if isinstance(first_val, str):
                return "VARCHAR"
            elif isinstance(first_val, (int, float)):
                return "DOUBLE"
            else:
                return "VARCHAR"  # Default to VARCHAR for unknown object types
        else:
            return "VARCHAR"
    else:
        return "VARCHAR"  # Default fallback


def _create_table_with_explicit_schema(
    conn: duckdb.DuckDBPyConnection, full_table_name: str, df: pd.DataFrame
) -> None:
    """
    Create table with explicit column types to prevent DuckDB type inference issues.
    """
    _ensure_schema_exists(conn, full_table_name.split(".")[0])
    # Build CREATE TABLE statement with explicit column types
    column_definitions = []

    for column in df.columns:
        duckdb_type = _get_duckdb_column_type(df[column])
        # Escape column names that might be reserved words
        escaped_column = (
            f'"{column}"' if column.lower() in ["order", "group", "select"] else column
        )
        column_definitions.append(f"{escaped_column} {duckdb_type}")

    create_sql = f"CREATE TABLE {full_table_name} ({', '.join(column_definitions)})"

    conn.execute(create_sql)


def _write_dataframe_to_duckdb(
    conn: duckdb.DuckDBPyConnection,
    df: pd.DataFrame,
    schema_name: str,
    table_name: str,
    how: str,
) -> None:
    """
    Write DataFrame to DuckDB using the safest method to preserve types.
    """
    # Register the DataFrame as a temporary table
    temp_table_name = f"temp_df_{table_name}_{id(df)}"
    conn.register(temp_table_name, df)

    try:
        full_table_name = f"{schema_name}.{table_name}"

        if how == "truncate":
            # For truncate, we've already created the table with explicit schema
            conn.execute(
                f"INSERT INTO {full_table_name} SELECT * FROM {temp_table_name}"
            )
        else:
            # For append, insert into existing table
            conn.execute(
                f"INSERT INTO {full_table_name} SELECT * FROM {temp_table_name}"
            )

    finally:
        # Always clean up the temporary table
        try:
            conn.unregister(temp_table_name)
        except Exception as e:
            log(
                f"Warning: Could not unregister temporary table {temp_table_name}: {e}",
                "warning",
            )


# Keep the rest of your existing functions unchanged
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
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
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


@dataclass
class DatabaseConfig:
    """Configuration for DuckDB connection."""

    data_dir: Path = Path("data")
    env: str = "dev"
    schema_name: str = "raw"

    @property
    def db_filename(self) -> Path:
        """Generate the database filename based on environment"""
        return Path(f"earth_{self.env}")

    @property
    def db_path(self) -> Path:
        """Generate database path based on environment."""
        return self.data_dir / self.env / f"{self.db_filename}.duckdb"

    def __post_init__(self) -> None:
        """Ensure the directory exists."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def for_dev(cls, schema_name: str = "raw") -> "DatabaseConfig":
        """Create a development configuration."""
        return cls(env="dev", schema_name=schema_name)

    @classmethod
    def for_prod(cls, schema_name: str = "raw") -> "DatabaseConfig":
        """Create a production configuration."""
        return cls(env="prod", schema_name=schema_name)

    @classmethod
    def for_testing(cls, schema_name: str = "test") -> "DatabaseConfig":
        """Create a test configuration (uses dev environment with test schema)."""
        return cls(env="dev", schema_name=schema_name)

    def __str__(self) -> str:
        """String representation showing key config details."""
        return f"DatabaseConfig(env={self.env}, db_path={self.db_path}, schema={self.schema_name})"


def _ensure_schema_exists(conn: duckdb.DuckDBPyConnection, schema_name: str) -> None:
    """Check for existing schema and create if not"""
    try:
        conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
    except Exception as e:
        log(f"Failed to create schema {schema_name}: {str(e)}", "error")


def connect_to_duckdb(
    config: Optional[DatabaseConfig] = None,
) -> duckdb.DuckDBPyConnection:
    """
    Create and return DuckDB connection.

    Args:
        config: Database configuration object

    Returns:
        DuckDB connection object
    """
    if config is None:
        config = DatabaseConfig.for_dev()

    try:
        log(f"Connecting to DuckDB: {config}")
        conn = duckdb.connect(str(config.db_path))  # Convert Path to string

        # Create schema if it doesn't exist
        _ensure_schema_exists(conn, config.schema_name)
        log(f"Ensured schema '{config.schema_name}' exists")

        return conn

    except Exception as e:
        log(f"Failed to connect to DuckDB: {str(e)}", "error")
        raise


def get_table_info(
    conn: duckdb.DuckDBPyConnection, schema_name: str, table_name: str
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
        result = conn.execute(f"SELECT COUNT(*) FROM {full_table_name}").fetchone()
        row_count = result[0] if result else 0

        # Get column information
        columns = conn.execute(f"DESCRIBE {full_table_name}").df()

        return {
            "exists": True,
            "row_count": row_count,
            "columns": columns.to_dict("records"),
        }

    except Exception as e:
        log(f"Error getting table info: {str(e)}", "error")
        return {"exists": False, "row_count": 0, "columns": []}
