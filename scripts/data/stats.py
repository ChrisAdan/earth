import sys

sys.path.insert(0, "src")
from earth.core.loader import connect_to_duckdb, operate_on_table, DatabaseConfig

conn = connect_to_duckdb(DatabaseConfig.for_dev())
print("📊 People Table:")
result = operate_on_table(
    conn,
    "raw",
    "persons",
    "read",
    query="SELECT COUNT(*) as total_persons,"
    " MIN(age) as min_age, MAX(age) as max_age, AVG(age) as avg_age"
    " FROM raw.persons",
)
(
    print(result.to_string(index=False))
    if not result.empty
    else print("No person data found")
)
print('"🏢 Companies Table:"')
result = operate_on_table(
    conn,
    "raw",
    "companies",
    "read",
    query="SELECT COUNT(*) as total_companies,"
    " AVG(employee_count) as avg_employees, COUNT(DISTINCT industry) as unique_industries"
    " FROM raw.companies",
)
(
    print(result.to_string(index=False))
    if not result.empty
    else print("No company data found")
)
