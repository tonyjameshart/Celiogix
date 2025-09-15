# path: services/__init__.py
"""
Lightweight service package init.

Don't re-export submodules here — import them directly:
    from services import themes
    from services import inventory
    from services import shopping
This avoids heavy side effects at import time.
"""

__all__ = []  # Intentionally empty. Submodules are imported explicitly by consumers.
