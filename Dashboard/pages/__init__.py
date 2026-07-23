# Automatically import all modules in the pages folder

import importlib
import pkgutil

# Dynamically import all .py files except __init__.py
__all__ = []

for loader, module_name, is_pkg in pkgutil.iter_modules(__path__):
    if module_name != "__init__":
        module = importlib.import_module(f"{__name__}.{module_name}")
        globals()[module_name] = module
        __all__.append(module_name)
