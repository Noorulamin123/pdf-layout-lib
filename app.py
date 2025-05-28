import json
from reportlab.platypus import SimpleDocTemplate

from table_utils import build_table, build_data_table

def interpret_dsl(layout, filename="output.pdf"):
    doc = SimpleDocTemplate(filename)

    field_map = layout["field_map"]
    data_rows = layout["data_rows"]

    table_data = build_data_table(field_map, data_rows)

    # Make sure layout has data_rows key
    layout["data_rows"] = data_rows

    table = build_table(table_data, layout)
    doc.build([table])
    print(f"✅ PDF generated: {filename}")

if __name__ == "__main__":
    with open("layout.json") as f:
        layout = json.load(f)
    with open("data.json") as f:
        data = json.load(f)
    layout["data_rows"] = data
    interpret_dsl(layout, "custom_headers_table.pdf")