from reportlab.platypus import Spacer, PageBreak, Table as RLTable
from reportlab.lib import colors
from table import build_table, build_data_table
from transform_utils import apply_transforms
from separator import Separator

def render_block(block, data_rows):
    if block["type"] == "table":
        block["data_rows"] = data_rows
        field_map = block["field_map"]
        table_data = build_data_table(field_map, data_rows)
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
    return None

def interpret_layout(layout, data_rows):
    flowables = []
    layout_type = layout.get("type", "column")
    children = layout.get("children", [])
    columns = layout.get("columns", 2)

    if layout_type == "column":
        for block in children:
            repeat = block.get("repeat", 1)
            sep = block.get("repeat_separator")
            for i in range(repeat):
                rendered = render_block(block, data_rows)
                if rendered:
                    flowables.append(rendered)
                if sep and i < repeat - 1:
                    if sep == "spacer":
                        flowables.append(Spacer(1, 20))
                    elif sep == "pagebreak":
                        flowables.append(PageBreak())

    elif layout_type == "row":
        row_items = []
        for block in children:
            rendered = render_block(block, data_rows)
            if rendered:
                row_items.append(rendered)
        if row_items:
            flowables.append(RLTable([row_items], hAlign='LEFT'))

    elif layout_type == "grid":
        grid_rows = []
        row = []
        for i, block in enumerate(children):
            rendered = render_block(block, data_rows)
            row.append(rendered)
            if (i + 1) % columns == 0:
                grid_rows.append(row)
                row = []
        if row:
            grid_rows.append(row)
        flowables.append(RLTable(grid_rows, hAlign='LEFT'))

    else:
        print(f"⚠️ Unsupported layout type '{layout_type}'")

    return flowables