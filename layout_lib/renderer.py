from reportlab.platypus import Spacer, PageBreak, Table as RLTable, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from layout_lib.table import build_table, build_data_table
from layout_lib.transform_utils import apply_transforms, TRANSFORMS
from layout_lib.separator import Separator
from layout_lib.filter_utils import apply_filter

def render_block(block, data_rows, group_context=None):
    if block["type"] == "table":
        print("🔍 Table block found")
        print(f"🔍 Block data: {block.get('data')}")
        print(f"🔍 Data rows: {data_rows}")
        # Use block['data'] if present, else fall back to data_rows
        table_data_rows = block.get("data", data_rows)
        print(f"🔍 Using table data rows: {table_data_rows}")
        
        # Apply negative filter if specified
        negative_filter = block.get("negative_filter")
        if negative_filter and table_data_rows:
            print(f"🔍 Applying negative filters: {negative_filter}")
            try:
                # Handle both single filter and list of filters
                if not isinstance(negative_filter, list):
                    negative_filter = [negative_filter]
                
                # Track all objects to exclude
                excluded_indices = set()
                
                for filter_condition in negative_filter:
                    print(f"🔍 Processing negative filter: {filter_condition}")
                    # Apply filter to find objects that match this condition
                    filtered_data = apply_filter(table_data_rows, filter_condition)
                    
                    # Mark matching objects for exclusion
                    for i, obj in enumerate(table_data_rows):
                        if obj in filtered_data:
                            excluded_indices.add(i)
                            print(f"🔍 Excluding object {i}: {obj.get('RIC', 'N/A')} (matches: {filter_condition})")
                
                # Keep only objects that were NOT excluded by any negative filter
                table_data_rows = [obj for i, obj in enumerate(table_data_rows) if i not in excluded_indices]
                print(f"🔍 After negative filters: {len(table_data_rows)} objects remaining")
            except Exception as e:
                print(f"⚠️ Negative filter error: {e}")
        
        block["data_rows"] = table_data_rows
        field_map = block["field_map"]
        print(f"🔍 Field map: {field_map}")
        transformed_rows = apply_transforms(field_map, table_data_rows)
        print(f"🔍 Transformed rows: {transformed_rows}")
        table_data = build_data_table(field_map, transformed_rows)
        print(f"🔍 Final table data: {table_data}")
        return build_table(table_data, block)

    elif block["type"] == "separator":
        length = block.get("length", 500)
        thickness = block.get("thickness", 1)
        color_name = block.get("color", "black")
        direction = block.get("direction", "horizontal")
        color = getattr(colors, color_name, colors.black)
        margin_before = block.get("margin_before", 10)
        margin_after = block.get("margin_after", 10)
        dash = block.get("dash", None)
        return Separator(length, thickness, color, direction, margin_before, margin_after, dash)

    elif block["type"] == "variable":
        label = block.get("label", "")
        key = block.get("key")
        transform_name = block.get("transform")
        group_name = block.get("group_name")

        value = ""
        if group_name and group_context and group_name in group_context:
            group_data = group_context[group_name]
            if isinstance(group_data, list) and group_data:
                # If group_data is a list, use the first item
                group_data = group_data[0]
            
            if "|" in key:
                keys = key.split("|")
                values = [group_data.get(k.strip(), "") for k in keys]
            else:
                values = group_data.get(key, "")
        else:
            # fallback to first row in data_rows if no group data
            if data_rows and "|" in key:
                keys = key.split("|")
                values = [data_rows[0].get(k.strip(), "") for k in keys]
            elif data_rows:
                values = data_rows[0].get(key, "")
            else:
                values = ""

        # Apply transform if specified
        if transform_name:
            transform = TRANSFORMS.get(transform_name)
            if transform:
                try:
                    value = transform(values)
                except Exception as e:
                    print(f"⚠️ Transform error in variable '{key}': {e}")
            else:
                # fallback if transform not found: just join if list else str
                if isinstance(values, list):
                    value = " ".join(str(v) for v in values)
                else:
                    value = str(values)
        else:
            # no transform, if list join by space
            if isinstance(values, list):
                value = " ".join(str(v) for v in values)
            else:
                value = str(values)

        style = getSampleStyleSheet()["BodyText"]
        return Paragraph(f"{label}: {value}", style)

    elif block["type"] == "group":
        # group holds data only; no rendering output
        return None

    return None


