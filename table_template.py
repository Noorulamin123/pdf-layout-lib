from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth

def build_table(data, layout):
    max_cols = max(len(row) for row in data)
    for row in data:
        while len(row) < max_cols:
            row.append("")

    # Auto column widths
    font_name = 'Helvetica'
    font_size = 10
    col_widths = [0] * max_cols
    for col_idx in range(max_cols):
        max_width = 0
        for row in data:
            width = stringWidth(str(row[col_idx]), font_name, font_size) + 10
            max_width = max(max_width, width)
        col_widths[col_idx] = max_width

    table = Table(data, colWidths=col_widths)

    header_rows = layout.get("style", {}).get("header_rows", 1)
    style = [
        ('BACKGROUND', (0, 0), (-1, header_rows - 1), getattr(colors, layout["style"].get("header_background", "grey"))),
        ('TEXTCOLOR', (0, 0), (-1, header_rows - 1), getattr(colors, layout["style"].get("header_text_color", "whitesmoke"))),
        ('FONTNAME', (0, 0), (-1, header_rows - 1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, header_rows - 1), 10),
        ('BACKGROUND', (0, header_rows), (-1, -1), getattr(colors, layout["style"].get("body_background", "beige"))),
    ]

    if layout["style"].get("grid", True):
        style.append(('GRID', (0, 0), (-1, -1), 1, colors.black))

    # Add spans for subheaders
    col = 0
    for item in layout["field_map"]:
        if item.get("group"):
            child_count = len(item["children"])
            style.append(('SPAN', (col, 0), (col + child_count - 1, 0)))
            col += child_count
        else:
            style.append(('SPAN', (col, 0), (col, 1)))
            col += 1

    table.setStyle(TableStyle(style))
    return table