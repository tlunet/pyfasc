from adapters.registry import get_registry

def detect_language(filename):
    registry = get_registry()
    return registry.detect_language(filename) or 'unknown'