def interpret_layout(layout, data_rows, group_context=None):
    if group_context is None:
        group_context = {}

    flowables = []
    layout_type = layout.get("type", "column")
    children = layout.get("children", [])
    columns = layout.get("columns", 2)

    if not group_context:
        for block in children:
            if block.get("type") == "group":
                group_name = block.get("group_name")
                raw_data = block.get("data", {})
                filter_condition = block.get("filter")

                if isinstance(raw_data, list):
                    if not filter_condition:
                        raise ValueError(f"Group '{group_name}' is a list but missing 'filter' field.")

                    try:
                        filtered_data = apply_filter(raw_data, filter_condition)
                        if filtered_data:
                            group_context[group_name] = filtered_data
                        else:
                            print(f"⚠️ No match found in group '{group_name}' for filter: {filter_condition}")
                            group_context[group_name] = {}
                    except Exception as e:
                        print(f"⚠️ Filter error in group '{group_name}': {e}")
                        group_context[group_name] = {}
                elif isinstance(raw_data, dict):
                    group_context[group_name] = raw_data
                else:
                    print(f"⚠️ Unsupported group data format in group '{group_name}'")

    if layout_type == "column":
        for block in children:
            if block.get("type") == "group":
                continue  # skip rendering group blocks
            if "children" in block:
                # nested container, recurse
                flowables.extend(interpret_layout(block, data_rows, group_context))
            else:
                rendered = render_block(block, data_rows, group_context)
                if rendered:
                    flowables.append(rendered)

    elif layout_type == "row":
        row_items = []
        for block in children:
            if block.get("type") == "group":
                continue
            if "children" in block:
                # For nested containers inside row, render them and append as flowables
                nested = interpret_layout(block, data_rows, group_context)
                row_items.extend(nested)
            else:
                rendered = render_block(block, data_rows, group_context)
                if rendered:
                    row_items.append(rendered)
        if row_items:
            flowables.append(RLTable([row_items], hAlign='LEFT'))

    elif layout_type == "grid":
        # If no data rows, just layout the blocks in a grid
        if not data_rows:
            grid_rows = []
            row = []
            for i, block in enumerate(children):
                if block.get("type") == "group":
                    continue
                if "children" in block:
                    nested = interpret_layout(block, data_rows, group_context)
                    row.extend(nested)
                else:
                    rendered = render_block(block, data_rows, group_context)
                    row.append(rendered)
                if (i + 1) % columns == 0:
                    grid_rows.append(row)
                    row = []
            if row:
                grid_rows.append(row)
            flowables.append(RLTable(grid_rows, hAlign='LEFT'))
        else:
            # Create a grid from data rows
            grid_rows = []
            for data_row in data_rows:
                row = []
                for block in children:
                    if block.get("type") == "group":
                        continue
                    if "children" in block:
                        # For nested blocks, create a sub-grid
                        nested = interpret_layout(block, [data_row], group_context)
                        row.extend(nested)
                    else:
                        # For single blocks, render with current data row
                        rendered = render_block(block, [data_row], group_context)
                        if rendered:
                            row.append(rendered)
                if row:
                    grid_rows.append(row)
            if grid_rows:
                flowables.append(RLTable(grid_rows, hAlign='LEFT'))

    else:
        print(f"⚠️ Unsupported layout type '{layout_type}'. Supported types are: column, row, grid")
        return []

    return flowables