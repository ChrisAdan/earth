import sys
sys.path.insert(0, 'tests')
from tests import run_test_suite

results = run_test_suite(verbose=False)
print('\\n📊 Test Summary Report:')
print('=' * 40)
[print(f'  {cat.upper()}: {"PASS" if success else "FAIL"}') \
 for cat, success in results.items()]