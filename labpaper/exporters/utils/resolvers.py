from traitlets.config.loader import LazyConfigValue

def resolve_boolean(value, default=None):
    """Resolve a boolean value."""
    if isinstance(value, LazyConfigValue):
         # LazyConfigValue requires special handling; merge into a temporary value
        placeholder = None  # Default placeholder value for resolution
        value = value.merge_into(placeholder)
        # Allow string resolution to proceed if needed

    if isinstance(value, str):
        # Handle string representations of booleans
        return value.lower() in ['true', '1', 'yes']
    
    # Converted value should not be None, supply default or else allow False
    if default is not None and value is None:
        return default
    
    # Final conversion with bool()
    return bool(value)

def resolve_string(value, default=None):
    """Resolve a string value."""
    if isinstance(value, LazyConfigValue):
        value = value.merge_into(None)
    return str(value) if value is not None else default
