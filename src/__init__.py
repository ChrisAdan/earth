"""
Earth: Synthetic data generation platform for analytics engineering.
"""

__author__ = "Chris Adan"

from earth.core.loader import connect_to_duckdb, operate_on_table, log
from earth.generators.person import generate_person, PersonProfile

__all__ = [
    "connect_to_duckdb",
    "operate_on_table",
    "log",
    "generate_person",
    "PersonProfile",
]
