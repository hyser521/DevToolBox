def example_function(param1: str, param2: int = 10) -> str:
    """
    Example function docstring.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    """
    return f'{param1}_{param2}'

class ExampleClass:
    """Example class for testing."""
    
    def __init__(self, name: str):
        self.name = name
    
    def get_name(self) -> str:
        """Return the name."""
        return self.name