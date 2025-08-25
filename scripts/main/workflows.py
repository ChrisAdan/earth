import sys

sys.path.insert(0, "app")
from workflows import AVAILABLE_WORKFLOWS

[
    print(f'  • {name}: {info["description"]}')
    for name, info in AVAILABLE_WORKFLOWS.items()
]
