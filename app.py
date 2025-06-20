import json
from reportlab.platypus import SimpleDocTemplate
from layout_lib.renderer import interpret_layout
from layout_lib.table import build_table, build_data_table

def generate_pdf_from_layout(layout, filename="output.pdf"):
    doc = SimpleDocTemplate(filename)
    data_rows = layout.get("data_rows", [])
    layout_tree = {
        "type": layout.get("type", "column"),
        "children": layout.get("children", layout.get("layout", [])),
        "columns": layout.get("columns", 2)
    }
    flowables = interpret_layout(layout_tree, data_rows)
    doc.build(flowables)
    print(f"✅ PDF generated: {filename}")

if __name__ == "__main__":
    with open("layout.json") as f:
        layout = json.load(f)
    with open("data/data.json") as f:
        data = json.load(f)
    layout["data_rows"] = data

    # Load group data from JSON file
    with open("data/group_data2.json") as gf:
        group_data = json.load(gf)

    # Inject group data into all group blocks matching group_name
    for block in layout.get("children", []):
        if block.get("type") == "group":
            group_name = block.get("group_name")
            # For simplicity, inject group_data into all groups; you can refine if needed
            block["data"] = group_data

    # The table will use negative_filter to exclude objects used by groups
    # No need to manually filter data - the table handles it automatically
    print(f"📊 Total objects available: {len(data)}")
    print(f"🔍 Table will automatically exclude objects matching negative_filter")

    generate_pdf_from_layout(layout, "custom_headers_table.pdf")