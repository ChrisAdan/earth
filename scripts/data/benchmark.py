import sys, time

sys.path.extend(["src", "app"])
from workflows import WorkflowConfig, PeopleWorkflow, CompaniesWorkflow
from earth.core.loader import DatabaseConfig

config = WorkflowConfig(batch_size=100, seed=42)
results = []

for workflow_class, name, count in [
    (CompaniesWorkflow, "Companies", 50),
    (PeopleWorkflow, "People", 500),
]:
    start = time.time()
    workflow = workflow_class(config, DatabaseConfig.for_dev())
    result = workflow.execute(count)
    duration = time.time() - start
    rate = count / duration
    results.append((name, count, duration, rate))
print("⏱️  Workflow Performance:")
[
    print(f"   {name}: {count} records in {duration:.1f}s ({rate:.0f} records/sec)")
    for name, count, duration, rate in results
]
