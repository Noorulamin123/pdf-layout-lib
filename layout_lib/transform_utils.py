from typing import Any, Callable, Dict, List, Union
import json
from datetime import datetime

def dollarize(value: Union[str, float, int]) -> str:
    """Format number as dollar amount."""
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return str(value)

def volume_millions(value: Union[str, float, int]) -> str:
    """Format volume in millions."""
    try:
        return f"{float(value)/1000000:.2f}M"
    except (ValueError, TypeError):
        return str(value)

def join_pipes(values: Union[str, List[str]]) -> str:
    """Join values with pipe separator."""
    if isinstance(values, list):
        return " | ".join(str(v) for v in values)
    return str(values)

def join_lines(values: Union[str, List[str]]) -> str:
    """Join values with newline separator."""
    if isinstance(values, list):
        return "\n".join(str(v) for v in values)
    return str(values)

# Dictionary of predefined transforms
TRANSFORMS: Dict[str, Callable] = {
    "dollarize": dollarize,
    "volume_millions": volume_millions,
    "join_pipes": join_pipes,
    "join_lines": join_lines
}

def parse_lambda(lambda_str: str) -> Callable:
    """Parse a lambda function string into a callable function."""
    try:
        # Remove 'lambda' keyword and any whitespace
        lambda_body = lambda_str.strip()
        if not lambda_body.startswith('lambda'):
            raise ValueError("Invalid lambda function format")
        
        # Extract the lambda expression
        lambda_expr = lambda_body[6:].strip()  # Remove 'lambda' keyword
        
        # Create the function
        return eval(lambda_expr)
    except Exception as e:
        raise ValueError(f"Invalid lambda function: {e}")

def apply_transforms(field_map: List[Dict], data_rows: List[Dict]) -> List[Dict]:
    """Apply transforms to data rows based on field map."""
    transformed_rows = []
    
    for row in data_rows:
        transformed_row = {}
        for field in field_map:
            if "children" in field:
                # Handle nested fields
                transformed_row[field["label"]] = apply_transforms(field["children"], [row])[0]
            else:
                key = field.get("key", "")
                transform = field.get("transform")
                
                if not key:
                    continue
                
                # Get the value(s)
                if "|" in key:
                    keys = key.split("|")
                    values = [row.get(k.strip(), "") for k in keys]
                else:
                    values = row.get(key, "")
                
                # Apply transform if specified
                if transform:
                    if isinstance(transform, str):
                        # Check if it's a predefined transform
                        if transform in TRANSFORMS:
                            transform_func = TRANSFORMS[transform]
                        else:
                            # Try to parse as lambda
                            transform_func = parse_lambda(transform)
                    else:
                        # Direct function reference
                        transform_func = transform
                    
                    try:
                        transformed_row[field["label"]] = transform_func(values)
                    except Exception as e:
                        print(f"⚠️ Transform error for field '{key}': {e}")
                        transformed_row[field["label"]] = str(values)
                else:
                    # No transform, just join if list
                    if isinstance(values, list):
                        transformed_row[field["label"]] = " ".join(str(v) for v in values)
                    else:
                        transformed_row[field["label"]] = str(values)
        
        transformed_rows.append(transformed_row)
    
    return transformed_rows