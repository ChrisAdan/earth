"""
Earth - Realistic synthetic data generation for testing and development.

A comprehensive toolkit for generating realistic synthetic data including:
- Person profiles with demographics and career progression
- Company data with industry-specific characteristics  
- Marketing campaigns and product information
- Vehicle ownership and automotive data

Supports modular installation for specific use cases.
"""

__version__ = "0.1.0"
__author__ = "Chris Adan"
__description__ = "Realistic synthetic data generation for testing and development"

# Core imports - always available
from .core.utils import *
from .generators.person import generate_person, generate_multiple_persons, PersonProfile
from .generators.career import generate_career_profile, CareerProfile

# Conditional imports for optional modules
def _optional_import(module_path: str, install_extra: str):
    """Helper to conditionally import optional modules."""
    try:
        import importlib
        return importlib.import_module(module_path)
    except ImportError:
        def _missing_module(*args, **kwargs):
            raise ImportError(
                f"This functionality requires the '{install_extra}' extra. "
                f"Install with: pip install earth[{install_extra}]"
            )
        return type('MissingModule', (), {'__getattr__': lambda self, name: _missing_module})()

# Optional module imports
companies = _optional_import('.modules.companies', 'companies')
campaigns = _optional_import('.modules.campaigns', 'campaigns') 
automotive = _optional_import('.modules.automotive', 'automotive')

# Main API exports
__all__ = [
    # Version info
    '__version__',
    '__author__', 
    '__description__',
    
    # Core functionality - always available
    'generate_person',
    'generate_multiple_persons',
    'PersonProfile',
    'generate_career_profile', 
    'CareerProfile',
    
    # Optional modules - available if installed
    'companies',
    'campaigns',
    'automotive',
]

# Module availability checker
def check_module_availability() -> dict:
    """
    Check which optional modules are available.
    
    Returns:
        Dict mapping module names to availability status
    """
    availability = {}
    
    optional_modules = {
        'companies': 'earth.modules.companies',
        'campaigns': 'earth.modules.campaigns', 
        'automotive': 'earth.modules.automotive'
    }
    
    for module_name, module_path in optional_modules.items():
        try:
            import importlib
            importlib.import_module(module_path)
            availability[module_name] = True
        except ImportError:
            availability[module_name] = False
            
    return availability

def get_install_command(module_name: str) -> str:
    """
    Get pip install command for a specific module.
    
    Args:
        module_name: Name of the optional module
        
    Returns:
        Pip install command string
    """
    valid_modules = ['companies', 'campaigns', 'automotive', 'all']
    
    if module_name not in valid_modules:
        raise ValueError(f"Unknown module '{module_name}'. Valid modules: {valid_modules}")
        
    return f"pip install earth[{module_name}]"

# Package metadata for introspection
PACKAGE_INFO = {
    'name': 'earth',
    'version': __version__,
    'description': __description__,
    'author': __author__,
    'modules': {
        'core': ['person', 'career', 'utils'],
        'optional': ['companies', 'campaigns', 'automotive']
    },
    'install_extras': {
        'companies': 'Company and enterprise data generation',
        'campaigns': 'Marketing campaign and product simulation', 
        'automotive': 'Vehicle ownership and automotive data',
        'all': 'All optional modules',
        'dev': 'Development dependencies'
    }
}

def info():
    """Print package information and module availability."""
    print(f"🌍 Earth v{__version__}")
    print(f"   {__description__}")
    print()
    
    availability = check_module_availability()
    
    print("📦 Core Modules (always available):")
    for module in PACKAGE_INFO['modules']['core']:
        print(f"   ✅ {module}")
    print()
    
    print("🔧 Optional Modules:")
    for module in PACKAGE_INFO['modules']['optional']:
        status = "✅ Available" if availability[module] else "❌ Not installed"
        print(f"   {status} {module}")
        if not availability[module]:
            print(f"      Install: {get_install_command(module)}")
    print()
    
    if not all(availability.values()):
        print("💡 Install all modules: pip install earth[all]")


if __name__ == "__main__":
    info()