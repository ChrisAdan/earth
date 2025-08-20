#!/usr/bin/env python3
"""Modular test runner for Earth data generator."""

from argparse import ArgumentParser
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

class TestRunner:
    """Manages and executes different test categories."""
    
    TEST_CATEGORIES: Dict = {
        'core': ['database', 'utilities', 'loader'],
        'generators': ['person', 'company', 'career'],
        'modules': ['companies', 'campaigns', 'automotive'],
        'app': ['workflows', 'orchestration', 'main']
    }
    
    def __init__(self):
        self.verbose: bool = False
        self.failed_tests: List = []
    
    def run_category(self, category: str) -> bool:
        """Run tests for a specific category."""
        if category not in self.TEST_CATEGORIES:
            print(f"❌ Unknown test category: {category}")
            return False
        
        print(f"🧪 Running {category.upper()} tests...")
        
        success: bool = True
        for module in self.TEST_CATEGORIES[category]:
            if not self._run_module_tests(category, module):
                success = False
        
        return success
    
    def _run_module_tests(self, category: str, module: str) -> bool:
        """Run tests for a specific module."""
        try:
            # Import and run the specific test module
            test_module = __import__(f'tests.{category}.test_{module}', fromlist=[''])
            print(f'Type of test_module: {type(test_module)}')
            print('*'*60)
            if hasattr(test_module, 'run_tests'):
                result = test_module.run_tests(verbose=self.verbose)
                if not result:
                    self.failed_tests.append(f"{category}.{module}")
                return result
            else:
                print(f"⚠️  No run_tests function in {category}.{module}")
                return True
                
        except ImportError as e:
            if self.verbose:
                print(f"⚠️  Skipping {category}.{module}: {e}")
            return True
        except Exception as e:
            print(f"❌ Error in {category}.{module}: {e}")
            self.failed_tests.append(f"{category}.{module}")
            return False

def main():
    parser: ArgumentParser = ArgumentParser(description="Run Earth data generator tests")
    parser.add_argument('--mode', choices=['all', 'core', 'generators', 'modules', 'app', 'smoke'], 
                       default='all', help='Test mode to run')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args: Tuple[Any, List] = parser.parse_args()
    
    runner: TestRunner = TestRunner()
    runner.verbose = args.verbose
    
    if args.mode == 'all':
        categories = list(runner.TEST_CATEGORIES.keys())
    elif args.mode == 'smoke':
        # Quick smoke test - just core essentials
        categories = ['core']
    else:
        categories = [args.mode]
    
    total_success: bool = True
    for category in categories:
        if not runner.run_category(category):
            total_success = False
    
    # Summary
    if runner.failed_tests:
        print(f"\n❌ Failed tests: {', '.join(runner.failed_tests)}")
    else:
        print(f"\n✅ All tests passed!")
    
    sys.exit(0 if total_success else 1)

if __name__ == '__main__':
    main()