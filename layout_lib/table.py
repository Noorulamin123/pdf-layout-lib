from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.styles import getSampleStyleSheet
from layout_lib.transform_utils import TRANSFORMS, parse_lambda

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

    def recurse(items, row=0, col_ref=[0]):
        for item in items:
            col = col_ref[0]
            if item.get("group"):
                span = count_leaf_keys(item["children"])
                header_rows[row] += [""] * (col - len(header_rows[row]))
                header_rows[row].append(item["label"])
                for _ in range(1, span):
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

    return header_rows, final_keys

def build_data_table(field_map, data_rows):
    header_rows, final_keys = parse_field_map(field_map)

    transform_map = {}
    def collect_transforms(items):
        for item in items:
            if item.get("group"):
                collect_transforms(item["children"])
            else:
                if "transform" in item:
                    transform = item["transform"]
                    if isinstance(transform, str):
                        if transform in TRANSFORMS:
                            transform_map[item["key"]] = TRANSFORMS[transform]
                        else:
                            try:
                                transform_map[item["key"]] = parse_lambda(transform)
                            except Exception:
                                transform_map[item["key"]] = None
                    elif callable(transform):
                        transform_map[item["key"]] = transform
                    else:
                        transform_map[item["key"]] = None

    collect_transforms(field_map)

    body_rows = []
    style = getSampleStyleSheet()["BodyText"]

    def flatten_row(row, field_map):
        flat = {}
        for field in field_map:
            if field.get("group"):
                # Recursively flatten children
                child_flat = flatten_row(row.get(field["label"], {}), field["children"])
                flat.update(child_flat)
            else:
                key = field.get("key")
                flat[key] = row.get(field["label"], "")
        return flat

    for row in data_rows:
        new_row = []
        flat_row = flatten_row(row, field_map)
        for key in final_keys:
            value = flat_row.get(key, "")
            transform = transform_map.get(key)
            if transform:
                try:
                    value = transform(value)
                except Exception as e:
                    print(f"⚠️ Transform error on key '{key}': {e}")
            if isinstance(value, str) and "\n" in value:
                value = Paragraph(value.replace("\n", "<br/>"), style)
            new_row.append(value)
        body_rows.append(new_row)

    return header_rows + body_rows

def build_table(data, layout):
    max_cols = max(len(row) for row in data)
    for row in data:
        while len(row) < max_cols:
            row.append("")

    style_config = layout.get("style", {})
    font_name = style_config.get("font_name", "Helvetica")
    font_size = style_config.get("font_size", 10)
    body_font_size = style_config.get("body_font_size", font_size)
    font_style = style_config.get("font_style", "").lower()

    font_name_map = {
        ("helvetica", ""): "Helvetica",
        ("helvetica", "bold"): "Helvetica-Bold",
        ("helvetica", "italic"): "Helvetica-Oblique",
        ("helvetica", "bold-italic"): "Helvetica-BoldOblique",
        ("times-roman", ""): "Times-Roman",
        ("times-roman", "bold"): "Times-Bold",
        ("times-roman", "italic"): "Times-Italic",
        ("times-roman", "bold-italic"): "Times-BoldItalic",
        ("courier", ""): "Courier",
        ("courier", "bold"): "Courier-Bold",
        ("courier", "italic"): "Courier-Oblique",
        ("courier", "bold-italic"): "Courier-BoldOblique"
    }
    font_key = (font_name.lower(), font_style)
    resolved_font_name = font_name_map.get(font_key, font_name)

    col_widths = style_config.get("col_widths")
    if not col_widths:
        col_widths = []
        for col in range(max_cols):
            max_width = 0
            for row in data:
                cell = row[col]
                text = cell.getPlainText() if hasattr(cell, 'getPlainText') else str(cell)
                max_width = max(max_width, stringWidth(text, font_name, font_size))
            col_widths.append(max_width + 10)

    table = Table(data, colWidths=col_widths)

    header_rows_count = len(data) - len(layout["data_rows"])
    max_header_row = header_rows_count - 1

    style = [
        ('BACKGROUND', (0, 0), (-1, max_header_row), getattr(colors, style_config.get("header_background", "grey"))),
        ('TEXTCOLOR', (0, 0), (-1, max_header_row), getattr(colors, style_config.get("header_text_color", "whitesmoke"))),
        ('FONTNAME', (0, 0), (-1, max_header_row), resolved_font_name),
        ('FONTSIZE', (0, 0), (-1, max_header_row), font_size),
        ('FONTSIZE', (0, header_rows_count), (-1, -1), body_font_size),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, max_header_row), 10),
        ('BACKGROUND', (0, header_rows_count), (-1, -1), getattr(colors, style_config.get("body_background", "beige")))
    ]

    if style_config.get("grid", True):
        style.append(('GRID', (0, 0), (-1, -1), 1, colors.black))

    def count_leaf_keys(items):
        return sum(count_leaf_keys(i["children"]) if i.get("group") else 1 for i in items)

    def apply_spans(field_map, start_col=0, row=0, max_row=max_header_row):
        col = start_col
        for item in field_map:
            if item.get("group"):
                span = count_leaf_keys(item["children"])
                style.append(('SPAN', (col, row), (col + span - 1, row)))
                apply_spans(item["children"], col, row + 1, max_row)
                col += span
            else:
                style.append(('SPAN', (col, row), (col, max_row)))
                col += 1
        return col

    apply_spans(layout["field_map"])
    table.setStyle(TableStyle(style))
    return table