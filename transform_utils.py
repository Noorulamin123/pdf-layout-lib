from datetime import datetime

def dollarize(value):
    return f"${value}"


# Define the transforms once at module level
TRANSFORMS = {
    "price": lambda v: f"${v:.2f}" if v is not None else "-",
    "volume_millions": lambda v: f"{v / 1_000_000:.1f}M" if v is not None else "-",
    "format_time_dd": lambda v: datetime.fromtimestamp(v).strftime("%H:%M %d") if v else "-",
    "dash_if_none": lambda v: "-" if v is None else v,
    "dollarize": dollarize
}

def apply_transforms(field_map, data_rows):
    from table import parse_field_map  # avoid circular import
    _, final_keys = parse_field_map(field_map)
    transform_map = {}

    def collect_transforms(items):
        for item in items:
            if item.get("group"):
                collect_transforms(item["children"])
            else:
                key = item["key"]
                name = item.get("transform")
                if name:
                    transform_map[key] = TRANSFORMS.get(name)

    collect_transforms(field_map)

    transformed_rows = []
    for row in data_rows:
        new_row = {}
        for key in final_keys:
            val = row.get(key, "")
            transform = transform_map.get(key)
            new_row[key] = transform(val) if transform else val
        transformed_rows.append(new_row)
    return transformed_rows