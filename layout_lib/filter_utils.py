from typing import Any, Dict, List, Union
import operator
from functools import reduce

# Define comparison operators
OPERATORS = {
    "=": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
    "in": lambda x, y: x in y,
    "not_in": lambda x, y: x not in y,
    "contains": lambda x, y: y in x if isinstance(x, str) else False,
    "starts_with": lambda x, y: x.startswith(y) if isinstance(x, str) else False,
    "ends_with": lambda x, y: x.endswith(y) if isinstance(x, str) else False
}

class FilterEvaluator:
    def __init__(self, data: Union[Dict, List]):
        self.data = data if isinstance(data, list) else [data]

    def evaluate_condition(self, item: Dict, condition: Dict) -> bool:
        """Evaluate a single condition against an item."""
        if "or" in condition:
            return any(self.evaluate_condition(item, sub_condition) 
                      for sub_condition in condition["or"])
        
        if "and" in condition:
            return all(self.evaluate_condition(item, sub_condition) 
                      for sub_condition in condition["and"])
        
        if "not" in condition:
            return not self.evaluate_condition(item, condition["not"])

        # Handle comparison operators
        for field, value in condition.items():
            if isinstance(value, dict):
                for op, op_value in value.items():
                    if op in OPERATORS:
                        return OPERATORS[op](item.get(field), op_value)
            else:
                # Default to equality comparison
                return item.get(field) == value

        return False

    def filter(self, filter_condition: Union[str, Dict]) -> List[Dict]:
        """Filter data based on the provided condition."""
        if isinstance(filter_condition, str):
            # Handle legacy format: "field=value"
            field, value = [f.strip() for f in filter_condition.split("=", 1)]
            filter_condition = {field: value}

        return [item for item in self.data 
                if self.evaluate_condition(item, filter_condition)]

def apply_filter(data: Union[Dict, List], filter_condition: Union[str, Dict]) -> Union[Dict, List]:
    """
    Apply a filter condition to the data.
    
    Args:
        data: The data to filter (dict or list)
        filter_condition: The filter condition (string or dict)
    
    Returns:
        Filtered data (dict or list)
    """
    evaluator = FilterEvaluator(data)
    filtered = evaluator.filter(filter_condition)
    
    # Return single item if input was dict, otherwise return list
    return filtered[0] if isinstance(data, dict) else filtered 