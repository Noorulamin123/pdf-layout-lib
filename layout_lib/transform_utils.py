from datetime import datetime

def dollarize(value):
    return f"${value}"


# Define the transforms once at module level
TRANSFORMS = {
    "price": lambda v: f"${v:.2f}" if v is not None else "-",
    "volume_millions": lambda v: f"{v / 1_000_000:.1f}M" if v is not None else "-",
    "format_time_dd": lambda v: datetime.fromtimestamp(v).strftime("%H:%M %d") if v else "-",
    "dash_if_none": lambda v: "-" if v is None else v,
    "dollarize": dollarize,
    "join_lines": lambda values: "\n".join(str(v) for v in values),
    "join_pipes": lambda values: " | ".join(str(v) for v in values)
}


def apply_transforms(field_map, data_rows):
    from layout_lib.table import parse_field_map  # avoid circular import
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
                    transform_func = TRANSFORMS.get(name)
                    if transform_func:
                        transform_map[key] = transform_func
                    else:
                        print(f"⚠️ Invalid transform for '{key}': {name}")

    collect_transforms(field_map)

    transformed_rows = []
    for row in data_rows:
        new_row = {}
        for key in final_keys:
            transform = transform_map.get(key)

            if "|" in key:
                # Composite key (e.g., "Volume1|Volume2|Volume3")
                keys = key.split("|")
                values = [row.get(k, "") for k in keys]

                if transform:
                    try:
                        new_row[key] = transform(values)
                    except Exception as e:
                        print(f"⚠️ Transform error for '{key}': {e}")
                        new_row[key] = "-"
                else:
                    new_row[key] = ", ".join(str(v) for v in values)
            else:
                val = row.get(key, "")
                if transform:
                    try:
                        new_row[key] = transform(val)
                    except Exception as e:
                        print(f"⚠️ Transform error for '{key}': {e}")
                        new_row[key] = "-"
                else:
                    new_row[key] = val

        transformed_rows.append(new_row)
    return transformed_rows