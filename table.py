from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
from transform_utils import TRANSFORMS  # Add this import

def parse_field_map(field_map):
    final_keys = []

    def get_depth(items):
        max_depth = 0
        for item in items:
            if item.get("group"):
                max_depth = max(max_depth, 1 + get_depth(item["children"]))
            else:
                max_depth = max(max_depth, 1)
        return max_depth

    depth = get_depth(field_map)
    header_rows = [[] for _ in range(depth)]

    # Track column position globally using mutable list
    def recurse(items, row=0, col_ref=[0]):
        for item in items:
            col = col_ref[0]
            if item.get("group"):
                span = count_leaf_keys(item["children"])
                header_rows[row] += [""] * (col - len(header_rows[row]))
                header_rows[row].append(item["label"])
                for i in range(1, span):
                    header_rows[row].append("")
                recurse(item["children"], row + 1, col_ref)
            else:
                header_rows[row] += [""] * (col - len(header_rows[row]))
                header_rows[row].append(item["label"])
                for r in range(row + 1, depth):
                    header_rows[r] += [""] * (col - len(header_rows[r]))
                    header_rows[r].append("")
                final_keys.append(item["key"])
                col_ref[0] += 1

    def count_leaf_keys(items):
        return sum(count_leaf_keys(i["children"]) if i.get("group") else 1 for i in items)

    recurse(field_map)

    max_len = max(len(r) for r in header_rows)
    for r in header_rows:
        while len(r) < max_len:
            r.append("")

    # debug_header_rows(header_rows)

    return header_rows, final_keys


def debug_header_rows(header_rows):
    print("DEBUG: Header Rows:")
    for i, row in enumerate(header_rows):
        print(f"Row {i}: {row}")

def build_data_table(field_map, data_rows):
    header_rows, final_keys = parse_field_map(field_map)

    transform_map = {}
    def collect_transforms(items):
        for item in items:
            if item.get("group"):
                collect_transforms(item["children"])
            else:
                key = item["key"]
                if "transform" in item:
                    transform_val = item["transform"]
                    if isinstance(transform_val, str):
                        # Try to get from TRANSFORMS, else eval as lambda
                        if transform_val in TRANSFORMS:
                            transform_map[key] = TRANSFORMS[transform_val]
                        else:
                            try:
                                transform_map[key] = eval(transform_val)
                            except Exception as e:
                                print(f"⚠️ Invalid transform for '{key}': {e}")
                    else:
                        try:
                            transform_map[key] = eval(transform_val)
                        except Exception as e:
                            print(f"⚠️ Invalid transform for '{key}': {e}")

    collect_transforms(field_map)

    body_rows = []
    for row in data_rows:
        new_row = []
        for key in final_keys:
            value = row.get(key, "")
            transform = transform_map.get(key)
            if transform:
                try:
                    value = transform(value)
                except Exception as e:
                    print(f"⚠️ Transform error on key '{key}': {e}")
            new_row.append(value)
        body_rows.append(new_row)
    return header_rows + body_rows


def build_table(data, layout):
    max_cols = max(len(row) for row in data)
    for row in data:
        while len(row) < max_cols:
            row.append("")

    font_name = 'Helvetica'
    font_size = 10
    col_widths = [max(stringWidth(str(row[col]), font_name, font_size) for row in data) + 10 for col in range(max_cols)]

    table = Table(data, colWidths=col_widths)

    header_rows_count = len(data) - len(layout["data_rows"])
    max_header_row = header_rows_count - 1

    style = [
        ('BACKGROUND', (0, 0), (-1, max_header_row), getattr(colors, layout["style"].get("header_background", "grey"))),
        ('TEXTCOLOR', (0, 0), (-1, max_header_row), getattr(colors, layout["style"].get("header_text_color", "whitesmoke"))),
        ('FONTNAME', (0, 0), (-1, max_header_row), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, max_header_row), 10),
        ('BACKGROUND', (0, header_rows_count), (-1, -1), getattr(colors, layout["style"].get("body_background", "beige")))
    ]

    if layout["style"].get("grid", True):
        style.append(('GRID', (0, 0), (-1, -1), 1, colors.black))

    def count_leaf_keys(items):
        return sum(count_leaf_keys(i["children"]) if i.get("group") else 1 for i in items)

    def apply_spans(field_map, start_col=0, row=0, max_row=max_header_row):
        col = start_col
        for item in field_map:
            if item.get("group"):
                span = count_leaf_keys(item["children"])
                # Horizontal span across columns in this row
                style.append(('SPAN', (col, row), (col + span - 1, row)))
                # Recurse to next row for children
                apply_spans(item["children"], col, row + 1, max_row)
                col += span
            else:
                # Vertical span from current row down to last header row
                style.append(('SPAN', (col, row), (col, max_row)))
                col += 1
        return col

    apply_spans(layout["field_map"])

    table.setStyle(TableStyle(style))
    return table